# On Scaling Neuronal Network Simulations Using Distributed Computing

> Vladimir Omelyusik, Khawar Shehzad, Tyler Banks, Praveen Rao, and Satish S. Nair. "On Scaling Neuronal Network Simulations Using Distributed Computing." (2024)

Presented at [INDIS Workshop 2024](https://scinet.supercomputing.org/community/indis/previous-editions/sc24-indis/program/) – [[paper]](https://conferences.computer.org/sc-wpub/pdfs/SC-W2024-6oZmigAQfgJ1GhPL0yE3pS/555400a745/555400a745.pdf) – [[slides]](https://delaat.net/sc/sc24/indis/pdf/5.1-112-ws_indis112-Vladimir-Omelyusik.pdf).

## Configuring FABRIC for simulations with NEURON

See [this file](cluster_setup_instr.md) for guidelines on:
- setting up Python, MPI, NVIDIA drivers for GPU access, [Munge](https://dun.github.io/munge/), [SLURM](https://slurm.schedmd.com), [CoreNEURON](https://nrn.readthedocs.io/en/8.0.1/coreneuron/how-to/coreneuron.html), and [METIS](https://metis.readthedocs.io/en/latest/),
- running simulations,
- profiling.

## Networks

- [N-Pairs](N-Pairs/). N cell assemblies of 2 RTM cells connected via a single excitatory synapse.
- [N-K-Cliques](N-K-Cliques/). N cell assemblies of K RTM cells, fully connected with excitatory synapses.
- [PING-Assembly](PING-Assembly/). N cell assemblies of K cells, 80% of which are excitatory and 20% are inhibitory.
  - [PING-Assembly/realistic](PING-Assembly/realistic). Biologically realistic connectivity from [1] (implemented in [CoreNEURON](https://nrn.readthedocs.io/en/8.0.1/coreneuron/how-to/coreneuron.html)).
  - [PING-Assembly/realistic_bmtk](PING-Assembly/realistic_bmtk). Biologically realistic connectivity from [1] (implemented in [BMTK](https://alleninstitute.github.io/bmtk/)).
  - [PING-Assembly/fully_connected](PING-Assembly/fully_connected). Full connectivity within assemblies (biologically unrealistic; implemented in [CoreNEURON](https://nrn.readthedocs.io/en/8.0.1/coreneuron/how-to/coreneuron.html)).
- [Experimental networks](experimental_networks/). Other networks used in early experiments, mostly examples from [the NEURON website](https://neuron.yale.edu/neuron/docs/ball-and-stick-model-part-1).

## Bibliography

[1] Börgers, Christoph. An introduction to modeling neuronal dynamics. Vol. 66. Berlin: Springer, 2017.