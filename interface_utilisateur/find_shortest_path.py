import pandas as pd
import networkx as nx

def add_prices(G, prices_csv):
    """
    Ajoute les prix des vols aux arêtes du graphe.
    """
    prices = pd.read_csv(prices_csv)
    
    for edge in G.edges:
        start_node, end_node = edge
        price = prices[(prices['ID_start'] == start_node) & (prices['ID_end'] == end_node)]['price'].values
        if price:
            G.edges[start_node, end_node]['price'] = price[0]
        else:
            print(f"Prix non trouvé pour le vol de {start_node} à {end_node}.")


def add_times(G, waiting_times_csv, average_speed=800):
    """
    Ajoute les temps de vol et les temps d'attente de l'aéroport de départ aux arêtes du graphe.
    """
    # waiting_times contain the waiting times at each airport
    waiting_times = pd.read_csv(waiting_times_csv)
    # 1) convertir les distances en temps de vol
    # 2) ajouter les temps d'attentes aux temps de vol
    for edge in G.edges:
        start_node, end_node = edge
        distance = G.edges[start_node, end_node]['distance']
        speed = average_speed
        time = distance / speed
        # Add waiting time at the start node
        G.nodes[start_node]['idle_time'] = waiting_times[waiting_times['ID'] == start_node]['idle_time'].values[0]
        time += G.nodes[start_node]['idle_time']/60
        G.edges[edge]['time'] = time

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