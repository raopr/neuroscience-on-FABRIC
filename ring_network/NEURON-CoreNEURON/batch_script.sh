#!/bin/sh
  
#SBATCH --job-name=sim
#SBATCH --gres=gpu:2
#SBATCH -n 1

mpiexec -n 1 x86_64/special -mpi -python3 run_simulation.py
