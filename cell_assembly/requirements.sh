#!/usr/bin/env bash

sudo apt-get update -y

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

sudo apt-get install -y bison
sudo apt-get install -y flex
sudo apt-get install -y libreadline-dev

sudo apt install -y ubuntu-drivers-common 
sudo apt install -y nvidia-driver-535
sudo apt install -y alsa-utils
sudo ubuntu-drivers autoinstall

curl https://developer.download.nvidia.com/hpc-sdk/ubuntu/DEB-GPG-KEY-NVIDIA-HPC-SDK | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-hpcsdk-archive-keyring.gpg
echo 'deb [signed-by=/usr/share/keyrings/nvidia-hpcsdk-archive-keyring.gpg] https://developer.download.nvidia.com/hpc-sdk/ubuntu/amd64 /' | sudo tee /etc/apt/sources.list.d/nvhpc.list
sudo apt-get update -y
sudo apt-get install -y nvhpc-23-9
sudo /opt/nvidia/hpc_sdk/Linux_x86_64/23.9/compilers/bin/makelocalrc -x /opt/nvidia/hpc_sdk/Linux_x86_64/23.9/compilers/bin -net

wget https://developer.download.nvidia.com/compute/cuda/12.2.2/local_installers/cuda_12.2.2_535.104.05_linux.run
