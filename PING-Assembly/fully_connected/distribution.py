import numpy as np
import metis
import networkx as nx

def distribute_randomly(parameters):
    random_state = np.random.RandomState(parameters.random_state)
    all_gids = np.arange(parameters.N_assemblies * (parameters.N_E + parameters.N_I))
    distributed_gids = []
    random_state.shuffle(all_gids)
    for array in np.split(all_gids, parameters.N_assemblies):
        distributed_gids.append(array.tolist())
    return distributed_gids

def distribute_by_assembly(parameters):
    all_gids = np.arange(parameters.N_assemblies * (parameters.N_E + parameters.N_I))
    distributed_gids = []
    for array in np.split(all_gids, parameters.N_assemblies):
        distributed_gids.append(array.tolist())
    return distributed_gids

def _read_graph(path):
    with open(path, "r") as file: lines = file.read()

    G = nx.Graph()
    for line in lines.split("\n"):
        numbers = line.split(",")
        if (len(numbers) >= 3):
            G.add_edge(float(numbers[0]), float(numbers[1]), weight = float(numbers[2]))
    return G

def distribute_by_partitioning(parameters):

    G = _read_graph("graph.txt")
    results = metis.part_graph(G, nparts = parameters.N_assemblies, objtype = "cut")
    print(f"Partitioning error: {results[0]}")

    all_gids = np.arange(parameters.N_assemblies * (parameters.N_E + parameters.N_I))
    distributed_gids = []
    for i in range(parameters.N_assemblies):
        distributed_gids.append(all_gids[np.array(results[1]) == i].tolist())
    return distributed_gids
