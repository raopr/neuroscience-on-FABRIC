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
        self.gids_on_node = []
        self.cells_on_node = []

        self.assemblies = []
        self._create_assemblies()

    def _create_assemblies(self) -> None:
        all_gids = list(range((self.parameters.N_assemblies * self.parameters.N_cells_per_assembly)))
        for i in range(self.parameters.N_assemblies):
            self.assemblies.append(CellAssembly(
                N_cells = self.parameters.N_cells_per_assembly,
                gids = all_gids[self.parameters.N_cells_per_assembly * i : self.parameters.N_cells_per_assembly * (i + 1)],
                exc_syn_connectivity = self.parameters.exc_syn_connectivity,
                inh_syn_connectivity = self.parameters.inh_syn_connectivity,
            ))

    def set_gids(self, distributed_gids: list) -> None:
        self.gids_on_node = distributed_gids[pc.id()].tolist()
        for gid in self.gids_on_node:
            pc.set_gid2node(gid, pc.id())

    def create_cells(self):
        N_exc_syn = int(self.parameters.N_cells_per_assembly * self.parameters.exc_syn_connectivity)
        N_inh_syn = int(self.parameters.N_cells_per_assembly * self.parameters.inh_syn_connectivity)

        for lid, gid in enumerate(self.gids_on_node):
            cell = Cell(gid = gid, lid = lid)

            for _ in range(N_exc_syn):
                cell.exc_synapses.append(h.Exp2Syn(cell.soma(0.5)))

            for _ in range(N_inh_syn):
                cell.inh_synapses.append(h.Exp2Syn(cell.soma(0.5)))

            for syn in cell.exc_synapses: 
                syn.e = 0
            for syn in cell.inh_synapses: 
                syn.e = -75

            cell.set_ci(
                amp = self.parameters.CI_amp, 
                dur = self.parameters.CI_dur, 
                delay = self.parameters.CI_delay)
            
            self.cells_on_node.append(cell)
        
        for cell in self.cells_on_node:
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

        pc.barrier()

        # Connect cells between assemblies
        exc_inter_assembly_conns = []
        inh_inter_assembly_conns = []

        # Choose random target cells on the current node and add
        target_cell_gids = self.random_state.choice(self.gids_on_node, self.parameters.n_between * 2, True)
        for target_cell_gid in target_cell_gids[:10]:
            exc_inter_assembly_conns.append(self._connect_between_assemblies(
                    target_cell_gid,
                    "exc", 
                    self.random_state))
        for target_cell_gid in target_cell_gids[10:]:
            inh_inter_assembly_conns.append(self._connect_between_assemblies(
                    target_cell_gid,
                    "inh", 
                    self.random_state))
        
        pc.barrier()
        
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
                
    def _connect_between_assemblies(self, target_cell_gid, syn_type, random_state) -> tuple:
        random_assembly_index = int(self.random_state.choice(range(self.parameters.N_assemblies), 1))
        while target_cell_gid in self.assemblies[random_assembly_index].gids:
            random_assembly_index = int(self.random_state.choice(range(self.parameters.N_assemblies), 1))
        
        # Choose a random cell within the source assembly
        source_gid = int(np.random.choice(self.assemblies[random_assembly_index].gids, 1))

        # Add either a synapse to the target cell
        if syn_type == "exc":
            syn = h.Exp2Syn(self.cells_on_node[self.gids_on_node.index(target_cell_gid)].soma(0.5))
            syn.e = 0
            self.cells_on_node[self.gids_on_node.index(target_cell_gid)].exc_synapses.append(syn)

            # Connect the cells
            nc = pc.gid_connect(
                source_gid,
                self.cells_on_node[self.gids_on_node.index(target_cell_gid)].exc_synapses[-1]
                )
            nc.weight[0] = self.parameters.exc_syn_weight
            nc.delay = self.parameters.exc_syn_delay
            nc.threshold = self.parameters.exc_syn_threshold

        elif syn_type == "inh":
            syn = h.Exp2Syn(self.cells_on_node[self.gids_on_node.index(target_cell_gid)].soma(0.5))
            syn.e = -75
            self.cells_on_node[self.gids_on_node.index(target_cell_gid)].inh_synapses.append(syn)

            # Connect the cells
            nc = pc.gid_connect(
                source_gid,
                self.cells_on_node[self.gids_on_node.index(target_cell_gid)].inh_synapses[-1]
                )
            nc.weight[0] = self.parameters.inh_syn_weight
            nc.delay = self.parameters.inh_syn_delay
            nc.threshold = self.parameters.inh_syn_threshold
        

        self.cells_on_node[self.gids_on_node.index(target_cell_gid)].netcons.append(nc)
      
        # Save gids
        return (source_gid, target_cell_gid)

    
    def _connect_within_assembly(self, assembly, connectivity_matrix: np.ndarray, syn_type: str) -> None:
        for target_syn_ind in range(connectivity_matrix.shape[0]):
            for source_lid in range(connectivity_matrix.shape[1]):
                if connectivity_matrix[target_syn_ind, source_lid] == 0:
                    continue
                if syn_type == "exc":
                    target_lid = target_syn_ind // assembly.N_exc_syn
                    target_gid = assembly.gids[target_lid]
                    if target_gid not in self.gids_on_node: continue

                    nc = pc.gid_connect(
                        assembly.gids[source_lid],
                        self.cells_on_node[self.gids_on_node.index(target_gid)].exc_synapses[int(target_syn_ind % assembly.N_exc_syn)]
                    )

                    nc.weight[0] = self.parameters.exc_syn_weight
                    nc.delay = self.parameters.exc_syn_delay
                    nc.threshold = self.parameters.exc_syn_threshold
                    self.cells_on_node[self.gids_on_node.index(target_gid)].netcons.append(nc)

                elif syn_type == "inh":
                    target_lid = target_syn_ind // assembly.N_inh_syn
                    target_gid = assembly.gids[target_lid]
                    if target_gid not in self.gids_on_node: continue

                    nc = pc.gid_connect(
                        assembly.gids[source_lid],
                        self.cells_on_node[self.gids_on_node.index(target_gid)].inh_synapses[int(target_syn_ind % assembly.N_inh_syn)]
                    )
                    nc.weight[0] = self.parameters.inh_syn_weight
                    nc.delay = self.parameters.inh_syn_delay
                    nc.threshold = self.parameters.inh_syn_threshold
                    self.cells_on_node[self.gids_on_node.index(target_gid)].netcons.append(nc)
                else:
                    raise ValueError

