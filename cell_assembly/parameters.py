from dataclasses import dataclass

@dataclass
class Parameters:
    random_state: int = 123

    # Build
    N_assemblies: int = 1
    N_cells_per_assembly: int = 5
    
    # Current injection
    CI_amp: float = 6 # (nA)
    CI_dur: float = 700 # (ms)
    CI_delay: float = 200 # (ms)

    # Simulation
    tstop: float = 1000 # (ms)
    dt: float = 0.1
    v_init: float = -75 # (mV)
    
    # Connectivity within assemblies
    exc_syn_connectivity: float = 0.8
    exc_syn_weight: float = 4
    exc_syn_delay: float = 2
    exc_syn_threshold: float = 1

    inh_syn_connectivity: float = 0.2
    inh_syn_weight: float = 1
    inh_syn_delay: float = 2
    inh_syn_threshold: float = 1

    # Connectivity between assemblies
    n_between: int = 1

