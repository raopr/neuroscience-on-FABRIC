from neuron import h

h.nrnmpi_init()
pc = h.ParallelContext()

class WTANetwork:

    def __init__(self, num_cell: int, amps: list):
        self.num_cell = num_cell
        self.amps = amps

        self.gidlist = []
        self.cells = []

        self.set_gids()
        self.create_cells()
        self.connect_cells()
        self.init_synapses()
        self.init_current_injections()

    def set_gids(self) -> None:
        # Set cell indices for this node
        self.gidlist = list(range(pc.id(), self.num_cell, pc.nhost()))
        for gid in self.gidlist:
            pc.set_gid2node(gid, pc.id())

    def create_cells(self) -> None:
        # Only create cells which exist on this node
        for gid in self.gidlist:
            self.cells.append(FastSpikingCell(gid = gid, num_synapses = self.num_cell - 1))

        # Associate the cell with this host and gid
        for cell in self.cells:
            pc.cell(cell.gid, cell.spike_detector)

    def connect_cells(self) -> None:

        for target_cell in self.cells:
            source_gids = list(range(0, self.num_cell))
            source_gids.remove(target_cell.gid)
            for gid_ind, s_gid in enumerate(source_gids):
                nc = pc.gid_connect(s_gid, target_cell.synapses[gid_ind])
                nc.weight[0] = 0
                nc.delay = 2
                nc.threshold = 1
                target_cell.netcons.append(nc)
    
    def init_synapses(self) -> None:
        for cell in self.cells:
            for syn in cell.synapses:
                syn.initW = 9

    def init_current_injections(self) -> None:
        for cell in self.cells:
            cell.set_ci(amp = self.amps[cell.gid], dur = 500, delay = 100)


class FastSpikingCell:

    def __init__(self, gid, num_synapses: int):

        self.gid = gid

        # Create sections
        self.soma = h.Section(name = 'soma')
        self.dend = h.Section(name = 'dend')

        # Topology
        self.dend.connect(self.soma(1), 0) # child -> parent

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
        self.soma.insert('leak')
        self.soma.el_leak = -70 # (mV)
        self.soma.glbar_leak = 0.00005 # (S/cm2)

        self.soma.insert('na')
        self.soma.ena = 45 # (mV)
        self.soma.gnabar_na = 0.035 # (S/cm2)

        self.soma.insert('kdr')
        self.soma.ek = -80 # (mV)
        self.soma.gkdrbar_kdr = 0.008 # (S/cm2)

        self.dend.insert('leak')
        self.dend.el_leak = -70 # (mV)
        self.dend.glbar_leak = 0.00005 # (S/cm2)

        self.dend.insert('na')
        self.dend.ena = 45 # (mV)
        self.dend.gnabar_na = 0.01 # (S/cm2)

        self.dend.insert('kdr')
        self.dend.ek = -80 # (mV)
        self.dend.gkdrbar_kdr = 0.003 # S/cm2

        # Connectivity
        self.synapses = []
        for _ in range(num_synapses):
            self.synapses.append(h.GABA(self.soma(0.1)))
        self.netcons = []
        
        # --- Recorders

        # Spikes
        self.spike_detector = h.NetCon(self.dend(0.5)._ref_v, None, sec = self.dend)
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