from neuron import h
import numpy as np
import pandas as pd

from cells import WBInhCell, RTMExcCell
from parameters import Parameters

h.nrnmpi_init()
pc = h.ParallelContext()

class PINGAN:

    def __init__(self, parameters: Parameters) -> None:
        self.parameters = parameters
        self.random_state = np.random.RandomState(self.parameters.random_state + pc.id())

        self.gids_on_node = []
        self.cells_on_node = []

        self.ASSEMBLIES = [] # [[A1 gids], [A2 gids], ..., [AN gids]], the same on all nodes
        self.ALL_EXC_GIDS = [] # for convenience, the same on all nodes
        self.ALL_INH_GIDS = [] # for convenience, the same on all nodes
        self._init_assembly_gids()

    def _init_assembly_gids(self) -> None:
        # GIDs are distributed across assemblies and exc/inh in order, i.e.,
        # A1 = [[0, 1, 2, ..., N_E], [N_E + 1, N_E + 2, ..., N_E + N_I]]
        # A2 = [[N_E + N_I + 1, ...], [...]], etc.
        all_gids = np.arange(self.parameters.N_assemblies * (self.parameters.N_E + self.parameters.N_I))
        for assembly_gids in np.split(all_gids, self.parameters.N_assemblies):
            self.ASSEMBLIES.append((
                assembly_gids[:self.parameters.N_E].tolist(), 
                assembly_gids[self.parameters.N_E:].tolist()))
            self.ALL_EXC_GIDS.extend(assembly_gids[:self.parameters.N_E].tolist())
            self.ALL_INH_GIDS.extend(assembly_gids[self.parameters.N_E:].tolist())

    def set_gids(self, distributed_gids: list) -> None:
        self.gids_on_node = distributed_gids[pc.id()]
        for gid in self.gids_on_node:
            pc.set_gid2node(gid, pc.id())

    def init_cells(self) -> None:

        for lid, gid in enumerate(self.gids_on_node):
            if gid in self.ALL_EXC_GIDS:
                cell = RTMExcCell(gid = gid, lid = lid)
                cell.IClamp.amp = self.parameters.I_E
            else:
                cell = WBInhCell(gid = gid, lid = lid)
                cell.IClamp.amp = self.parameters.I_I
            
            cell.IClamp.dur = self.parameters.IClamp_dur
            cell.IClamp.delay = self.parameters.IClamp_delay

            self.cells_on_node.append(cell)
        
        # Do separately as an additional check
        for cell in self.cells_on_node:
            pc.cell(cell.gid, cell.spike_detector)

    def generate_connectivity(self) -> None:
        # Connect within assemblies
        for assembly in self.ASSEMBLIES:
            self._connect_within_PING(assembly_gids = assembly)

        # Connect between assemblies (only EE and EI)

        # If there is only one assembly, don't add additional connections
        if self.parameters.N_assemblies == 1:
            return
        
        for assembly in self.ASSEMBLIES:
            self._connect_between_PINGs(assembly_gids = assembly)

    def connect_cells(self, graph_file) -> None:
        graph = pd.read_csv(graph_file, header = None)
        graph.columns = ["source_gid", "target_gid", "weight", "conn_type"]
        print(graph.head())
        for i in range(len(graph)):
            if graph.loc[i, "target_gid"] not in self.gids_on_node: continue
            self._create_synapse_and_connect(graph.loc[i, "source_gid"], graph.loc[i, "target_gid"], graph.loc[i, "conn_type"], graph.loc[i, "weight"])

    def _connect_between_PINGs(self, assembly_gids: list) -> None:

        n_connected_cells_E = 0
        n_connected_cells_I = 0

        # ... – E
        for target_gid in assembly_gids[0]:
            # Create only N_between% of connections
            # Divide by N_assemblies_on_node to account for the number of nodes
            if n_connected_cells_E >= int(self.parameters.N_between * self.parameters.N_E):
                break

            # Choose a random exc cell in a different assembly
            source_gid = int(self.random_state.choice(self.ALL_EXC_GIDS, 1))
            while source_gid in assembly_gids[0]:
                source_gid = int(self.random_state.choice(self.ALL_EXC_GIDS, 1))

            self._add_connection(source_gid, target_gid, "EE")
            n_connected_cells_E += 1
        
        # ... – I
        for target_gid in assembly_gids[1]:
            # Create only N_between% of connections
            if n_connected_cells_I >= int(self.parameters.N_between * self.parameters.N_I):
                break

            # Choose a random exc cell in a different assembly
            source_gid = int(self.random_state.choice(self.ALL_EXC_GIDS, 1))
            while source_gid in assembly_gids[0]:
                source_gid = int(self.random_state.choice(self.ALL_EXC_GIDS, 1))

            self._add_connection(source_gid, target_gid, "EI")
            n_connected_cells_I += 1


    def _connect_within_PING(self, assembly_gids: list) -> None:
        # ... - E
        for target_gid in assembly_gids[0]:
            for source_gid in assembly_gids[0]: # E - E
                # Do not connect to self
                if source_gid == target_gid: continue
                self._add_connection(source_gid, target_gid, "EE")

            for source_gid in assembly_gids[1]: # I – E
                # Do not connect to self
                if source_gid == target_gid: continue
                self._add_connection(source_gid, target_gid, "IE")
        
        # ... – I
        for target_gid in assembly_gids[1]:
            for source_gid in assembly_gids[0]: # E - I
                # Do not connect to self
                if source_gid == target_gid: continue
                self._add_connection(source_gid, target_gid, "EI")

            for source_gid in assembly_gids[1]: # I – I
                # Do not connect to self
                if source_gid == target_gid: continue
                self._add_connection(source_gid, target_gid, "II")

    def _add_connection(self, source_gid: int, target_gid: int, conn_type: str) -> None:

        # Generate weight
        if conn_type == "EE":
            weight = self._compute_gbar(self.parameters.g_EE, self.parameters.p_EE, self.parameters.N_E)
        elif conn_type == "EI":
            weight = self._compute_gbar(self.parameters.g_EI, self.parameters.p_EI, self.parameters.N_E)
        elif conn_type == "IE":
            weight = self._compute_gbar(self.parameters.g_IE, self.parameters.p_IE, self.parameters.N_I)
        elif conn_type == "II":
            weight = self._compute_gbar(self.parameters.g_II, self.parameters.p_II, self.parameters.N_I)

        # Don't add a 0-weight synapse
        if weight == 0: return

        with open(self.parameters.graph_file, "a") as file:
            file.write(f"{source_gid},{target_gid},{weight},{conn_type}\n")
                

    def _create_synapse_and_connect(self, source_gid: int, target_gid: int, conn_type: str, weight: float) -> float:
        # Create a new synapse on target with respect to source
        syn = h.Exp2Syn(self.cells_on_node[self.gids_on_node.index(target_gid)].soma(0.5))

        if conn_type[0] == "E":
            syn.e = self.parameters.rev_E
            syn.tau1 = self.parameters.tau1_E
            syn.tau2 = self.parameters.tau2_E
        else:
            syn.e = self.parameters.rev_I
            syn.tau1 = self.parameters.tau1_I
            syn.tau2 = self.parameters.tau2_I


        self.cells_on_node[self.gids_on_node.index(target_gid)].synapses.append(syn)

        # Connect the source to the target
        nc = pc.gid_connect(
            source_gid,
            self.cells_on_node[self.gids_on_node.index(target_gid)].synapses[-1]
            )

        nc.weight[0] = weight
        nc.threshold = -15

        self.cells_on_node[self.gids_on_node.index(target_gid)].netcons.append(nc)

        return weight

    def _compute_gbar(self, g_hat: float, p: float, N: int) -> float:
        Z = self.random_state.binomial(n = 1, p = p)
        return g_hat * Z / (p * N + 1e-15)
