import pandas as pd
import networkx as nx


def find_shortest_path(G, start_node, end_node, metric='distance'):
    """
    Trouve le plus court chemin entre deux nœuds dans un graphe.
    """
    if metric == 'time':
        # retire le temps d'attente au premier nœud
        length -= G.nodes[start_node]['idle_time']
    path = nx.shortest_path(G, start_node, end_node, weight=metric)
    length = nx.shortest_path_length(G, start_node, end_node, weight=metric)
    return path, length