import create_random_graph as crg
import networkx as nx

# Charger le graphe
G = crg.create_airport_graph("../basic_datasets/airports.csv", "../basic_datasets/pre_existing_routes.csv")


def precompute_shortest_paths(G, J):
    """Pré-calcule les plus courts chemins pour tous les trajets dans J et stocke les résultats."""
    return {
        (s, t): (path := nx.astar_path(G, s, t, weight="weight"), 
                 sum(G[path[i]][path[i+1]]["weight"] for i in range(len(path)-1)))
        for s, t in J
    }

def update_shortest_paths(G, J, shortest_paths, removed_edge):
    """Met à jour uniquement les trajets impactés après suppression d'une arête."""
    u, v = removed_edge
    updated_paths = shortest_paths.copy()  # Copie pour ne pas modifier l'original
    for (s, t) in J:
        path, _ = shortest_paths[(s, t)]
        if (u, v) in zip(path, path[1:]) or (v, u) in zip(path, path[1:]):  # Si l'arête supprimée est utilisée
            try:
                new_path = nx.astar_path(G, s, t, weight="weight")
                new_length = sum(G[new_path[i]][new_path[i+1]]["weight"] for i in range(len(new_path)-1))
                updated_paths[(s, t)] = (new_path, new_length)
            except nx.NetworkXNoPath:
                updated_paths[(s, t)] = (None, float("inf"))  # Impossible d'atteindre t depuis s
    return updated_paths

def Algo(G, J, C):
    G_prime = G.copy()
    shortest_paths = precompute_shortest_paths(G_prime, J)  # On pré-calcule tout

    # Stocker les coûts pour chaque arête supprimée
    edge_costs = {}

    for u, v in list(G_prime.edges()):
        G_prime.remove_edge(u, v)  # Supprime une arête temporairement
        updated_paths = update_shortest_paths(G_prime, J, shortest_paths, (u, v))  # Mise à jour des trajets impactés

        # Calcul du nouveau coût total
        current_cost = sum(length for _, length in updated_paths.values()) + C * (len(G_prime.edges()))
        edge_costs[(u, v)] = current_cost  # Stocker le coût

        G_prime.add_edge(u, v, weight=G[u][v]["weight"])  # Remettre l'arête

    # Trouver l'arête qui minimise le coût
    best_edge_to_remove = min(edge_costs, key=edge_costs.get)
    
    # Supprimer définitivement la meilleure arête
    G_prime.remove_edge(*best_edge_to_remove)

    return G_prime, best_edge_to_remove, edge_costs[best_edge_to_remove]




# Appliquer l’algorithme
optimized_G = Algo(sub_G, J)

# Vérifier le résultat
print("Optimisation terminée :")
print("Nombre d'arêtes après optimisation :", optimized_G.number_of_edges())
