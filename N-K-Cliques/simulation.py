import os

# Set GPUs
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank % 2 == 0:
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
else:
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"


from neuron import h
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

from network import NCliques
from parameters import Parameters

from neuron import coreneuron
coreneuron.enable = True

cvode = h.CVode()
mode = cvode.cache_efficient(True)

## To set GPUs, change the following lines
coreneuron.gpu = True
##

if __name__ == "__main__":

    pc = h.ParallelContext()
    parameters = Parameters()
    assert (pc.nhost() == 1) or (pc.nhost() == 2)
    assert parameters.N_cliques % 2 == 0

    neuron_r = h.Random()
    neuron_r.MCellRan4(parameters.random_state)

    # Distribute cells randomly
    # random_state = np.random.RandomState(parameters.random_state)
    # all_gids = np.arange(parameters.N_cliques * parameters.cells_per_clique)
    # random_state.shuffle(all_gids)
    # distributed_gids = [[i for i in all_gids[::2]], [i for i in all_gids[1::2]]]
    
    # Half of cliques is on one process, the other half is on the other one
    N_cells = parameters.N_cliques * parameters.cells_per_clique
    distributed_gids = [
        [i for i in range(N_cells)[:int(parameters.N_cliques // 2) * parameters.cells_per_clique]], 
        [i for i in range(N_cells)[int(parameters.N_cliques // 2) * parameters.cells_per_clique:]]]

    net = NCliques(parameters)

    net.set_gids(distributed_gids)
    pc.barrier()

    net.init_cells()
    pc.barrier()

    net.connect_cells()
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
        # Combine the data from the various processes
        data = {}
        for process_data in all_data: data.update(process_data)

        # Collect data on the first 4 cliques to check the spike raster
        raster_data = []

        # Collect firing rates to plot a histogram
        fr = []

        for key, value in data.items():
            if len(raster_data) <= 4 * parameters.cells_per_clique:
                    raster_data.append(np.array(value).astype(int)[:4])
                    fr.append(len(value) / parameters.tstop)

        # Plot the raster and the histogram
        fig, ax = plt.subplots(1, 2, figsize = (10, 5))
        for idx, spike_times in enumerate(raster_data):
            ax[0].scatter(spike_times, [idx] * len(spike_times), marker = "v", color = 'red')

        ax[1].hist(fr, alpha = 0.7)
        fig.savefig("raster.png")

        # Report the numbers of spikes
        print(f"Num spikes: {int(np.sum(fr) * parameters.tstop)}, mean FR: {np.round(np.mean(fr), 2)}")

    # ----------

    pc.barrier()
    pc.done()
    h.quit()
