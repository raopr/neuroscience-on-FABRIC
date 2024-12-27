import numpy as np

from bmtk.builder.networks import NetworkBuilder
from bmtk.builder.auxi.node_params import positions_columinar
from bmtk.builder.auxi.edge_connectors import distance_connector

def build_network(N = 400):

    net = NetworkBuilder("V1")

    # Create neurons
    net.add_nodes(N = N, positions=positions_columinar(N = N, center = [0, 50.0, 0], max_radius = 30.0, height = 100.0),
                  pop_name = 'Scnn1a', location = 'VisL4', ei = 'e', model_type = 'point_process',
                  model_template = 'nest:iaf_psc_alpha', dynamics_params = '472363762_point.json')
    
    ## E-to-E connections
    net.add_edges(source = {'ei': 'e'}, target = {'pop_name': 'Scnn1a'}, connection_rule = distance_connector,
                  connection_params = {'d_weight_min': 0.0, 'd_weight_max': 0.34, 'd_max': 300.0, 'nsyn_min': 3, 'nsyn_max': 7},
                  syn_weight = 3.0, delay = 2.0, dynamics_params = 'ExcToExc.json', model_template = 'static_synapse')
    
    net.build()
    net.save_nodes(output_dir = 'sim/network')
    net.save_edges(output_dir = 'sim/network')

    # Spike trains
    lgn = NetworkBuilder('LGN')
    lgn.add_nodes(N = N, pop_name = 'tON', potential = 'exc', model_type = 'virtual')

    lgn.add_edges(source = lgn.nodes(), target = net.nodes(pop_name = 'Scnn1a'), iterator = 'all_to_one', 
                  connection_rule = select_source_cells, connection_params = {'nsources_min': 10, 'nsources_max': 25},
                  syn_weight = 15.0, delay = 2.0, dynamics_params = 'ExcToExc.json', model_template = 'static_synapse')
    
    lgn.build()
    lgn.save_nodes(output_dir='sim/network')
    lgn.save_edges(output_dir='sim/network')

def select_source_cells(sources, target, nsources_min = 10, nsources_max = 30, nsyns_min = 3, nsyns_max = 12):
    total_sources = len(sources)
    nsources = np.random.randint(nsources_min, nsources_max)
    selected_sources = np.random.choice(total_sources, nsources, replace = False)
    syns = np.zeros(total_sources)
    syns[selected_sources] = np.random.randint(nsyns_min, nsyns_max, size = nsources)
    return syns