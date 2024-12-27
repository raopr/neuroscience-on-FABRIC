import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    with open("graph.txt", "r") as file:
        lines = file.read()

    G = nx.Graph()
    for line in lines.split("\n")[::100]:
        numbers = line.split(",")
        if (len(numbers) == 4) and (np.random.uniform() > 0.5):
            G.add_edge(float(numbers[0]), float(numbers[1]), weight = float(numbers[2]))
    
    nx.draw(G)
    plt.show()