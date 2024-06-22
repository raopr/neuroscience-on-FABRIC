import os

# Set GPUs
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank % 2 == 0:
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
else:
    os.environ["CUDA_VISIBLE_DEVICES"] = "1"


from neuron import h
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

from network import PINGAN
from parameters import Parameters
from distribution import distribute_randomly, distribute_by_assembly

from neuron import coreneuron
coreneuron.enable = True

cvode = h.CVode()
mode = cvode.cache_efficient(True)

### To set GPUs, change the following lines
coreneuron.gpu = True
###

if __name__ == "__main__":

    pc = h.ParallelContext()
    parameters = Parameters()
    assert parameters.N_assemblies == pc.nhost()

    neuron_r = h.Random()
    neuron_r.MCellRan4(parameters.random_state)

    if parameters.strategy == "random":
        distributed_gids = distribute_randomly(parameters, pc)
    elif parameters.strategy == "assembly":
        distributed_gids = distribute_by_assembly(parameters, pc)
    else:
        raise ValueError

    net = PINGAN(parameters)

    net.set_gids(distributed_gids)
    pc.barrier()

    net.init_cells()
    pc.barrier()

    net.connect_cells("graph.txt")
    pc.barrier()

    # Report cells on the node for a sanity check
    print(f"The first 10 cells on node {pc.id()}: {[cell.gid for cell in net.cells_on_node[:10]]}")
    print(f"The first 10 gids on node {pc.id()}: {net.gids_on_node[:10]}")
    pc.barrier()

    pc.set_maxstep(1 / parameters.dt)

    # Run the simulation
    print(f"[{datetime.now()}]: Starting simulation on process {pc.id()}", flush = True)
    h.finitialize(parameters.v_init)
    pc.psolve(parameters.tstop)
    print(f"[{datetime.now()}]: Finished simulation on process {pc.id()}", flush = True)

    # ----------
    local_data = {}
    for cell in net.cells_on_node:
        local_data[cell.gid] = list(cell.spike_times.as_numpy())

    all_data = pc.py_alltoall([local_data] + [None] * (pc.nhost() - 1))

    if pc.id() == 0:
        print(f"Strategy: {parameters.strategy}")
        # Combine the data from the various processes
        data = {}
        for process_data in all_data: data.update(process_data)

        # Collect data on at most 50+50 random cells to check the spike raster
        raster_data_exc = []
        raster_data_inh = []

        # Collect firing rates to plot a histogram
        fr_exc = []
        fr_inh = []

        for key, value in data.items():
            if key in net.ALL_EXC_GIDS:
                if (np.random.RandomState(parameters.random_state).uniform() > 0.5) and (len(raster_data_exc) <= 50):
                    raster_data_exc.append(np.array(value).astype(int)[:4])
                fr_exc.append(len(value) / parameters.tstop)
            else:
                if (np.random.RandomState(parameters.random_state).uniform() > 0.5) and (len(raster_data_inh) <= 50):
                    raster_data_inh.append(np.array(value).astype(int)[:4])
                fr_inh.append(len(value) / parameters.tstop)

        # Plot the raster and the histogram
        fig, ax = plt.subplots(1, 2, figsize = (10, 5))
        for idx, spike_times in enumerate(raster_data_exc):
            ax[0].scatter(spike_times, [idx + 50] * len(spike_times), marker = "v", color = 'red')
        for idx, spike_times in enumerate(raster_data_inh):
            ax[0].scatter(spike_times, [idx] * len(spike_times), marker = ".", color = 'blue')

        ax[1].hist(fr_exc, alpha = 0.7, label = "exc")
        ax[1].hist(fr_inh, alpha = 0.7, label = "inh")
        ax[1].legend()
        fig.savefig("raster.png")

        # Report the numbers of spikes
        print(f"Num exc. spikes: {int(np.sum(fr_exc) * parameters.tstop)}, mean FR: {np.round(np.mean(fr_exc), 2)}")
        print(f"Num inh. spikes: {int(np.sum(fr_inh) * parameters.tstop)}, mean FR: {np.round(np.mean(fr_inh), 2)}")

        # Report oscillation frequency
        random_cell = np.random.RandomState(parameters.random_state).choice(list(data.keys()), 1)
        spike_times = np.array(data[int(random_cell[0])]).astype(int)
        ISI = np.diff(spike_times)
        print(f"The network is oscillating around {1000 / np.mean(ISI)} Hz.")
    # ----------

    pc.barrier()
    pc.done()
    h.quit()
