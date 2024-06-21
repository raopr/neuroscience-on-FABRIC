#!/bin/bash

printf "Starting cpu monitoring\n"
sar -u 1 > /home/ubuntu/neuroscience-on-FABRIC/N_pairs/profilingLogs/cpu_usage.log &
SAR_PID=$!
printf "cpu util job id is : "
echo $SAR_PID
printf "\n"

#Start monitoring RAM usage
printf "Starting RAM monitoring\n" 
free -m |  grep "^ "
free -m | stdbuf -o0 grep '^ ' > /home/ubuntu/neuroscience-on-FABRIC/N_pairs/profilingLogs/mem_usage.log
free -m -s 1 | stdbuf -o0 grep '^Mem:' >> /home/ubuntu/neuroscience-on-FABRIC/N_pairs/profilingLogs/mem_usage.log &
FREE_PID=$!
printf "RAM utilization job ID is: %s\n" "$FREE_PID"


#start network monitoring 
echo "recv send" > /home/ubuntu/neuroscience-on-FABRIC/N_pairs/profilingLogs/networkLog.log



printf "Starting gpu monitoring\n"
monitor_gpu() {
    local gpu_index=$1
    local log_file="/home/ubuntu/neuroscience-on-FABRIC/N_pairs/profilingLogs/gpu_usage.log"
    nvidia-smi --query-gpu=timestamp,index,uuid,name,utilization.gpu,utilization.memory,memory.total,memory.used --format=csv -i $gpu_index | head -n 1 > $log_file
    while true; do
        dstat --net --nocolor 1 5 | tail -n +3 >> /home/ubuntu/neuroscience-on-FABRIC/N_pairs/profilingLogs/networkLog.log
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