class CellAssembly:

    def __init__(
            self, 
            N_cells: int,
            gids: int, 
            exc_syn_connectivity: float, 
            inh_syn_connectivity: float,
            ):
        
        self.N_cells = N_cells
        self.gids = gids
        self.N_exc_syn = int(N_cells * exc_syn_connectivity)
        self.N_inh_syn = int(N_cells * inh_syn_connectivity)

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
        
        for source_cell_lid, source_cell_gid in enumerate(self.gids):
            if syn_type == "exc":
                matrix = np.zeros((self.N_cells * self.N_exc_syn, self.N_cells))
                n_syn = self.N_exc_syn
            elif syn_type == "inh":
                matrix = np.zeros((self.N_cells * self.N_inh_syn, self.N_cells))
                n_syn = self.N_inh_syn
            else:
                raise ValueError

            for syn_idx in range(n_syn):
                # Choose a random cell to connect to
                target_cell_gid = random_state.choice(self.gids, size = 1)[0]
                while target_cell_gid == source_cell_gid:
                    target_cell_gid = random_state.choice(self.gids, size = 1)[0]
                matrix[int(source_cell_lid * n_syn + syn_idx), self.gids.index(target_cell_gid)] = 1
        return matrix


class Cell:

    def __init__(self, gid: int, lid: int):

        self.gid = gid
        self.lid = lid

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
