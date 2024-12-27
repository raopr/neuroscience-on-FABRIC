from dataclasses import dataclass

@dataclass
class Parameters:

    random_state: int = 123

    # Build
    # ----------
    N_pairs: int = 1250
    # ----------

    # Simulation
    tstop: float = 4000 # (ms)
    dt: float = 0.1
    v_init: float = -75 # (mV)

    # Current injection
    IClamp_amp: float = 10 # (nA)
    IClamp_delay: float = 200 # (ms)
    IClamp_dur: float = tstop - IClamp_delay # (ms)

    # File to save the graph
    graph_file = "graph.txt"

