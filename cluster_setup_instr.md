# Python + MPI

On all nodes:
```
sudo apt-get update

sudo snap install cmake --classic
sudo apt-get install mpich
sudo apt install -y python3-all-dev
sudo apt install -y python3-pip
sudo apt install -y python3-numpy
sudo apt install -y python3-scipy
sudo apt install -y python3-matplotlib

pip3 install mpi4py-mpich
pip3 install pytest
pip3 install sympy
pip3 install pandas
pip3 install networkx

sudo apt-get install -y bison
sudo apt-get install -y flex
sudo apt-get install -y libreadline-dev
sudo apt install sysstat -y
sudo apt install dstat -y
sudo apt install net-tools -y
```

To resolve `sudo: unable to resolve host Node1: Name or service not known` do `sudo nano /etc/hosts` and add `Node1` or the respective node next to localhost with a space

# NVIDIA drivers

On all nodes:
```
sudo apt install -y ubuntu-drivers-common 
sudo apt install -y nvidia-driver-535
sudo apt install -y alsa-utils
sudo ubuntu-drivers autoinstall
```

```
curl https://developer.download.nvidia.com/hpc-sdk/ubuntu/DEB-GPG-KEY-NVIDIA-HPC-SDK | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-hpcsdk-archive-keyring.gpg
echo 'deb [signed-by=/usr/share/keyrings/nvidia-hpcsdk-archive-keyring.gpg] https://developer.download.nvidia.com/hpc-sdk/ubuntu/amd64 /' | sudo tee /etc/apt/sources.list.d/nvhpc.list
sudo apt-get update -y
sudo apt-get install -y nvhpc-23-9
sudo /opt/nvidia/hpc_sdk/Linux_x86_64/23.9/compilers/bin/makelocalrc -x /opt/nvidia/hpc_sdk/Linux_x86_64/23.9/compilers/bin -net
```

```
wget https://developer.download.nvidia.com/compute/cuda/12.2.2/local_installers/cuda_12.2.2_535.104.05_linux.run
```

The following command will display a window (it might take some time do NOT press any buttons before this window appears). The window will tell you that the driver is already installed, ignore it and choose continue, then accept. Remove "x" from the 535 driver box and choose install.
```
sudo sh cuda_12.2.2_535.104.05_linux.run
```

# Munge

On all nodes:
```bash
sudo apt-get install libmunge-dev libmunge2 munge
sudo systemctl enable munge
sudo systemctl start munge
sudo munge -n | unmunge | grep STATUS
```
Check that "Success" is printed.

On Master node, from ~:
```bash
sudo cp /etc/munge/munge.key ~
sudo chmod 777 munge.key
```
Then send ~/munge.key to ~ of all compute nodes.

On Master node, from ~:
```bash
rm munge.key
```

On Compute nodes:
```bash
sudo rm /etc/munge/munge.key
sudo cp ~/munge.key /etc/munge/
sudo chmod 700 /etc/munge/munge.key
sudo chmod 700 /etc/munge/
sudo chown munge:munge /etc/munge/munge.key
```

On all nodes:
```bash
sudo systemctl restart munge
```

# SLURM

On all nodes:
```
sudo apt-get install slurm-wlm
sudo vim /etc/slurm-llnl/slurm.conf
```

