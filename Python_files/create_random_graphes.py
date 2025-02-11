import random
import networkx as nx
import pandas as pd

def create_airport_graph(airports_csv, routes_csv):
    # Charger les données des fichiers CSV
    airports = pd.read_csv(airports_csv)
    routes = pd.read_csv(routes_csv)
    
    # Créer un graphe dirigé
    G = nx.DiGraph()
    
    # Ajouter les nœuds (aéroports)
    for index, row in airports.iterrows():
        G.add_node(row['ID'], name=row['name'], city=row['city'], country=row['country'], latitude=row['latitude'], longitude=row['longitude'])
    
    # Ajouter les arêtes (connexions)
    for index, row in routes.iterrows():
        G.add_edge(row['ID_start'], row['ID_end'])
    
    return G

def create_random_subgraph(G, n, m):
    """
    Crée un sous-graphe aléatoire à partir d'un graphe existant.

    Args:
        G (networkx.DiGraph): Le graphe original.
        n (int): Nombre de nœuds dans le sous-graphe.
        m (int): Nombre d'arêtes dans le sous-graphe.

    Returns:
        networkx.DiGraph: Le sous-graphe aléatoire.
    """
    # Étape 1 : Sélectionner n nœuds aléatoires
    if n > G.number_of_nodes():
        print("Le nombre de nœuds demandé dépasse le nombre de nœuds disponibles.")
    selected_nodes = random.sample(list(G.nodes), n)
    
    # Étape 2 : Filtrer les arêtes pour ne garder que celles connectant les nœuds sélectionnés
    potential_edges = [
        edge for edge in G.edges(selected_nodes)
        if edge[0] in selected_nodes and edge[1] in selected_nodes
    ]
    
    # Étape 3 : Sélectionner m arêtes aléatoires parmi celles disponibles
    if m > len(potential_edges):
        print((f"Impossible de sélectionner {m} arêtes parmi les {len(potential_edges)} possibles."))
    selected_edges = random.sample(potential_edges, m)
    
    # Étape 4 : Construire le sous-graphe
    subgraph = nx.DiGraph()
    subgraph.add_nodes_from(selected_nodes)
    subgraph.add_edges_from(selected_edges)
    
    return subgraph


# Chemins vers les fichiers CSV
airports_csv = "../basic_datasets/airports.csv"
routes_csv = "../basic_datasets/pre_existing_routes.csv"

# Créer le graphe complet
airport_graph = create_airport_graph(airports_csv, routes_csv)

# Générer un sous-graphe aléatoire
n = int(input("Nombre de nœuds dans le sous-graphe = "))
m = int(input("Nombre d'arêtes dans le sous-graphe = "))
random_subgraph = create_random_subgraph(airport_graph, n, m)

# Afficher des informations sur le sous-graphe
print("Sous-graphe aléatoire :")
print("Nombre de nœuds :", random_subgraph.number_of_nodes())
print("Nombre d'arêtes :", random_subgraph.number_of_edges())
print("Liste des nœuds :", list(random_subgraph.nodes(data=True)))
print("Liste des arêtes :", list(random_subgraph.edges(data=True)))