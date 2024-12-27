import numpy as np
from bmtk.utils.reports.spike_trains import SpikeTrains

spikes = SpikeTrains.load('/Users/vladimiromelyusik/neuroscience-on-FABRIC/PING-bmtk/output/spikes.h5', population = 'PING-Assembly')
ISI = np.diff(np.sort(spikes.get_times(node_id = 0)))
print(f"The network is oscillating around {1000 / np.mean(ISI)} Hz.")