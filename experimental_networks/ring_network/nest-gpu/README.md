# Running NEST (GPU)

Simulation:
- Model: [aeif_psc_alpha](https://nest-gpu.readthedocs.io/en/latest/models/index.html)
- Number of cells: 20000
- Time: 30000 ms

[[Set up]](https://github.com/raopr/neuroscience-on-FABRIC/issues/6#issuecomment-1758516441) the environment and variables
```bash
export CUDACXX=/usr/local/cuda-12.2/bin/nvcc
sudo systemctl restart slurmd
sudo systemctl restart slurmctld
source /home/ubuntu/nest-gpu-x-build/bin/nestgpu_vars.sh
```

## 1 GPU
Run with
```bash
sbatch batch_script.sh
```

## 2 GPUs
Run with
```bash
mpirun -np 2 python3 2gpu_run_simulation.py -N 20000 -t 30000
```
