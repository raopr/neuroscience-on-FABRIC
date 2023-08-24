
## Dependencies

```bash
sudo apt-get update -y
sudo apt-get install libreadline-dev -y
sudo apt-get install libmeschach-dev -y
sudo apt install python3-pip -y
sudo apt install openmpi-bin -y
pip3 install mpi4py==3.0.3
pip3 install bmtk
pip3 install --upgrade scipy
pip3 uninstall numpy -y
pip3 install numpy==1.23.1
sudo apt-get install nest -y
source /usr/bin/nest/nest_vars.sh -y
```

## Running the simulation
1. Clone `git clone https://github.com/raopr/neuroscience-on-FABRIC.git` and go to `pointnet_simulation`.
2. Adjust parameters in `simulation.py`.
    - Number of cells: `N` in line 11.
    - Duration: `tstop` in line 13.
3. Build network,
```bash
python3 simulation.py
```
4. To run with `mpi`,
```bash
cd sim
mpirun -np 20 python3 run_pointnet.py
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
