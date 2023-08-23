# https://alleninstitute.github.io/bmtk/tutorial_pointnet_modeling.html

from bmtk.utils.sim_setup import build_env_pointnet
from network import build_network
from bmtk.simulator import pointnet
import json

if __name__ == "__main__":

    # Build network
    build_network(N = 10)
    build_env_pointnet(base_dir = 'sim', network_dir = 'sim/network', dt = 0.01, include_examples = True,
                       tstop = 3000.0)
    
    # Change the config file
    with open("sim/simulation_config.json", "r") as file:
        config = json.load(file)

    config["inputs"] = {"LGN_spikes": {
            "input_type": "spikes",
            "module": "h5",
            "input_file": "$BASE_DIR/lgn_spikes.h5",
            "node_set": "LGN"}}
    
    with open("sim/simulation_config.json", "w") as file:
        json.dump(config, file, indent = 4)

    # Change the python script
    with open("sim/run_pointnet.py", "r") as file:
        py_data = file.readlines()
    py_data[-1] = py_data[-1].replace("${CONFIG}", "config.json")
    with open("sim/run_pointnet.py", "w") as file:
        file.writelines(py_data)