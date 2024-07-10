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
```

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
wget http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/metis-5.1.0.tar.gz
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
