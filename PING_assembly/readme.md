## Working on the readme -- incomplete 
To collect stats we need to do the following: </br> </br> 
1-  Create the directory `profilingLogs` in all the nodes `/home/ubuntu/neuroscience-on-FABRIC/PING_assembly/profilingLogs` </br></br>
2-  Make sure `ssh` between nodes, `sar` and `free` tools are setup/available </br></br>
3-  We need to start the `monitoring.sh` script on all nodes before running simulation and then end it once the simulation ends. </br> </br>
start monitoring using the following command `for i in {0..2}; do ssh vm$i "screen -dm bash -c 'bash /home/ubuntu/neuroscience-on-FABRIC/PING_assembly/monitoring.sh; exec sh'"; done`. Change the loop length based on the number of nodes we have. This command opens screen on all nodes and run the `monitoring.sh` script inside it</br></br>
4- Once simulation ends, kill all screens using ```for i in {0..2}; do 
    ssh vm$i 'screen -ls | grep -o "^[[:space:]]*[0-9]*\\.[^[:space:]]*" | awk "{print \$1}" | xargs -I{} screen -S {} -X quit';
done```

5- To load logs in pandas dataframe for plotting eventually use the following code snippets. Following commands work in a python enviornment like Google Colab, you can use ipython shell aswell.  
`import pandas as pd` </br>
For memory log : `columns_to_read = ['total', 'used','free','shared','buff/cache','available']` </br>
`df = pd.read_csv('/path/to/mem_usage.log', delim_whitespace=True,usecols=columns_to_read)`

For cpu log:  `columns_to_read = ['CPU', '%user', '%nice', '%system', '%iowait','%steal', '%idle']`  </br>
`df2 = pd.read_csv('/content/cpu_usage.log', delim_whitespace=True, skiprows=2, usecols=columns_to_read)` </br></br>

6- For plotting and saving we can use matplotlib as follows: </br>
Read the csv first mentioned in above step and follow below </br>
```
import matplotlib.pyplot as plt
df.plot()
plt.savefig("memplot.png")
plt.show()
```

7- For GPU plots and reading the logs: </br>
```
use_columns = [' index', ' uuid', ' name', ' utilization.gpu [%]',' utilization.memory [%]', ' memory.total [MiB]', ' memory.used [MiB]']
df = pd.read_csv('/content/profilingLogs_master/gpu_usage.log', delimiter=',')
df = df.drop(columns=['timestamp',' uuid',' name',' memory.total [MiB]'])
df[' utilization.gpu [%]'] = df[' utilization.gpu [%]'].str.replace('%', '').astype(int)
df[' utilization.memory [%]'] = df[' utilization.memory [%]'].str.replace('%', '').astype(int)
df[' memory.used [MiB]'] = df[' memory.used [MiB]'].str.replace('MiB', '').astype(int)


groups = df.groupby(' index')


plt.figure(figsize=(10, 6))

for name, group in groups:
    plt.plot(group.index, group[' utilization.gpu [%]'], marker='o', label=f'GPU {name} - Utilization GPU [%]')
    plt.plot(group.index, group[' utilization.memory [%]'], marker='o', label=f'GPU {name} - Utilization Memory [%]')
    plt.plot(group.index, group[' memory.used [MiB]'], marker='o', label=f'GPU {name} - Memory Used [MiB]')

plt.xlabel('Index')
plt.ylabel('Values')
plt.title('GPU Metrics')

plt.legend(bbox_to_anchor=(0.5, -0.2), loc='lower center', ncol=3)
plt.grid(True)
plt.savefig("/content/gpuPlots.png", bbox_inches='tight') 

plt.show()
```
