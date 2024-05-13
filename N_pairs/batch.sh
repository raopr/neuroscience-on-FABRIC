#!/bin/sh
  
#SBATCH --job-name=sim
#SBATCH -N 1
#SBATCH -n 2
#SBATCH --ntasks-per-node=2

START=$(date)
mpiexec x86_64/special -mpi -python simulation.py
END=$(date)

printf "Start: $START \nEnd:   $END\n"
