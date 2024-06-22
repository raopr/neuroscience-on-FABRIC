from network import PINGAN
from parameters import Parameters

# Generates graph.txt
if __name__ == "__main__":
    parameters = Parameters()
    net = PINGAN(parameters)
    net.generate_connectivity()