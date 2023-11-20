import numpy as np
import pandas as pd
from neuron import h
from parameters import Parameters

h.nrnmpi_init()
pc = h.ParallelContext()

class AssemblyNetwork:

    def __init__(self, parameters: Parameters):
        self.parameters = parameters
        self.random_state = np.random.RandomState(self.parameters.random_state)
        self.assemblies = []
        self._create_assemblies()
        self._init_current_injections()

    def distribute_by_assembly(self) -> None:
        # Do round-robin counting on assemblies
        assembly_ids = list(range(pc.id(), len(self.assemblies), pc.nhost()))
        for idx in assembly_ids:
            for cell in self.assemblies[idx].cells:
                pc.set_gid2node(cell.gid, pc.id())
                pc.cell(cell.gid, cell.spike_detector)

    def distribute_round_robin(self) -> None:
        cell_ids = list(range(pc.id(), (self.parameters.N_assemblies * self.parameters.N_cells_per_assembly), pc.nhost()))
        for assembly in self.assemblies:
            for cell in assembly.cells:
                if cell.gid in cell_ids:
                    pc.set_gid2node(cell.gid, pc.id())
                    pc.cell(cell.gid, cell.spike_detector)

    def distribute_by_gid(self, gids: list) -> None:
        for assembly in self.assemblies:
            for cell in assembly.cells:
                if cell.gid in gids:
                    pc.set_gid2node(cell.gid, pc.id())
                    pc.cell(cell.gid, cell.spike_detector)

    def connect_cells(self) -> None:

        exc_within_assembly_conns = []
        inh_within_assembly_conns = []

        # Connect cells within assemblies
        for assembly in self.assemblies:
            exc_matrix, inh_matrix = assembly.generate_connectivity(self.random_state)
            self._connect_within_assembly(assembly, exc_matrix, "exc")
            self._connect_within_assembly(assembly, inh_matrix, "inh")

            exc_within_assembly_conns.append(exc_matrix)
            inh_within_assembly_conns.append(inh_matrix)

        # Connect cells between assemblies
        exc_inter_assembly_conns = []
        inh_inter_assembly_conns = []

        all_inds = list(range(self.parameters.N_assemblies))
        for source_assembly_ind in range(len(self.assemblies)):
            target_assembly_inds = self.random_state.choice(
                all_inds[:source_assembly_ind] + all_inds[source_assembly_ind + 1:], 
                size = 20, 
                replace = True)
            for target_assemly_ind in target_assembly_inds[:10]:
                exc_inter_assembly_conns.append(self._connect_between_assemblies(
                    source_assembly_ind, 
                    target_assemly_ind, 
                    "exc", 
                    self.random_state))
            for target_assemly_ind in target_assembly_inds[10:]:
                inh_inter_assembly_conns.append(self._connect_between_assemblies(
                    source_assembly_ind, 
                    target_assemly_ind, 
                    "inh", 
                    self.random_state))
        
        return exc_within_assembly_conns, inh_within_assembly_conns, exc_inter_assembly_conns, inh_inter_assembly_conns

    def summarize_connectivity(
            self,
            exc_within_assembly_conns, 
            inh_within_assembly_conns, 
            exc_inter_assembly_conns, 
            inh_inter_assembly_conns) -> None:

        within_matrices = []
        index_names = []
        for ind, assembly in enumerate(self.assemblies):
            within_matrices.append(assembly.summarize_connectivity(exc_within_assembly_conns[ind], "exc").flatten())
            within_matrices.append(assembly.summarize_connectivity(inh_within_assembly_conns[ind], "inh").flatten())
            index_names.append(f"{ind}-exc")
            index_names.append(f"{ind}-inh")
        
        within_df = pd.DataFrame(data = within_matrices, index = index_names)
        within_df.to_csv("within.csv")
        
        N_cells = int(self.parameters.N_assemblies * self.parameters.N_cells_per_assembly)
        exc_inter_matrix = np.zeros((N_cells, N_cells))
        inh_inter_matrix = np.zeros((N_cells, N_cells))
        for conn in exc_inter_assembly_conns:
            exc_inter_matrix[conn[0], conn[1]] = 1
        for conn in inh_inter_assembly_conns:
            inh_inter_matrix[conn[0], conn[1]] = 1

        between_matrices = [exc_inter_matrix.flatten(), inh_inter_matrix.flatten()]
        between_df = pd.DataFrame(data = between_matrices, index = ["exc", "inh"])
        between_df.to_csv("between.csv")
    
    def _init_current_injections(self) -> None:
        for assembly in self.assemblies:
            for cell in assembly.cells:
                cell.set_ci(
                    amp = self.parameters.CI_amp, 
                    dur = self.parameters.CI_dur, 
                    delay = self.parameters.CI_delay)

    def _create_assemblies(self) -> None:
        for i in range(self.parameters.N_assemblies):
            self.assemblies.append(CellAssembly(
                N_cells = self.parameters.N_cells_per_assembly,
                gid_shift = i * self.parameters.N_cells_per_assembly,
                exc_syn_connectivity = self.parameters.exc_syn_connectivity,
                inh_syn_connectivity = self.parameters.inh_syn_connectivity,
            ))
                
    def _connect_between_assemblies(self, source_assembly_ind, target_assemly_ind, syn_type, random_state) -> tuple:
        # Choose a random cell within the source assembly and add a synapse to it
        source_cell_ind = random_state.choice(range(len(self.assemblies[source_assembly_ind].cells)), size = 1)[0]
        if syn_type == "exc":
            syn = h.Exp2Syn(self.assemblies[source_assembly_ind].cells[source_cell_ind].soma(0.5))
            syn.e = 0
            self.assemblies[source_assembly_ind].cells[source_cell_ind].exc_synapses.append(syn)
        elif syn_type == "inh":
            syn = h.Exp2Syn(self.assemblies[source_assembly_ind].cells[source_cell_ind].soma(0.5))
            syn.e = -75
            self.assemblies[source_assembly_ind].cells[source_cell_ind].inh_synapses.append(syn)
        else:
            raise ValueError
        
        # Choose a random cell within the target assembly and connect to it
        target_cell_ind = random_state.choice(range(len(self.assemblies[target_assemly_ind].cells)), size = 1)[0]
        if syn_type == "exc":
            nc = pc.gid_connect(
                self.assemblies[target_assemly_ind].cells[target_cell_ind].gid,
                self.assemblies[source_assembly_ind].cells[source_cell_ind].exc_synapses[-1]
                )
            nc.weight[0] = self.parameters.exc_syn_weight
            nc.delay = self.parameters.exc_syn_delay
            nc.threshold = self.parameters.exc_syn_threshold
        elif syn_type == "inh":
            nc = pc.gid_connect(
                self.assemblies[target_assemly_ind].cells[target_cell_ind].gid,
                self.assemblies[source_assembly_ind].cells[source_cell_ind].inh_synapses[-1]
                )
            nc.weight[0] = self.parameters.inh_syn_weight
            nc.delay = self.parameters.inh_syn_delay
            nc.threshold = self.parameters.inh_syn_threshold
        self.assemblies[source_assembly_ind].cells[source_cell_ind].netcons.append(nc)

        # Save gids
        return (
            self.assemblies[source_assembly_ind].cells[source_cell_ind].gid, 
            self.assemblies[target_assemly_ind].cells[target_cell_ind].gid
            )

    
    def _connect_within_assembly(self, assembly, connectivity_matrix: np.ndarray, syn_type: str) -> None:
        for syn_ind in range(connectivity_matrix.shape[0]):
            for cell_loc_ind in range(connectivity_matrix.shape[1]):
                if connectivity_matrix[syn_ind, cell_loc_ind] == 0:
                    continue
                if syn_type == "exc":
                    nc = pc.gid_connect(
                        assembly.cells[cell_loc_ind].gid, 
                        assembly.cells[int(syn_ind // assembly.N_exc_syn)].exc_synapses[int(syn_ind % assembly.N_exc_syn)])
                    nc.weight[0] = self.parameters.exc_syn_weight
                    nc.delay = self.parameters.exc_syn_delay
                    nc.threshold = self.parameters.exc_syn_threshold
                    assembly.cells[int(syn_ind // assembly.N_exc_syn)].netcons.append(nc)
                elif syn_type == "inh":
                    nc = pc.gid_connect(
                        assembly.cells[cell_loc_ind].gid, 
                        assembly.cells[int(syn_ind // assembly.N_inh_syn)].inh_synapses[int(syn_ind % assembly.N_inh_syn)])
                    nc.weight[0] = self.parameters.inh_syn_weight
                    nc.delay = self.parameters.inh_syn_delay
                    nc.threshold = self.parameters.inh_syn_threshold
                    assembly.cells[int(syn_ind // assembly.N_exc_syn)].netcons.append(nc)
                else:
                    raise ValueError

class CellAssembly:

    def __init__(
            self, 
            N_cells: int,
            gid_shift: int, 
            exc_syn_connectivity: float, 
            inh_syn_connectivity: float,
            ):
        
        self.N_cells = N_cells
        self.gid_shift = gid_shift
        self.N_exc_syn = int(N_cells * exc_syn_connectivity)
        self.N_inh_syn = int(N_cells * inh_syn_connectivity)

        self.cells = []
        self._create_cells_and_synapses()

    def generate_connectivity(self, random_state: np.random.RandomState) -> tuple:
        exc_matrix = self._create_connectivity_matrix("exc", random_state)
        inh_matrix = self._create_connectivity_matrix("inh", random_state)
        return exc_matrix, inh_matrix
    
    def summarize_connectivity(self, connectivity_matrix: np.ndarray, syn_type: str):
        if syn_type == "exc":
            win_size = self.N_exc_syn
        elif syn_type == "inh":
            win_size = self.N_inh_syn
        else:
            raise ValueError
        return connectivity_matrix.reshape(-1, win_size, connectivity_matrix.shape[-1]).sum(axis = 1)
    
    def _create_connectivity_matrix(
            self, 
            syn_type: str, 
            random_state: np.random.RandomState
            ) -> np.ndarray:
        for cell_idx, cell in enumerate(self.cells):
            if syn_type == "exc":
                matrix = np.zeros((self.N_cells * self.N_exc_syn, self.N_cells))
                syn_list = cell.exc_synapses
                n_syn = self.N_exc_syn
            elif syn_type == "inh":
                matrix = np.zeros((self.N_cells * self.N_inh_syn, self.N_cells))
                syn_list = cell.inh_synapses
                n_syn = self.N_inh_syn
            else:
                raise ValueError

            for syn_idx in range(len(syn_list)):
                # Choose a random cell to connect to
                target_cell = random_state.choice(self.cells, size = 1)[0]
                while target_cell.gid == cell.gid:
                    target_cell = random_state.choice(self.cells, size = 1)[0]
                matrix[int(cell_idx * n_syn + syn_idx), target_cell.loc_id] = 1
        return matrix
                
    def _create_cells_and_synapses(self) -> None:
        for i in range(self.N_cells):
            cell = Cell(gid = i + self.gid_shift, loc_id = i)

            for _ in range(self.N_exc_syn):
                cell.exc_synapses.append(h.Exp2Syn(cell.soma(0.5)))

            for _ in range(self.N_inh_syn):
                cell.inh_synapses.append(h.Exp2Syn(cell.soma(0.5)))

            for syn in cell.exc_synapses: 
                syn.e = 0
            for syn in cell.inh_synapses: 
                syn.e = -75
            
            self.cells.append(cell)


class Cell:

    def __init__(self, gid: int, loc_id: int):

        self.gid = gid
        self.loc_id = loc_id

        # Create sections
        self.soma = h.Section(name = 'soma')
        self.dend = h.Section(name = 'dend')

        # Topology
        self.dend.connect(self.soma) # child -> parent

        # Geometry & biophysics
        self.soma.L = 15 # (um)
        self.soma.diam = 15 # (um)
        self.soma.Ra = 150 * 22.5 # (ohm-cm)

        self.dend.L = 150 # (um)
        self.dend.diam = 10 # (um)
        self.dend.Ra = 150 # (ohm-cm)

        self.soma.nseg = self.dend.nseg = 1
        self.soma.cm = self.dend.cm = 1 # (uF/cm2)

        # Channels 
        self.soma.insert('hh')
        self.soma(0.5).hh.el = -70 # (mV)
        self.soma(0.5).hh.gl = 0.00005 # (S/cm2)
        self.soma(0.5).hh.gnabar = 0.035 # (S/cm2)
        self.soma(0.5).hh.gkbar = 0.008 # (S/cm2)

        self.dend.insert('pas')
        self.dend(0.5).pas.e = -70 # (mV)
        self.dend(0.5).pas.g = 0.00005 # (S/cm2)

        # Connectivity
        self.exc_synapses = []
        self.inh_synapses = []
        self.netcons = []
        
        # --- Recorders

        # Spikes
        self.spike_detector = h.NetCon(self.soma(0.5)._ref_v, None, sec = self.soma)
        self.spike_times = h.Vector()
        self.spike_detector.record(self.spike_times)

        # Soma voltage
        self.V = h.Vector().record(self.soma(0.5)._ref_v)

        # Current
        self.ci = h.IClamp(self.soma(0.5))
        self.ci_vec = h.Vector().record(self.ci._ref_i)
        
    def set_ci(self, amp: float, dur = None, delay = None) -> None:
        self.ci.amp = amp
        if dur is not None: self.ci.dur = dur
        if delay is not None: self.ci.delay = delay