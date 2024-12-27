#!/bin/sh
  
#SBATCH --job-name=sim
#SBATCH -N 1
#SBATCH -n 4
#SBATCH --ntasks-per-node=4

mkdir -p /home/ubuntu/neuroscience-on-FABRIC/PING_assembly/profilingLogs

printf "Starting cpu monitoring\n"
sar -u 1 > /home/ubuntu/neuroscience-on-FABRIC/PING_assembly/profilingLogs/cpu_usage.log &
SAR_PID=$!
printf "cpu util job id is : "
echo $SAR_PID
printf "\n"

#Start monitoring RAM usage
printf "Starting RAM monitoring\n" 
free -m |  grep "^ "
free -m | stdbuf -o0 grep '^ ' > /home/ubuntu/neuroscience-on-FABRIC/PING_assembly/profilingLogs/mem_usage.log
free -m -s 1 | stdbuf -o0 grep '^Mem:' >> /home/ubuntu/neuroscience-on-FABRIC/PING_assembly/profilingLogs/mem_usage.log &
FREE_PID=$!
printf "RAM utilization job ID is: %s\n" "$FREE_PID"

#printf "Starting gpu monitoring\n"
#monitor_gpu() {
#    local gpu_index=$1
#    local log_file="/home/ubuntu/neuroscience-on-FABRIC/PING_assembly/profilingLogs/gpu_usage.log"
#    printf "made it till here/n"
    #nvidia-smi --query-gpu=timestamp,index,uuid,name,utilization.gpu,utilization.memory,memory.total,memory.used --format=csv -i $gpu_index | head -n 1 > $log_file
#    while true; do
        #nvidia-smi --query-gpu=timestamp,index,name,uuid,utilization.gpu,utilization.memory,memory.total,memory.used --format=csv -i $gpu_index | tail -n +2 >> $log_file
#        sleep 1
#    done
#}

printf "Starting slurm job\n"
START=$(date)
mpiexec x86_64/special -mpi -python simulation.py
END=$(date)

printf "Killing cpu usage monitoring\n" 
kill $SAR_PID

printf "Killing memory usage monitoring\n"
kill $FREE_PID

printf "Start: $START \nEnd:   $END\n"
