import numpy as np
import metis
import networkx as nx

def distribute_randomly(parameters, pc):
    random_state = np.random.RandomState(parameters.random_state)
    all_gids = np.arange(parameters.N_assemblies * (parameters.N_E + parameters.N_I)).tolist()
    distributed_gids = []
    for _ in range(pc.nhost()):
        distributed_gids.append(random_state.choice(a = all_gids, size = parameters.N_E + parameters.N_I, replace = False).tolist())
        for gid in distributed_gids[-1]:
            all_gids.remove(gid)
    return distributed_gids

def distribute_by_assembly(parameters, pc):
    all_gids = np.arange(parameters.N_assemblies * (parameters.N_E + parameters.N_I)).tolist()
    distributed_gids = []
    for i in range(pc.nhost()):
        distributed_gids.append(all_gids[(parameters.N_E + parameters.N_I) * i : (parameters.N_E + parameters.N_I) * (i + 1)])
    return distributed_gids

def distribute_round_robin(parameters, pc):
    all_gids = np.arange(parameters.N_assemblies * (parameters.N_E + parameters.N_I))
    distributed_gids = []
    for i in range(pc.nhost()):
        node_gids = []
        for j in range(i, len(all_gids), pc.nhost()):
            node_gids.append(all_gids[j])
        distributed_gids.append(node_gids)
    return distributed_gids

def _read_graph(path):
    with open(path, "r") as file: lines = file.read()

    G = nx.Graph()
    for line in lines.split("\n"):
        numbers = line.split(",")
        if (len(numbers) >= 3):
            G.add_edge(float(numbers[0]), float(numbers[1]), weight = float(numbers[2]))
    return G

def distribute_by_partitioning(parameters, pc):

    G = _read_graph("graph.txt")
    results = metis.part_graph(G, nparts = parameters.nparts, objtype = "cut")
    print(f"Partitioning error: {results[0]}")

    distributed_gids = []
    for i in range(pc.nhost()):
        distributed_gids.append(results[1][(parameters.N_E + parameters.N_I) * i : (parameters.N_E + parameters.N_I) * (i + 1)])
    return distributed_gids