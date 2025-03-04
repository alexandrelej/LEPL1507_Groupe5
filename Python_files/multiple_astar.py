import networkx as nx
import numpy as np
import time
import random
from create_graphe import haversine
def generate_order(G: nx.DiGraph, Trajets: list[tuple[str, str]], mode = "random") -> list[tuple[str, str]]:
    """
    Generate an order for the trajectories
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

def approx_multiple_astar(G: nx.DiGraph, Trajets: list[tuple[str, str]], C: float,iterations : int =1) -> nx.DiGraph:
    def heuristic(u, v):
        return haversine(G.nodes[u]["latitude"], G.nodes[u]["longitude"], G.nodes[v]["latitude"], G.nodes[v]["longitude"])
    """
    Approximate the optimal solution by iteratively doing A* on the graph.
    """
    G_reweighted = G.copy()
    N = len(Trajets)
    nx.set_edge_attributes(G_reweighted, 0, "used")
    for edge in G_reweighted.edges():
        G_reweighted.edges[edge]['distance'] += N*C
    
    shortest_paths = {}
    total_length = 0
    for it in range(iterations):
        #print("iteration", it)
        #print(shortest_paths)
        
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
        if(total_length ==sum(length for _, length in shortest_paths.values())):break
        total_length = sum(length for _, length in shortest_paths.values())
    # On utilise list(G_reweighted.edges()) pour éviter la modification en cours d'itération
    for u, v in list(G_reweighted.edges()):
        if G_reweighted[u][v]['used'] == 0:
            G_reweighted.remove_edge(u, v)
    
    return G_reweighted, G

