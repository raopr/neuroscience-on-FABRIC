# Results

## 1VM on 1 Node

### CoreNEURON

N = 4000, t = 6000 ms

| #GPUs      | Site | Time (sec) | Speedup | MAX GPU1 (%) | MAX GPU2 (%) |
| ---------- | ---- | ---------- | ------- | ------------ | ------------ |
| 0 (CPU=20) | MAX  | 251        | 1       | 0            | 0            |
| 1          | MAX  | 121        | 2       | 41           | 0            |
| 2          | MAX  | 117        | 2       | 41           | 0            |


### NEST

N = 20000, t = 30000 ms

| #GPUs      | Site | Time (sec) | Speedup | MAX GPU1 (%) | MAX GPU2 (%) |
| ---------- | ---- | ---------- | ------- | ------------ | ------------ |
| 0 (CPU=20) | MAX  | 8243       | 1       | 0            | 0            |
| 1          | MAX  | 43         | 190     | 77           | 0            |
| 2          | MAX  | 43         | 190     | 77           | 0            |
