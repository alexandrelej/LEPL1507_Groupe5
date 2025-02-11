import pandas as pd
import heapq
import math
import networkx as nx

def load_airports(csv_file):
    df = pd.read_csv(csv_file)
    airports = {row['ID']: (row['latitude'], row['longitude']) for _, row in df.iterrows()}
    return airports

def load_connections(csv_file):
    df = pd.read_csv(csv_file)
    connections = set()
    for _, row in df.iterrows():
        try:
            connections.add((row["ID_start"], row["ID_end"]))
        except ValueError:
            print(f"Erreur de format sur la ligne : {row}")
    return connections

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

def CreateGraphe(airports : dict[str, tuple[float,float]] ,connexions : set[tuple[str,str]]) -> nx.DiGraph:

    G : nx.DiGraph = nx.DiGraph()

    # Utilisons la colonne "ID" comme identifiant du nœud
    for airport_id in airports.keys():
        G.add_node(
            airport_id,
        )

    # Ajout des connexions (arêtes) avec l'attribut "distance"
    for source, target in connexions:
        
        # Vérifier que les deux aéroports existent dans le graphe
        if source in G.nodes and target in G.nodes:
            lat1 = airports[source][0]
            lon1 = airports[source][1]
            lat2 = airports[target][0]
            lon2 = airports[target][1]
            distance = haversine(lat1, lon1, lat2, lon2)
            G.add_edge(source, target, distance=distance)
        else:
            print(f"Avertissement : l'un des aéroports {source} ou {target} n'a pas été trouvé dans le fichier des aéroports.")
    return G

def generate_sous_graphe(): #plus petit graphe
    return
def generate_J(): #génère une liste J
    return