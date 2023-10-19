#!/bin/sh
  
#SBATCH --job-name=sim
#SBATCH --gres=gpu:2
#SBATCH -n 2

mpiexec -n 2 x86_64/special -mpi -python3 run_simulation.py
