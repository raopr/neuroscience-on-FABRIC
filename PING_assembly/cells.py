from neuron import h

class WBInhCell:

    def __init__(self, gid: int, lid: int) -> None:
        self.gid = gid
        self.lid = lid
        self.synapses = []
        self.netcons = []

        # Set soma
        self.soma = h.Section(name = "soma")
        self.soma.nseg = 1
        self.soma.cm = 1 # (microF / cm2)
        
        # Insert channels
        self.soma.insert("leak")
        self.soma.eleak = -65 # (mV)
        self.soma.gbar_leak = 1e-4 # (siemens / cm2)

        self.soma.insert("na_wb")
        self.soma.ena = 55
        self.soma.gbar_na_wb = 0.035 # (siemens / cm2)

        self.soma.insert("k_wb")
        self.soma.ek = -90
        self.soma.gbar_k_wb = 0.009 # // (siemens / cm2)

        # Spikes
        self.spike_detector = h.NetCon(self.soma(0.5)._ref_v, None, sec = self.soma)
        self.spike_times = h.Vector()
        self.spike_detector.record(self.spike_times)

        # Soma voltage
        self.V = h.Vector().record(self.soma(0.5)._ref_v)

        # Current
        self.IClamp = h.IClamp(self.soma(0.5))

class RTMExcCell:

    def __init__(self, gid: int, lid: int) -> None:
        self.gid = gid
        self.lid = lid
        self.synapses = []
        self.netcons = []

        # Set soma
        self.soma = h.Section(name = "soma")
        self.soma.nseg = 1
        self.soma.cm = 1 # (microF / cm2)
        
        # Insert channels
        self.soma.insert("leak")
        self.soma.eleak = -67 # (mV)
        self.soma.gbar_leak = 1e-4 # (siemens / cm2)

        self.soma.insert("na_rtm")
        self.soma.ena = 50
        self.soma.gbar_na_rtm = 0.1 # (siemens / cm2)

        self.soma.insert("k_rtm")
        self.soma.ek = -100
        self.soma.gbar_k_rtm = 0.08 # (siemens / cm2)

        # Spikes
        self.spike_detector = h.NetCon(self.soma(0.5)._ref_v, None, sec = self.soma)
        self.spike_times = h.Vector()
        self.spike_detector.record(self.spike_times)

        # Soma voltage
        self.V = h.Vector().record(self.soma(0.5)._ref_v)

        # Current
        self.IClamp = h.IClamp(self.soma(0.5))
