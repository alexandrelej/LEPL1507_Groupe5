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
        order = []
        for Trajet in Trajets:
            start = Trajet[0]
            end = Trajet[1]
            shortest_path = nx.shortest_path(G, source=start, target=end, weight='distance')
            order.append((shortest_path, Trajet))
        return order

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
    
    for i in range(iterations):
        for trajet in generate_order(G, Trajets, mode="random"):
            
            if i > 0:
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
    
    # On utilise list(G_reweighted.edges()) pour éviter la modification en cours d'itération
    for u, v in list(G_reweighted.edges()):
        if G_reweighted[u][v]['used'] == 0:
            G_reweighted.remove_edge(u, v)
            print(f"Removed edge {u} -> {v}")
    print(f"Total distance: {sum}")
    print(f"Total cost: {C * len(G_reweighted.edges())}")
    print(f"objective function value: {sum/len(Trajets)/N + C * len(G_reweighted.edges())}")
    print(f"Number of edges: {len(G_reweighted.edges())}")
    return G_reweighted, G

