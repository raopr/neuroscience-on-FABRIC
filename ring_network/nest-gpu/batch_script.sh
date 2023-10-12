#!/bin/sh
  
#SBATCH --job-name=sim
#SBATCH --gres=gpu:1
#SBATCH -n 1

srun python3 run_simulation.py -N 20000 -t 30000
