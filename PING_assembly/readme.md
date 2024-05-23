To collect stats we need to do the following: </br> </br> 
1-  Create the directory `profilingLogs` in all the nodes `/home/ubuntu/neuroscience-on-FABRIC/PING_assembly/profilingLogs` </br>
2-  Make sure `sar` and `free` tools are setup/available </br>
3-  In a screen start gpu monitoring via `./checkgpu.sh`. CPU and Memory logs will start and end automatically with the execution.  </br>
4-  Once the execustion ends, go to screen and cancle the running script. However the proceses will be running in the background, thus do `ps` to list the processes and `kill` to end them
