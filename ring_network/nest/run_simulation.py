import nest
import sys

if __name__ == "__main__":

    # Parse cl args
    if len(sys.argv) != 5:
        raise RuntimeError("usage: python3 file -N 10 -t 1000")
    else:
        N = int(sys.argv[sys.argv.index("-N") + 1])
        t_stop = int(sys.argv[sys.argv.index("-t") + 1])

    # Create N vanilla HH neurons
    neurons = nest.Create(model = "aeif_psc_alpha", n = N)

    # Make a ring network
    for i in range(N - 1):
        nest.Connect(neurons[i], neurons[i+1], syn_spec = {'weight': 10, 'delay': 0.1})
    nest.Connect(neurons[N - 1], neurons[0], syn_spec = {'weight': 10, 'delay': 0.1})

    # Apply current injection
    exc = 0.1
    ini = 0.1
    Istim = 2000.0
    Istim1 = 20.0
    nest.SetStatus(neurons[0],  {"tau_syn_ex": exc, "tau_syn_in": ini, "I_e": Istim1})
    nest.SetStatus(neurons[1:],  {"tau_syn_ex": exc, "tau_syn_in": ini, "I_e": Istim})

    # Record voltage and spikes
    voltmeter1 = nest.Create("voltmeter", params = {'record_to': 'memory'})
    nest.Connect(voltmeter1, neurons[0])
    spikes = nest.Create('spike_recorder', params = {'record_to': 'memory'})
    nest.Connect(neurons[0],  spikes)

    nest.Simulate(t_stop)

    print("SUCCESS")
