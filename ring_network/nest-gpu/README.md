# Running NEST (GPU)

Simulation:
- Model: [aeif_psc_alpha](https://nest-gpu.readthedocs.io/en/latest/models/index.html)
- Number of cells: 5000
- Time: 5000 ms

[[Set up]](https://github.com/raopr/neuroscience-on-FABRIC/issues/6#issuecomment-1750145807) the environment and variables
```bash
export CUDACXX=/usr/local/cuda-12.2/bin/nvcc
source /home/ubuntu/nest-gpu-x-build/bin/nestgpu_vars.sh
```

Run with
```bash
sbatch batch_script.sh
```
