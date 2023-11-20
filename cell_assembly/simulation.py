from neuron import h
import pandas as pd
from network import AssemblyNetwork
from parameters import Parameters

if __name__ == "__main__":

    parameters = Parameters()

    net = AssemblyNetwork(parameters)
    net.distribute_by_assembly()
    conns = net.connect_cells()
    net.summarize_connectivity(*conns)

    pc = h.ParallelContext()
    pc.set_maxstep(1 / parameters.dt)

    # Run the simulation
    h.finitialize(parameters.v_init)
    pc.psolve(parameters.tstop)

    local_data = {}
    for assembly in net.assemblies:
        for cell in assembly.cells:
            local_data[cell.gid] = list(cell.V.as_numpy())
    all_data = pc.py_alltoall([local_data] + [None] * (pc.nhost() - 1))

    if pc.id() == 0:
        # combine the data from the various processes
        data = {}
        for process_data in all_data:
            data.update(process_data)
        
        df = pd.DataFrame(data)
        df.to_csv("v.csv")

    pc.barrier()
    pc.done()
    h.quit()
