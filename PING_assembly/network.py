from neuron import h
import numpy as np

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

    def connect_cells(self) -> None:
        # Connect within assemblies
        for assembly in self.ASSEMBLIES:
            self._connect_within_PING(assembly_gids = assembly)

        # Connect between assemblies (only EE and EI)

        # If there is only one assembly, don't add additional connections
        if self.parameters.N_assemblies == 1:
            return
        
        # Choose random target cells on the node
        target_gids = self.random_state.choice(self.gids_on_node, self.parameters.N_between, True).tolist()
        for target_gid in target_gids:
            # Find a different assembly to connect to
            random_assembly_index = int(self.random_state.choice(range(self.parameters.N_assemblies), 1))

            while (target_gid in self.ASSEMBLIES[random_assembly_index][0]) or (target_gid in self.ASSEMBLIES[random_assembly_index][1]):
                random_assembly_index = int(self.random_state.choice(range(self.parameters.N_assemblies), 1))
            
            # Choose a random exc cell within the source assembly
            source_gid = int(self.random_state.choice(self.ASSEMBLIES[random_assembly_index][0], 1))
            if target_gid in self.ALL_EXC_GIDS:
                self._create_synapse_and_connect(source_gid, target_gid, "EE")
            else:
                self._create_synapse_and_connect(source_gid, target_gid, "EI")


    def _connect_within_PING(self, assembly_gids: list) -> None:
        # ... - E
        for target_gid in assembly_gids[0]:
            # Do not connect if not on the current node
            if target_gid not in self.gids_on_node: continue

            # Target GID is always on the current node;
            # Source GID might be anywhere

            for source_gid in assembly_gids[0]: # E - E
                # Do not connect to self
                if source_gid == target_gid: continue
                self._create_synapse_and_connect(source_gid, target_gid, "EE")

            for source_gid in assembly_gids[1]: # I – E
                # Do not connect to self
                if source_gid == target_gid: continue
                self._create_synapse_and_connect(source_gid, target_gid, "IE")
        
        # ... – I
        for target_gid in assembly_gids[1]:
            # Do not connect if not on the current node
            if target_gid not in self.gids_on_node: continue

            # Target GID is always on the current node;
            # Source GID might be anywhere

            for source_gid in assembly_gids[0]: # E - I
                # Do not connect to self
                if source_gid == target_gid: continue
                self._create_synapse_and_connect(source_gid, target_gid, "EI")

            for source_gid in assembly_gids[1]: # I – I
                # Do not connect to self
                if source_gid == target_gid: continue
                self._create_synapse_and_connect(source_gid, target_gid, "II")

                

    def _create_synapse_and_connect(self, source_gid: int, target_gid: int, conn_type: str) -> float:
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
        
        if conn_type == "EE":
            weight = self._compute_gbar(self.parameters.g_EE, self.parameters.p_EE, self.parameters.N_E)
        elif conn_type == "EI":
            weight = self._compute_gbar(self.parameters.g_EI, self.parameters.p_EI, self.parameters.N_E)
        elif conn_type == "IE":
            weight = self._compute_gbar(self.parameters.g_IE, self.parameters.p_IE, self.parameters.N_I)
        elif conn_type == "II":
            weight = self._compute_gbar(self.parameters.g_II, self.parameters.p_II, self.parameters.N_I)

        nc.weight[0] = weight
        nc.delay = 0.5
        nc.threshold = -15

        self.cells_on_node[self.gids_on_node.index(target_gid)].netcons.append(nc)

        with open(self.parameters.graph_file, "a") as file:
            file.write(f"{source_gid},{target_gid},{weight}\n")

        return weight

    def _compute_gbar(self, g_hat: float, p: float, N: int) -> float:
        Z = self.random_state.binomial(n = 1, p = p)
        return g_hat * Z / (p * N + 1e-15)
