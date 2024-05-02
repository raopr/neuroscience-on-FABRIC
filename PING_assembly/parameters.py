from dataclasses import dataclass

@dataclass
class Parameters:

    random_state: int = 123

    # Distribution
    strategy = "random" # "assembly"

    # Build
    N_assemblies: int = 1
    N_E: int = 200 # number of excitatory cells per PING
    N_I: int = N_E // 4 # number of inhibitory cells per PING

    # Drives (we use constant I)
    I_E = 1.4; sigma_E = 0.05; I_I = 0; sigma_I = 0.05
    # Synpatic conductances
    g_EE = 0; g_EI = 0.25; g_IE = 0.25; g_II = 0.25
    # Synaptic probabilities
    p_EE = 0; p_EI = 0.5; p_IE = 0.5; p_II = 0.5
    # Synaptic dynamics
    tau1_E = 0.5; tau2_E = 3; rev_E = 0
    tau1_I = 0.5; tau2_I = 9; rev_I = -75

    # Simulation
    tstop: float = 400 # (ms)
    dt: float = 0.1
    v_init: float = -75 # (mV)

    # Current injection
    IClamp_delay: float = 200 # (ms)
    IClamp_dur: float = tstop - IClamp_delay # (ms)

    # Connectivity between assemblies
    N_between: int = int(N_assemblies * (N_E + N_I) * 0.01)

    # File to save the graph
    graph_file = "graph.txt"

