#!/bin/bash
monitor_gpu() {
    local gpu_index=$1
    local log_file="/home/ubuntu/neuroscience-on-FABRIC/PING_assembly/profilingLogs/gpu_usage.log"
    nvidia-smi --query-gpu=timestamp,index,uuid,name,utilization.gpu,utilization.memory,memory.total,memory.used --format=csv -i $gpu_index | head -n 1 > $log_file
    while true; do
        nvidia-smi --query-gpu=timestamp,index,name,uuid,utilization.gpu,utilization.memory,memory.total,memory.used --format=csv -i $gpu_index | tail -n +2 >> $log_file
        sleep 1
    done
}

GPU_PIDS+=($!)
for gpu_index in $(nvidia-smi --query-gpu=index --format=csv,noheader); do
    monitor_gpu $gpu_index &
    GPU_PIDS+=($!)
done
PIDS=$(jobs -p)

#sleep 10 

#for pid in "${GPU_PIDS[@]}"; do
#    kill $pid
#done

wait
