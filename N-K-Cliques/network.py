from neuron import h
import numpy as np

from cells import RTMExcCell
from parameters import Parameters
import os

h.nrnmpi_init()
pc = h.ParallelContext()

class NCliques:

    def __init__(self, parameters: Parameters) -> None:
        self.parameters = parameters
        self.random_state = np.random.RandomState(self.parameters.random_state + pc.id())

        self.gids_on_node = []
        self.cells_on_node = []

        # Assume cliques are stored consequtively, i.e. [C0, C1, C2, C3, ...] <-> (C0 <-> C1 <-> C2 <-> C3), ...
        # All connections are symmetric, all-to-all
        self.ALL_GIDS = list(range(self.parameters.N_cliques * self.parameters.cells_per_clique))

    def set_gids(self, distributed_gids: list) -> None:
        self.gids_on_node = distributed_gids[pc.id()]
        for gid in self.gids_on_node:
            pc.set_gid2node(gid, pc.id())

    def init_cells(self) -> None:

        for lid, gid in enumerate(self.gids_on_node):
            cell = RTMExcCell(gid = gid, lid = lid)

            # Apply CI only to the first cell in the clique
            if gid % self.parameters.cells_per_clique == 0:
                cell.IClamp.amp = self.parameters.IClamp_amp
            else:
                cell.IClamp.amp = 0

            cell.IClamp.dur = self.parameters.IClamp_dur
            cell.IClamp.delay = self.parameters.IClamp_delay

            self.cells_on_node.append(cell)
        
        # Do separately as an additional check
        for cell in self.cells_on_node:
            pc.cell(cell.gid, cell.spike_detector)

    def connect_cells(self) -> None:
        # Clear the graph file if exists
        if os.path.isfile(self.parameters.graph_file):
            open(self.parameters.graph_file, 'w').close()

        for clique_start_gid in self.ALL_GIDS[::self.parameters.cells_per_clique]:
            # [(0, 1, 2, 3), (4, 5, 6, 7), (...)]
            for target_gid in range(clique_start_gid, clique_start_gid + self.parameters.cells_per_clique):
                for source_gid in range(clique_start_gid, clique_start_gid + self.parameters.cells_per_clique):
                    # Do not connect to self
                    if target_gid == source_gid: continue
                    # Do not connect if not on the current node
                    if target_gid not in self.gids_on_node: continue
                    self._create_synapse_and_connect(source_gid, target_gid)
                

    def _create_synapse_and_connect(self, source_gid: int, target_gid: int) -> float:
        # Create a new synapse on target with respect to source
        syn = h.Exp2Syn(self.cells_on_node[self.gids_on_node.index(target_gid)].soma(0.5))
        syn.e = 0
        syn.tau1 = 0.5
        syn.tau2 = 3

        self.cells_on_node[self.gids_on_node.index(target_gid)].synapses.append(syn)

        # Connect the source to the target
        nc = pc.gid_connect(
            source_gid,
            self.cells_on_node[self.gids_on_node.index(target_gid)].synapses[-1]
            )

        weight = 1
        nc.weight[0] = weight
        nc.threshold = -15

        self.cells_on_node[self.gids_on_node.index(target_gid)].netcons.append(nc)

        with open(self.parameters.graph_file, "a") as file:
            file.write(f"{source_gid},{target_gid},{weight}\n")

        return weight
