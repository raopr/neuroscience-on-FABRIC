import os

# Set GPUs
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    os.environ["CUDA_VISIBLE_DEVICES"]="0"
else:
    os.environ["CUDA_VISIBLE_DEVICES"]="1"

import nestgpu as ngpu
ngpu.ConnectMpiInit()

import sys

if __name__ == "__main__":

    # Parse cl args
    if len(sys.argv) != 5:
        raise RuntimeError("usage: python3 file -N 10 -t 1000")
    else:
        N = int(sys.argv[sys.argv.index("-N") + 1])
        t_stop = int(sys.argv[sys.argv.index("-t") + 1])

    # Create N / 2 neurons on each node
    neurons = []
    for i in range(2):
        neurons.append(ngpu.RemoteCreate(i, "aeif_psc_alpha", N // 2).node_seq)

    # Make a ring network
    conn_dict = {"rule": "one_to_one"}

    # Connect on the first node
    if rank == 0:
        for i in range(N // 2 - 1):
            ngpu.Connect(neurons[0][i:i+1], neurons[0][i+1:i+2], conn_dict, {'weight': 10, 'delay': 0.1, "receptor": 0})

    # Connect to the second node
    ngpu.RemoteConnect(0, neurons[0][N // 2 - 1 : N // 2], 1, neurons[1][0:1], conn_dict, {'weight': 10, 'delay': 0.1, "receptor": 0})

    # Connect on the second node
    if rank == 1:
        for i in range(N // 2 - 1):
            ngpu.Connect(neurons[1][i:i+1], neurons[1][i+1:i+2], conn_dict, {'weight': 10, 'delay': 0.1, "receptor": 0})

    spike_det = ngpu.Create("spike_detector")
    ngpu.Connect([neurons[0][0]], spike_det, {"rule": "one_to_one"}, {"weight": 1.0, "delay": 1.0, "receptor":0})

    # Apply current injection
    exc = 0.1
    ini = 0.1
    Istim = 2000.0
    Istim1 = 20.0
    ngpu.SetStatus(neurons[0][0:1],  {"tau_syn_ex": exc, "tau_syn_in": ini, "I_e": Istim1})
    ngpu.SetStatus(neurons[1][1:N//2],  {"tau_syn_ex": exc, "tau_syn_in": ini, "I_e": Istim})

    # Record voltage and spikes
    voltage = ngpu.CreateRecord("", ["V_m"], [neurons[0][0]], [0])
    spikes = ngpu.CreateRecord("", ["spike_height"], [spike_det[0]], [0])
    
    ngpu.Calibrate()
    ngpu.Simulate(t_stop)

    print("SUCCESS")
