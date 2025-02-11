import random
import networkx as nx
import pandas as pd
import math
from create_graphe import haversine


def create_airport_graph(airports_csv, routes_csv):
    # Charger les données des fichiers CSV
    airports = pd.read_csv(airports_csv)
    routes = pd.read_csv(routes_csv)
    
    # Créer un graphe dirigé
    G = nx.DiGraph()
    
    # Ajouter les nœuds (aéroports) avec leurs attributs
    for index, row in airports.iterrows():
        G.add_node(row['ID'], 
                   name=row['name'], 
                   city=row['city'], 
                   country=row['country'], 
                   latitude=row['latitude'], 
                   longitude=row['longitude'])
    
    # Ajouter les arêtes (connexions) avec l'attribut distance
    for index, row in routes.iterrows():
        start_node = row['ID_start']
        end_node = row['ID_end']
        
        # Obtenir les coordonnées des deux nœuds
        lat1, lon1 = G.nodes[start_node]['latitude'], G.nodes[start_node]['longitude']
        lat2, lon2 = G.nodes[end_node]['latitude'], G.nodes[end_node]['longitude']
        
        # Calculer la distance entre les deux nœuds
        distance = haversine(lat1, lon1, lat2, lon2)
        
        # Ajouter l'arête avec la distance comme attribut
        G.add_edge(start_node, end_node, distance=distance)
    
    return G

def create_random_subgraph(G, n, m):
    """
    Crée un sous-graphe aléatoire à partir d'un graphe existant avec des nœuds adjacents.
    """
    # Étape 1 : Sélectionner un nœud de départ
    start_node = random.choice(list(G.nodes))
    
    # Étape 2 : Sélectionner les nœuds adjacents au nœud de départ
    selected_nodes = [start_node]
    while len(selected_nodes) < n:
        neighbors = list(G.neighbors(selected_nodes[-1]))
        if not neighbors:
            break  # Arrêter si aucun voisin disponible
        new_node = random.choice(neighbors)
        if new_node not in selected_nodes:
            selected_nodes.append(new_node)
    
    # Si moins de nœuds peuvent être sélectionnés, on arrête ici
    if len(selected_nodes) < n:
        print(f"Impossible de sélectionner {n} nœuds adjacents. Il y en a seulement {len(selected_nodes)}.")

    # Étape 3 : Filtrer les arêtes pour ne garder que celles connectant les nœuds sélectionnés
    potential_edges = [
        edge for edge in G.edges(selected_nodes)
        if edge[0] in selected_nodes and edge[1] in selected_nodes
    ]
    
    # Étape 4 : Sélectionner m arêtes parmi celles disponibles
    if m > len(potential_edges):
        print(f"Impossible de sélectionner {m} arêtes parmi les {len(potential_edges)} possibles.")
    selected_edges = random.sample(potential_edges, m)
    
    # Étape 5 : Construire le sous-graphe et ajouter les nœuds avec leurs attributs
    subgraph = nx.DiGraph()
    subgraph.add_nodes_from(selected_nodes)

    # Copier les attributs des nœuds du graphe original vers le sous-graphe
    for node in selected_nodes:
        for key, value in G.nodes[node].items():
            subgraph.nodes[node][key] = value

    # Ajouter les arêtes (avec attributs de distance) au sous-graphe
    for edge in selected_edges:
        # Obtenir la distance de l'arête du graphe original
        distance = G[edge[0]][edge[1]]['distance']
        # Ajouter l'arête avec l'attribut distance
        subgraph.add_edge(edge[0], edge[1], distance=distance)

    return subgraph

def generate_random_pairs(subgraph, j):
    """
    Génère j paires de destinations parmi les nœuds du sous-graphe, où chaque paire est reliée par un chemin.
    """
    # Récupérer la liste des nœuds du sous-graphe
    nodes = list(subgraph.nodes)
    
    # Liste pour stocker les paires de destinations
    pairs = []
    
    while len(pairs) < j:
        # Choisir deux nœuds différents parmi ceux du sous-graphe
        node1, node2 = random.sample(nodes, 2)
        
        # Vérifier qu'il existe un chemin entre node1 et node2 dans le sous-graphe
        if nx.has_path(subgraph, node1, node2):
            pairs.append((node1, node2))
    
    return pairs





