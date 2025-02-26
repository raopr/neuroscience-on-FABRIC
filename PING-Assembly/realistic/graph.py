import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    with open("graph_2000.txt", "r") as file:
        lines = file.read()

    G = nx.Graph()
    for line in lines.split("\n"):
        numbers = line.split(",")
        if (len(numbers) == 3) and (np.random.uniform() > 0.5):
            G.add_edge(float(numbers[0]), float(numbers[1]), weight = float(numbers[2]))
    
    nx.draw(G)
    plt.show()