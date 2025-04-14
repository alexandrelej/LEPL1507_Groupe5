import random
import math
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

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
    visited_nodes = set(selected_nodes)
    
    while len(selected_nodes) < n:
        current_node = selected_nodes[-1]
        neighbors = list(G.neighbors(current_node))
        unvisited_neighbors = [node for node in neighbors if node not in visited_nodes]
        
        if unvisited_neighbors:
            new_node = random.choice(unvisited_neighbors)
            selected_nodes.append(new_node)
            visited_nodes.add(new_node)
        else:
            # Re-select a node from selected_nodes that has unvisited neighbors
            candidates = [node for node in selected_nodes if any(neighbor not in visited_nodes for neighbor in G.neighbors(node))]
            if not candidates:
                break  # No more nodes can be selected
            selected_nodes.append(random.choice(candidates))
    
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




