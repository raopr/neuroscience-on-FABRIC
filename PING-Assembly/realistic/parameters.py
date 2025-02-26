from dataclasses import dataclass

@dataclass
class Parameters:

    random_state: int = 123

    # Distribution
    strategy = "random"
    # strategy = "assembly"

    # Build
    # ----------
    N_assemblies: int = 4
    N_cell_per_assembly: int = 1250
    # ----------

    N_E: int = int(N_cell_per_assembly / 1.25) # number of excitatory cells per PING
    N_I: int = N_E // 4 # number of inhibitory cells per PING

    # Drives
    I_E = 1.4; sigma_E = 0.05; I_I = 0; sigma_I = 0.05
    # Synpatic conductances
    g_EE = 0; g_EI = 0.25; g_IE = 0.25; g_II = 0.25
    # Synaptic probabilities
    p_EE = 0; p_EI = 0.5; p_IE = 0.5; p_II = 0.5
    # Synaptic dynamics
    tau1_E = 0.5; tau2_E = 3; rev_E = 0
    tau1_I = 0.5; tau2_I = 9; rev_I = -75

    # Simulation
    tstop: float = 4000 # (ms)
    dt: float = 0.1
    v_init: float = -75 # (mV)

    # Current injection
    IClamp_delay: float = 200 # (ms)
    IClamp_dur: float = tstop - IClamp_delay # (ms)

    # Connectivity between assemblies
    N_between: float = 0.1

    # File to save the graph
    graph_file = "graph.txt"

