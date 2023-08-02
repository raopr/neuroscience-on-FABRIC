from neuron import h
from network import WTANetwork
import matplotlib.pyplot as plt

num_cell = 500
amps = [0.1] + [0.05] * (num_cell - 1)
plot = True

if __name__ == "__main__":

    net = WTANetwork(num_cell = num_cell, amps = amps)
    pc = h.ParallelContext()

    # Set simulation parameters
    dt = 0.025 # (ms)
    tstop = 700 # (ms)
    v_init = -75 # (mV)

    pc.set_maxstep(1 / dt)

    # Time recorder
    t_vec = h.Vector().record(h._ref_t)

    # Run the simulation
    h.finitialize(v_init)
    pc.psolve(tstop)

    local_data = {cell.gid: list(cell.V.as_numpy()) for cell in net.cells}
    all_data = pc.py_alltoall([local_data] + [None] * (pc.nhost() - 1))

    if pc.id() == 0:
        # combine the data from the various processes
        data = {}
        for process_data in all_data:
            data.update(process_data)

        if plot:
            fig, ax = plt.subplots(1, min([num_cell, 5]), figsize = (20, 4), sharey = True)
            for i in range(min([num_cell, 5])):
                ax[i].plot(t_vec, data[i])
                ax[i].set_xlabel("t (ms)")
                ax[i].set_title(f"Cell {i}: I = {amps[i]} nA")
                ax[i].grid()

            ax[0].set_ylabel("V (mV)")
            plt.show()

    pc.barrier()
    pc.done()
    h.quit()