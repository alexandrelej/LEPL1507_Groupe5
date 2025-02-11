import create_random_graph as crg
import networkx as nx

# Charger le graphe
G = crg.create_airport_graph("../basic_datasets/airports.csv", "../basic_datasets/pre_existing_routes.csv")

print("Nombre de nœuds :", G.number_of_nodes())
print("Nombre d'arêtes :", G.number_of_edges())

n, m = 10, 15
sub_G = crg.create_random_subgraph(G, n, m)

print("Sous-graphe créé avec", sub_G.number_of_nodes(), "nœuds et", sub_G.number_of_edges(), "arêtes")

def Algo(G, J):
    C = 1000  # Pénalité pour le nombre d’arêtes
    G_prime = G.copy()  #  On crée une copie du graphe pour ne pas modifier l’original

    initial_cost = sum(nx.shortest_path_length(G_prime, s, t, weight="weight") for s, t in J) / J + C * len(G_prime.edges)

    for u, v in list(G_prime.edges()):
        G_prime.remove_edge(u, v)  # Supprime une arête
        
        try:
            #  Recalculer le coût après suppression
            new_cost = sum(nx.shortest_path_length(G_prime, s, t, weight="weight") for s, t in J) + C * len(G_prime.edges)
            
            #  Si le coût est pire, on remet l’arête
            if new_cost > initial_cost:
                G_prime.add_edge(u, v, weight=G[u][v]["weight"])
            else:
                initial_cost = new_cost  # Mettre à jour le coût si c’est une amélioration
                
        except nx.NetworkXNoPath:
            #  Si une route devient impossible, on remet l’arête
            G_prime.add_edge(u, v, weight=G[u][v]["weight"])

    return G_prime

# Exemple de J (il faut donner des paires de nœuds)
J = [(1, 2), (3, 4), (5, 6)]  # Remplace avec de vrais nœuds

# Appliquer l’algorithme
optimized_G = Algo(sub_G, J)

# Vérifier le résultat
print("Optimisation terminée :")
print("Nombre d'arêtes après optimisation :", optimized_G.number_of_edges())
