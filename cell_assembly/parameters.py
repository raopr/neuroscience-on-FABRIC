from dataclasses import dataclass

@dataclass
class Parameters:
    random_state: int = 123

    # Build
    N_assemblies: int = 4
    N_cells_per_assembly: int = 5
    
    # Current injection
    CI_amp: float = 0.1 # (nA)
    CI_dur: float = 500 # (ms)
    CI_delay: float = 20 # (ms)

    # Simulation
    tstop: float = 700 # (ms)
    dt: float = 0.1
    v_init: float = -75 # (mV)
    
    # Connectivity
    exc_syn_connectivity: float = 0.5
    exc_syn_weight: float = 9
    exc_syn_delay: float = 2
    exc_syn_threshold: float = 1

    inh_syn_connectivity: float = 0.5
    inh_syn_weight: float = 9
    inh_syn_delay: float = 2
    inh_syn_threshold: float = 1

