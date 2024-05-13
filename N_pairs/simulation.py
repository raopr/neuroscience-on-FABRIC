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

from network import NPairs
from parameters import Parameters

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
    assert (pc.nhost() == 1) or (pc.nhost() == 2)

    neuron_r = h.Random()
    neuron_r.MCellRan4(parameters.random_state)
    
    # Assign senders to process 0 and receivers to process 1
    distributed_gids = [[i for i in range(0, parameters.N_pairs * 2)[::2]], [i for i in range(1, parameters.N_pairs * 2)[::2]]]

    net = NPairs(parameters)

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

        # Collect data on the first 50 cells to check the spike raster
        raster_data_sender = []
        raster_data_receiver = []

        # Collect firing rates to plot a histogram
        fr_sender = []
        fr_receiver = []

        for key, value in data.items():
            if key % 2 == 0: # sender
                if len(raster_data_sender) <= 50:
                    raster_data_sender.append(np.array(value).astype(int)[:4])
                fr_sender.append(len(value) / parameters.tstop)
            else:
                if len(raster_data_receiver) <= 50:
                    raster_data_receiver.append(np.array(value).astype(int)[:4])
                fr_receiver.append(len(value) / parameters.tstop)

        # Plot the raster and the histogram
        fig, ax = plt.subplots(1, 2, figsize = (10, 5))
        for idx, spike_times in enumerate(raster_data_sender):
            ax[0].scatter(spike_times, [idx + 50] * len(spike_times), marker = "v", color = 'red')
        for idx, spike_times in enumerate(raster_data_receiver):
            ax[0].scatter(spike_times, [idx] * len(spike_times), marker = ".", color = 'blue')

        ax[1].hist(fr_sender, alpha = 0.7, label = "sender")
        ax[1].hist(fr_receiver, alpha = 0.7, label = "receiver")
        ax[1].legend()
        fig.savefig("raster.png")

        # Report the numbers of spikes
        print(f"Num sender spikes: {int(np.sum(fr_sender) * parameters.tstop)}, mean FR: {np.round(np.mean(fr_sender), 2)}")
        print(f"Num receiver spikes: {int(np.sum(fr_receiver) * parameters.tstop)}, mean FR: {np.round(np.mean(fr_receiver), 2)}")

    # ----------

    pc.barrier()
    pc.done()
    h.quit()