The config file:
```
ControlMachine=Node1
  
MpiDefault=pmi2
ProctrackType=proctrack/linuxproc
ReturnToService=2
SlurmctldPidFile=/var/run/slurmctld.pid
SlurmctldPort=6817
SlurmdPidFile=/var/run/slurmd.pid
SlurmdPort=6818
SlurmdSpoolDir=/var/spool/slurmd
SlurmUser=root
SlurmdUser=root
StateSaveLocation=/var/spool/slurm
SwitchType=switch/none
TaskPlugin=task/none

SchedulerType=sched/backfill
SelectType=select/cons_res
SelectTypeParameters=CR_Core

AccountingStorageType=accounting_storage/none
ClusterName=cluster
JobAcctGatherType=jobacct_gather/none
SlurmdLogFile=/var/log/slurm/slurmd.log
SlurmdDebug=debug2

SlurmctldDebug=5
SlurmctldLogFile=/var/log/slurm/slurmctld.log
DebugFlags=gres

NodeName=Node1 NodeAddr=192.168.1.1 CPUs=20 STATE=UNKNOWN
NodeName=Node2 NodeAddr=192.168.1.2 CPUs=20 STATE=UNKNOWN
NodeName=Node3 NodeAddr=192.168.1.3 CPUs=20 STATE=UNKNOWN
PartitionName=nodes Nodes=ALL Default=YES MaxTime=INFINITE State=UP
```

On worker nodes:
```
sudo systemctl start slurmd
```

On control node:
```
sudo systemctl start slurmctld
sinfo
```

# CoreNEURON

On all nodes:
```
git clone https://github.com/neuronsimulator/nrn
cd nrn
git checkout 047dd82
mkdir build
cd build
cmake .. \
	-DNRN_ENABLE_CORENEURON=ON \
	-DCORENRN_ENABLE_GPU=ON \
	-DNRN_ENABLE_INTERVIEWS=OFF \
	-DNRN_ENABLE_RX3D=OFF \
	-DCMAKE_INSTALL_PREFIX=$HOME/install \
	-DCMAKE_C_COMPILER=/opt/nvidia/hpc_sdk/Linux_x86_64/23.9/compilers/bin/nvc \
	-DCMAKE_CXX_COMPILER=/opt/nvidia/hpc_sdk/Linux_x86_64/23.9/compilers/bin/nvc++
make -j
make install
export PATH=$HOME/install/bin:$PATH
export PYTHONPATH=$HOME/install/lib/python:$PYTHONPATH
```

# Metis
```
git clone https://github.com/xijunke/METIS-1
cd METIS-1/
gunzip metis-5.1.0.tar.gz
tar -xvf metis-5.1.0.tar
cd metis-5.1.0
sudo make config shared=1
sudo make install
pip3 install metis
export METIS_DLL=/usr/local/lib/libmetis.so
```

# Run

Cd to the simulation folder, compile the modfiles
```
nrnivmodl -coreneuron modfiles
```

Batch script:
```
#!/bin/sh
  
#SBATCH --job-name=sim
#SBATCH -N 2
#SBATCH -n 4

mpiexec x86_64/special -mpi -python simulation.py
```

Run with
```
sbatch batch.sh
```

