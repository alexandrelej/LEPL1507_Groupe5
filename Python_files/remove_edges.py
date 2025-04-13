import networkx as nx
from create_graphe import haversine

def precompute_shortest_paths(G, J):
    def heuristic(u, v):
        return haversine(G.nodes[u]["latitude"], G.nodes[u]["longitude"], G.nodes[v]["latitude"], G.nodes[v]["longitude"])
    """Pré-calcule les plus courts chemins et leurs coûts pour chaque paire de J."""
    shortest_paths = {}
    for s, t in J:
        try:
            path = nx.astar_path(G, s, t, weight="distance", heuristic=heuristic)
            length = sum(G[path[i]][path[i+1]]["distance"] for i in range(len(path)-1))
            shortest_paths[(s, t)] = (path, length)
        except nx.NetworkXNoPath:
            shortest_paths[(s, t)] = (None, float("inf"))  # Pas de chemin disponible
    return shortest_paths

def compute_average_cost(G, shortest_paths, C):
    """Calcule la moyenne des coûts des trajets."""
    total_cost = sum(length for _, length in shortest_paths.values())/len(shortest_paths) + C * G.number_of_edges()
    return total_cost

def update_shortest_paths(G, J, shortest_paths, removed_edge):
    def heuristic(u, v):
        return haversine(G.nodes[u]["latitude"], G.nodes[u]["longitude"], G.nodes[v]["latitude"], G.nodes[v]["longitude"])
    """Met à jour uniquement les trajets impactés après suppression d'une arête."""
    u, v = removed_edge
    updated_paths = shortest_paths.copy()

    for (s, t) in J:
        path, _ = shortest_paths[(s, t)]
        if path is not None and (u, v) in zip(path, path[1:]):  # Si l'arête supprimée est utilisée
            try:
                new_path = nx.astar_path(G, s, t, weight="distance", heuristic=heuristic)
                new_length = sum(G[new_path[i]][new_path[i+1]]["distance"] for i in range(len(new_path)-1))
                updated_paths[(s, t)] = (new_path, new_length)
            except nx.NetworkXNoPath:
                return None  # Impossible de connecter tous les trajets → annuler la suppression
    return updated_paths

def Remove_edges(G, J, C):
    """Optimise le graphe en supprimant les arêtes qui réduisent la moyenne des coûts tout en gardant les trajets possibles."""
    G_prime = G.copy()
    shortest_paths = precompute_shortest_paths(G_prime, J)

    best_avg_cost = compute_average_cost(G_prime, shortest_paths, C)
    removed_edges = []

    while True:
        edge_costs = {}
        
        for u, v in list(G_prime.edges()):
            G_prime.remove_edge(u, v)  # Suppression temporaire
            updated_paths = update_shortest_paths(G_prime, J, shortest_paths, (u, v))
            
            if updated_paths is not None:  # Vérifier que tous les trajets restent possibles
                new_avg_cost = compute_average_cost(G_prime, updated_paths, C)
                edge_costs[(u, v)] = new_avg_cost
            
            G_prime.add_edge(u, v, distance=G[u][v]["distance"])  # Remettre l'arête temporairement
        
        if not edge_costs:
            break  # Arrêter si aucune arête ne peut être supprimée sans casser la connectivité
        
        # Trouver l’arête qui réduit le plus la moyenne des coûts
        best_edge = min(edge_costs, key=edge_costs.get)
        new_avg_cost = edge_costs[best_edge]

        # Vérifier si la suppression réduit encore la moyenne
        if new_avg_cost >= best_avg_cost:
            break  # Stop si aucune suppression n'améliore la situation

        # Supprimer définitivement la meilleure arête
        G_prime.remove_edge(*best_edge)
        removed_edges.append(best_edge)
        shortest_paths = update_shortest_paths(G_prime, J, shortest_paths, best_edge)
        best_avg_cost = new_avg_cost

    return G_prime, removed_edges, best_avg_cost
