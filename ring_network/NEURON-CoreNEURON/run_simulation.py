# Source:
# https://neuron.yale.edu/neuron/docs/ball-and-stick-model-part-4

import os

# Set GPUs
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
print(rank)

if rank == 0:
    os.environ["CUDA_VISIBLE_DEVICES"]="0"
else:
    os.environ["CUDA_VISIBLE_DEVICES"]="1"


from neuron import h
from neuron.units import ms, mV
import matplotlib.pyplot as plt
from network import Ring

cvode = h.CVode()
mode = cvode.cache_efficient(True)

### To set CoreNEURON, change the following lines
from neuron import coreneuron
coreneuron.enable = True
coreneuron.gpu = False
###

if __name__ == "__main__":
    ring = Ring(N = 4000)
    
    pc = h.ParallelContext()
    ### Uncomment if running on CPU
    pc.nthread(20)
    ###
    pc.set_maxstep(10 * ms)

    t = h.Vector().record(h._ref_t)
    h.finitialize(-65 * mV)
    h.stdinit()
    pc.psolve(6000 * ms)

    # send all spike time data to node 0
    local_data = {cell._gid: list(cell.spike_times) for cell in ring.cells}
    all_data = pc.py_alltoall([local_data] + [None] * (pc.nhost() - 1))

    if pc.id() == 0:
        # combine the data from the various processes
        data = {}
        for process_data in all_data:
            data.update(process_data)
        # plot it
        plt.figure()
        for i, spike_times in data.items():
            plt.vlines(spike_times, i + 0.5, i + 1.5)
        plt.savefig("out.png")
    
    pc.barrier()
    pc.done()
    
    from datetime import datetime
    print(datetime.now())

    h.quit()

