import random
import networkx as nx
import pandas as pd

def create_airport_graph(airports_csv, routes_csv):
    # Charger les données des fichiers CSV
    airports = pd.read_csv(airports_csv)
    routes = pd.read_csv(routes_csv)
    
    # Créer un graphe dirigé
    G = nx.DiGraph()
    
    # Ajouter les nœuds (aéroports) avec leurs attributs
    for index, row in airports.iterrows():
        G.add_node(row['ID'], name=row['name'], city=row['city'], country=row['country'], latitude=row['latitude'], longitude=row['longitude'])
    
    # Ajouter les arêtes (connexions) avec les attributs si disponibles (ici j'ai supposé qu'il n'y en a pas dans le fichier CSV)
    for index, row in routes.iterrows():
        G.add_edge(row['ID_start'], row['ID_end'])
    
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

    # Ajouter les arêtes (sans attributs) au sous-graphe

    subgraph.add_edges_from(selected_edges)

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


# Chemins vers les fichiers CSV
airports_csv = "../basic_datasets/airports.csv"
routes_csv = "../basic_datasets/pre_existing_routes.csv"

# Créer le graphe complet
airport_graph = create_airport_graph(airports_csv, routes_csv)

# Générer un sous-graphe aléatoire
n = int(input("Nombre de nœuds dans le sous-graphe = "))
m = int(input("Nombre d'arêtes dans le sous-graphe = "))
j = int(input("Nombre de chemins requis (paires de destinations) = "))
random_subgraph = create_random_subgraph(airport_graph, n, m)

# Générer j paires de destinations reliées par un chemin
destination_pairs = generate_random_pairs(random_subgraph, j)

# Afficher des informations sur le sous-graphe et les paires de destinations
print("Sous-graphe aléatoire :")
print("Nombre de nœuds :", random_subgraph.number_of_nodes())
print("Nombre d'arêtes :", random_subgraph.number_of_edges())
print("Liste des nœuds :", list(random_subgraph.nodes(data=True)))
print("Liste des arêtes :", list(random_subgraph.edges(data=True)))

# Afficher les paires de destinations
print(f"Paires de destinations (avec chemin) : {destination_pairs}")

