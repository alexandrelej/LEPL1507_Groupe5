from create_random_graphes import create_airport_graph, create_random_subgraph, generate_random_pairs
from visualisation import visualize_graph_on_globe
from A_star import Astar, precompute_shortest_paths

# Chemins vers les fichiers CSV
airports_csv = "../basic_datasets/airports.csv"
routes_csv = "../basic_datasets/pre_existing_routes.csv"

# Créer le graphe complet
airport_graph = create_airport_graph(airports_csv, routes_csv)

# Générer un sous-graphe aléatoire
n = int(input("Nombre de nœuds dans le sous-graphe = "))
m = int(input("Nombre d'arêtes dans le sous-graphe = "))
j = int(input("Nombre de chemins requis (paires de destinations) = "))
C = int(input("Coût C par arête supplémentaire = "))
random_subgraph = create_random_subgraph(airport_graph, n, m)

# Générer j paires de destinations reliées par un chemin
destination_pairs = generate_random_pairs(random_subgraph, j)

# Exécuter A*
G_prime, best_edge_removed, best_cost = Astar(random_subgraph, destination_pairs, C)

# Précalculer les chemins après suppression de l’arête optimale
shortest_paths = precompute_shortest_paths(G_prime, destination_pairs)

# Visualiser le graphe avec les chemins trouvés
visualize_graph_on_globe(G_prime, shortest_paths)




# Afficher des informations sur le sous-graphe et les paires de destinations
print("Sous-graphe aléatoire :A star")
print("Nombre de nœuds :", random_subgraph.number_of_nodes())
print("Nombre d'arêtes :", random_subgraph.number_of_edges())
print("Liste des nœuds :", list(random_subgraph.nodes(data=True)))
print("Liste des arêtes :", list(random_subgraph.edges(data=True)))

# Afficher les paires de destinations
print(f"Paires de destinations (avec chemin) : {destination_pairs}")

# Afficher les résultats de l'optimisation
print("\n=== Résultats de l'A* Optimisé ===")
print("Arête supprimée pour optimisation :", best_edge_removed)
print("Meilleur coût moyen obtenu :", best_cost)
print("Nombre d'arêtes restantes :", G_prime.number_of_edges())
print("Liste des arêtes restantes :", list(G_prime.edges(data=True)))

