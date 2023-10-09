# Running NEST (CPU)

Simulation:

Number of cells: 5000
Time: 5000 ms
Runs for about 15 seconds in human time on CPU

[[For reference]](https://nest-simulator.readthedocs.io/en/v3.6/hpc/parallel_computing.html#distributed-computing): they say no changes to scripts are required to run in parllel.

```bash
mpirun -np 20 python3 run_simulation.py -N 5000 -t 5000
```
