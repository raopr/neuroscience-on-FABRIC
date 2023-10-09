# Running CoreNEURON

Simulation:
- Number of cells: 5000
- Time: 5000 ms
- Runs for about 3 mins in human time on CPU

[[Setup]](https://github.com/raopr/neuroscience-on-FABRIC/issues/9#issuecomment-1752290749) the environment. Compile the mod files with
```bash
nrnivmodl -coreneuron .
```

## On CPU
In `run_simulation.py` line 15, set `coreneuron.gpu = False`. Run with
```bash
mpiexec -n 1 x86_64/special -mpi -python3 run_simulation.py 
```

## On GPU
In `run_simulation.py` line 15, set `coreneuron.gpu = True`. Run with
```bash
mpiexec -n 1 x86_64/special -mpi -python3 run_simulation.py 
```
