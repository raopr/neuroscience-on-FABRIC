## Working on the readme -- incomplete 
To collect stats we need to do the following: </br> </br> 
1-  Create the directory `profilingLogs` in all the nodes `/home/ubuntu/neuroscience-on-FABRIC/PING_assembly/profilingLogs` </br>
2-  Make sure `ssh` between nodes, `sar` and `free` tools are setup/available </br>
3-  We need to start the `monitoring.sh` script on all nodes before running simulation and then end it once the simulation ends. </br> 
start monitoring using the following command `for i in {0..2}; do ssh vm$i "screen -dm bash -c 'bash /home/ubuntu/neuroscience-on-FABRIC/PING_assembly/monitoring.sh; exec sh'"; done`. Change the loop length based on the number of nodes we have. This command opens screen on all nodes and run the `monitoring.sh` script inside it</br>
4- Once simulation ends, kill all screens using ```for i in {0..2}; do 
    ssh vm$i 'screen -ls | grep -o "^[[:space:]]*[0-9]*\\.[^[:space:]]*" | awk "{print \$1}" | xargs -I{} screen -S {} -X quit';
done```

5- To load logs in pandas dataframe for plotting eventually use the following code snippets 
`import pandas as pd` 
</br></br>
For memory log : `columns_to_read = ['total', 'used','free','shared','buff/cache','available']` </br>
`df = pd.read_csv('/path/to/mem_usage.log', delim_whitespace=True,usecols=columns_to_read)`

For cpu log:  `columns_to_read = ['CPU', '%user', '%nice', '%system', '%iowait','%steal', '%idle']`  </br>
`df2 = pd.read_csv('/content/cpu_usage.log', delim_whitespace=True, skiprows=2, usecols=columns_to_read)`
