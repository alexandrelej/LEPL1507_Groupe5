import networkx as nx
import numpy as np
import time
import random
from create_graphs import haversine


def generate_order(G: nx.DiGraph, Trajets: list[tuple[str, str]], mode = "random") -> list[tuple[str, str]]:
    """
    Génère un ordre dans lequel les trajets seront parcourus.

    Paramètres :
        G (nx.DiGraph) : Le graphe représentant le réseau.
        Trajets (list[tuple[str, str]]) : Liste de paires (source, destination).
        mode (str) : Méthode de génération ("random" ou "shortest").

    Retourne :
        list[tuple[str, str]] : Liste des trajets dans l'ordre défini.
    """

    if mode == "random":
        return random.sample(Trajets, len(Trajets))
    elif mode == "shortest":
        path_lengths = []
        for Trajet in Trajets:
            start = Trajet[0]
            end = Trajet[1]
            shortest_path_length = nx.shortest_path_length(G, source=start, target=end, weight='distance')
            path_lengths.append((Trajet, shortest_path_length))
            path_lengths.sort(key=lambda x: x[1])
        return [Trajet for Trajet, _ in path_lengths]


def Update_costs(G: nx.DiGraph, Trajets: list[tuple[str, str]], C: float,iterations : int=10) -> nx.DiGraph:
    """
    Approche itérative pour approximer une solution optimale en utilisant A* et une pondération dynamique des arêtes.

    Paramètres :
        G (nx.DiGraph) : Graphe initial avec distances et coordonnées géographiques.
        Trajets (list[tuple[str, str]]) : Liste de trajets à assurer.
        C (float) : Coût fixe appliqué à chaque arête si elle est utilisée.
        iterations (int) : Nombre d'itérations pour affiner les chemins et stabiliser les pondérations.

    Retourne :
        tuple :
            - G_reweighted (nx.DiGraph) : Graphe optimisé avec les arêtes inutilisées supprimées.
            - G (nx.DiGraph) : Graphe original (non modifié).
    """

    def heuristic(u, v):
        return haversine(G.nodes[u]["latitude"], G.nodes[u]["longitude"], G.nodes[v]["latitude"], G.nodes[v]["longitude"])

    G_reweighted = G.copy()
    N = len(Trajets)
    nx.set_edge_attributes(G_reweighted, 0, "used")
    for edge in G_reweighted.edges():
        G_reweighted.edges[edge]['distance'] += N*C
    
    shortest_paths = {}
    total_length = 0
    for it in range(iterations):
        for trajet in generate_order(G_reweighted, Trajets, mode=random.choice(["shortest","random"])):
            if it > 0:
                #remove the previous path
                path = shortest_paths[trajet][0]
                for i in range(len(path) - 1):
                    G_reweighted[path[i]][path[i+1]]['used'] -= 1
                    if G_reweighted[path[i]][path[i+1]]['used'] == 0:
                        G_reweighted[path[i]][path[i+1]]['distance'] += N*C
            
            #update path
            start = trajet[0]
            end   = trajet[-1]
            path  = nx.astar_path(G_reweighted, source=start, target=end, weight='distance',heuristic=heuristic)

            length = sum(G_reweighted[path[i]][path[i+1]]["distance"] for i in range(len(path)-1))
            shortest_paths[trajet] = (path, length)
            #update the graph
            for i in range(len(path) - 1):
                if G_reweighted[path[i]][path[i+1]]['used'] == 0:
                    G_reweighted[path[i]][path[i+1]]['distance'] -= N*C
                G_reweighted[path[i]][path[i+1]]['used'] += 1
        
        if(total_length == sum(length for _, length in shortest_paths.values())):
            print("converged")
            break
        
        total_length = sum(length for _, length in shortest_paths.values())

    # On utilise list(G_reweighted.edges()) pour éviter la modification en cours d'itération
    for u, v in list(G_reweighted.edges()):
        if G_reweighted[u][v]['used'] == 0:
            G_reweighted.remove_edge(u, v)
    # Remove the used attribute from the graph
    for u, v in G_reweighted.edges():
        del G_reweighted[u][v]['used']
    return G_reweighted, G

