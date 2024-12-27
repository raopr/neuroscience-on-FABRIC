dstat -t -l -d -m --noupdate 5 > report.txt &
python3 simulation.py
cd sim
mpirun -np 20 python3 run_pointnet.py
