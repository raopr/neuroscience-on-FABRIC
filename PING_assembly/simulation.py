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
import plotext as plt
import numpy as np

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

    net.connect_cells()
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

        # Plot the spike raster
        num_processed = 0
        for key, value in data.items():
            if num_processed == 400: break
            
            if key in net.ALL_EXC_GIDS:
                marker = 'dot'
            else:
                marker = 'dollar'
            plt.scatter(np.array(value).astype(int), [key] * len(value), marker = marker)
            num_processed += 1
        plt.show()
    # ----------

    pc.barrier()
    pc.done()
    h.quit()
