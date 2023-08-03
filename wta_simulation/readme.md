
## Dependencies

```bash
sudo apt-get update 
sudo apt-get install libreadline-dev
sudo apt-get install libmeschach-dev
sudo apt install python3-pip
pip3 install neuron
pip3 install matplotlib
sudo apt install openmpi-bin
pip3 install mpi4py
```

## Running the simulation
1. Go to the folder which contains both `simulation.py` and `modfiles/`
2. From this folder, compile the modfiles,
```bash
/home/ubuntu/.local/bin/nrnivmodl modfiles
```
3. Adjust parameters in `simulation.py`.
4. To run with `mpi`,
```bash
mpiexec -n 2 python simulation.py
```
