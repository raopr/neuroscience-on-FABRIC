
## Dependencies

```bash
sudo apt-get update 
sudo apt-get install libreadline-dev -y
sudo apt-get install libmeschach-dev -y
sudo apt install python3-pip -y
pip3 install neuron
pip3 install matplotlib
sudo apt install openmpi-bin -y
pip3 install mpi4py
```

## Running the simulation
1. Clone `git clone https://github.com/raopr/neuroscience-on-FABRIC.git` and go to `ball_and_stick_simulation`
2. Adjust parameters in `simulation.py`.
    - Number of cells: `N` in line 9.
    - Duration: `k * ms` in line 16.
3. To run with `mpi`,
```bash
mpiexec -n 20 python3 simulation.py
```

## Running dstat

1. Install 
<br>`sudo apt-get update`
<br>`sudo apt-get install dstat -y`

2. Run
<br>`dstat -t -l -d -m --noupdate 2 > report.txt &`
<br> This command will write the output to report.txt in the background for every 2 seconds. Feel free to modify the time interval. Also, there are more options to collect stats like Netowork. Do `dstat -h` for full list of options 

3. To Stop:
<br> Get the process ID
<br>`pgrep -f "dstat -t -l -c -m -d"`
<br>`kill process-id`
