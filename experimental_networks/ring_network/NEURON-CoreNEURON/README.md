# Running CoreNEURON

Simulation:
- Number of cells: 4000
- Time: 6000 ms

[[Set up]](https://github.com/raopr/neuroscience-on-FABRIC/issues/9#issuecomment-1752290749) the environment. Compile the mod files with
```bash
nrnivmodl -coreneuron .
```

## On CPU
In `run_simulation.py` 
- line 29, set `coreneuron.gpu = False`.
- line 37, uncomment `pc.nthread(20)`.

Run with
```bash
mpiexec -n 1 x86_64/special -mpi -python3 run_simulation.py 
```

## On 1 GPU
In `run_simulation.py` line 29, set `coreneuron.gpu = True`. Run with
```bash
mpiexec -n 1 x86_64/special -mpi -python3 run_simulation.py 
```

## On 2 GPUs
In `run_simulation.py` line 29, set `coreneuron.gpu = True`. Run with
```bash
mpiexec -n 2 x86_64/special -mpi=pmix -python3 run_simulation.py
```