# Broken NVIDIA driver
[Fix is here](https://stackoverflow.com/questions/43022843/nvidia-nvml-driver-library-version-mismatch)


## Stats collection and plotting readme

To collect stats we need to do the following: </br> </br> 
1-  Create the directory `profilingLogs` in all the nodes `/home/ubuntu/neuroscience-on-FABRIC/PING_assembly/profilingLogs` </br></br>
2-  Make sure `ssh` between nodes, `sar` and `free` tools are setup/available </br></br>
3-  We need to start the `monitoring.sh` script on all nodes before running simulation and then end it once the simulation ends. </br> </br>
start monitoring using the following command `for i in {0..2}; do ssh vm$i "screen -dm bash -c 'bash /home/ubuntu/neuroscience-on-FABRIC/PING_assembly/monitoring.sh; exec sh'"; done`. Change the loop length based on the number of nodes we have. This command opens screen on all nodes and run the `monitoring.sh` script inside it</br>
For starting monitoring session in single screen do `screen -dm bash -c 'bash ./monitoring.sh; exec sh'` </br></br>
4- Once simulation ends, kill all screens using ```for i in {0..2}; do 
    ssh vm$i 'screen -ls | grep -o "^[[:space:]]*[0-9]*\\.[^[:space:]]*" | awk "{print \$1}" | xargs -I{} screen -S {} -X quit';
done``` </br>
or to kill screen in single node session do `screen -ls` and note the screen id and do `kill <id>` 

5- To load logs in pandas dataframe for plotting eventually use the following code snippets. Following commands work in a python enviornment like Google Colab, you can use ipython shell aswell.  
`import pandas as pd` </br></br>
For memory log : </br>
```
columns_to_read = ['total', 'used','free','shared','buff/cache','available']
mem_df = pd.read_csv('/path/to/mem_usage.log', delim_whitespace=True)
mem_df.reset_index(drop=True, inplace=True)
```

For cpu log:  
```
columns_to_read = ['CPU', '%user', '%nice', '%system', '%iowait','%steal', '%idle']
cpu_df = pd.read_csv('/content/cpu_usage.log', delim_whitespace=True, skiprows=2, usecols=columns_to_read)
```

For Network log: </br>
```
ntwrk_df = pd.read_csv('/home/ubuntu/neuroscience-on-FABRIC/PING_assembly/profilingLogs/networkLog.log', delim_whitespace=True)
ntwrk_df = ntwrk_df.apply(lambda x: x.str.replace('B', '').astype(int))
```

6- For plotting and saving we can use matplotlib as follows: </br>
Read the csv first mentioned in above step and follow below </br>
```
import matplotlib.pyplot as plt
mem_df.plot()
plt.savefig("memplot.png")
plt.show()
```

7- For GPU plots and reading the logs: </br>
```
use_columns = [' index', ' uuid', ' name', ' utilization.gpu [%]',' utilization.memory [%]', ' memory.total [MiB]', ' memory.used [MiB]']
df = pd.read_csv('/content/profilingLogs_master/gpu_usage.log', delimiter=',')
df = df.drop(columns=['timestamp',' uuid',' name',' memory.total [MiB]'])
df[' utilization.gpu [%]'] = df[' utilization.gpu [%]'].str.replace('%', '').astype(int)
df[' utilization.memory [%]'] = df[' utilization.memory [%]'].str.replace('%', '').astype(int)
df[' memory.used [MiB]'] = df[' memory.used [MiB]'].str.replace('MiB', '').astype(int)


groups = df.groupby(' index')


plt.figure(figsize=(10, 6))

for name, group in groups:
    plt.plot(group.index, group[' utilization.gpu [%]'], marker='o', label=f'GPU {name} - Utilization GPU [%]')
    plt.plot(group.index, group[' utilization.memory [%]'], marker='o', label=f'GPU {name} - Utilization Memory [%]')
    plt.plot(group.index, group[' memory.used [MiB]'], marker='o', label=f'GPU {name} - Memory Used [MiB]')

plt.xlabel('Index')
plt.ylabel('Values')
plt.title('GPU Metrics')

plt.legend(bbox_to_anchor=(0.5, -0.2), loc='lower center', ncol=3)
plt.grid(True)
plt.savefig("/content/gpuPlots.png", bbox_inches='tight') 

plt.show()
```

8- To create subplots of all the logs: </br>

```
###load all dataframes as mem_df, cpu_df, gpu_df, ntwrk_df###


dataframes = [mem_df, cpu_df, gpu_df, ntwrk_df]
titles = ['memory', 'cpu', 'gpu', 'network']

fig, axs = plt.subplots(2, 2, figsize=(15, 10))
axs = axs.flatten()


for i, df in enumerate(dataframes):
    ax = axs[i]
    for col in df.columns:
        ax.plot(df.index, df[col], marker='o', label=col)
    ax.set_title(titles[i])
    ax.legend()
    ax.grid(True)


plt.tight_layout()
plt.savefig("combined_subplots.png")
plt.show()
```
![Screenshot 2024-06-07 at 3 44 21 PM](https://github.com/raopr/neuroscience-on-FABRIC/assets/22073166/ec5f6100-de6d-4269-af28-96c78d845344)




