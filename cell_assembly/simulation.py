import dis
from neuron import h
import pandas as pd
from network import AssemblyNetwork
from parameters import Parameters
from datetime import datetime
import numpy as np

#from neuron import coreneuron
#coreneuron.enable = True

#cvode = h.CVode()
#mode = cvode.cache_efficient(True)

### To set GPUs, change the following lines
# coreneuron.gpu = True
###

def distribute_randomly(parameters, pc):
    random_state = np.random.RandomState(parameters.random_state)
    all_gids = list(range((parameters.N_assemblies * parameters.N_cells_per_assembly)))
    distributed_gids = []
    for _ in range(pc.nhost()):
        distributed_gids.append(random_state.choice(a = all_gids, size = parameters.N_cells_per_assembly, replace = False))
        for gid in distributed_gids[-1]:
            all_gids.remove(gid)
    return distributed_gids

def distribute_by_assembly(parameters, pc):
    all_gids = list(range((parameters.N_assemblies * parameters.N_cells_per_assembly)))
    distributed_gids = []
    for i in range(pc.nhost()):
        distributed_gids.append(all_gids[parameters.N_cells_per_assembly * i : parameters.N_cells_per_assembly * (i + 1)])
    return distributed_gids

def distribute_round_robin(parameters, pc):
    all_gids = list(range((parameters.N_assemblies * parameters.N_cells_per_assembly)))
    distributed_gids = []
    for i in range(pc.nhost()):
        distributed_gids.append(all_gids[i, len(all_gids), pc.nhost()])
    return distributed_gids

if __name__ == "__main__":

    pc = h.ParallelContext()
    parameters = Parameters()
    assert parameters.N_assemblies == pc.nhost()

    distributed_gids = distribute_randomly(parameters, pc)
    # distributed_gids = distribute_round_robin(parameters, pc)
    # distributed_gids = distribute_by_assembly(parameters, pc)

    net = AssemblyNetwork(parameters)
    net.set_gids(distributed_gids)
    pc.barrier()
    net.create_cells()
    pc.barrier()
    conns = net.connect_cells()
    pc.barrier()
    net.summarize_connectivity(*conns)
    pc.barrier()

    pc.set_maxstep(1 / parameters.dt)

    # Run the simulation
    print(f"[{datetime.now()}]: Starting simulation on process {pc.id()}", flush = True)
    h.finitialize(parameters.v_init)
    pc.psolve(parameters.tstop)
    
    print(f"[{datetime.now()}]: Finished simulation on process {pc.id()}", flush = True)
    local_data = {}
    for cell in net.cells_on_node:
        local_data[cell.gid] = list(cell.V.as_numpy())
    
    df = pd.DataFrame(local_data)
    df.to_csv(f"{pc.id()}_v.csv")

    # From the Neuron's tutorial, but doesn't work on FABRIC
    # ----------
    all_data = pc.py_alltoall([local_data] + [None] * (pc.nhost() - 1))

    if pc.id() == 0:
       # Combine the data from the various processes
       data = {}
       for process_data in all_data:
           data.update(process_data)
       
       df = pd.DataFrame(data)
       df.to_csv("v.csv")

    # ----------

    pc.barrier()
    pc.done()
    h.quit()
