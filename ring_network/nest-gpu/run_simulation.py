import nestgpu as ngpu
import sys

if __name__ == "__main__":

    # Parse cl args
    if len(sys.argv) != 5:
        raise RuntimeError("usage: python3 file -N 10 -t 1000")
    else:
        N = int(sys.argv[sys.argv.index("-N") + 1])
        t_stop = int(sys.argv[sys.argv.index("-t") + 1])

    # Create N vanilla HH neurons
    neurons = ngpu.Create("aeif_psc_alpha", N)

    # Make a ring network
    conn_dict = {"rule": "one_to_one"}
    for i in range(N - 1):
        ngpu.Connect(neurons[i:i+1], neurons[i+1:i+2], conn_dict, {'weight': 10, 'delay': 0.1, "receptor": 0})
    ngpu.Connect(neurons[N - 1:N], neurons[0:1], conn_dict, {'weight': 10, 'delay': 0.1, "receptor": 0})

    spike_det = ngpu.Create("spike_detector")
    ngpu.Connect([neurons[0]], spike_det, {"rule": "one_to_one"}, {"weight": 1.0, "delay": 1.0, "receptor":0})

    # Apply current injection
    exc = 0.1
    ini = 0.1
    Istim = 2000.0
    Istim1 = 20.0
    ngpu.SetStatus(neurons[0:1],  {"tau_syn_ex": exc, "tau_syn_in": ini, "I_e": Istim1})
    ngpu.SetStatus(neurons[1:N],  {"tau_syn_ex": exc, "tau_syn_in": ini, "I_e": Istim})

    # Record voltage and spikes
    voltage = ngpu.CreateRecord("", ["V_m"], [neurons[0]], [0])
    spikes = ngpu.CreateRecord("", ["spike_height"], [spike_det[0]], [0])

    ngpu.Simulate(t_stop)

    print("SUCCESS")
