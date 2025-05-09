import time
import matplotlib.pyplot as plt
import numpy as np
from create_graphs import create_airport_graph, create_random_subgraph, generate_random_pairs
from create_graphs import add_prices, add_times, graph_to_json_file
from update_costs import Update_costs
from disturbance_result import test_disturbance, multi_optimize_and_disturb
import networkx as nx
import copy 



debug = False
# Chemins vers les fichiers CSV
airports_csv = "../basic_datasets/airports.csv"
routes_csv = "../basic_datasets/pre_existing_routes.csv"

# Créer le graphe complet
airport_graph = create_airport_graph(airports_csv, routes_csv)

"""
# Lire les valeurs de n et m depuis l'input sous forme "10 20 30"
n_values = list(map(int, input("Liste des nombres de nœuds (séparés par espace) : ").split()))
m_values = list(map(int, input("Liste des nombres d'arêtes (séparés par espace) : ").split()))
j = int(input("Nombre de chemins requis (paires de destinations) = "))
C_values = list(map(int, input("Liste des différentes coûts pour une arête supplémentaire : ").split()))
"""
n_values = [40]
m_values = [150]
j = 10
C_values = [4000]


remove_edges_costs = []
update_costs_costs = []
remove_edges_times = []
update_costs_times = []

# Boucler sur différentes tailles de sous-graphes
for n, m in zip(n_values, m_values):
    print(f"\n### Test avec n = {n}, m = {m} ###")

    # Générer un sous-graphe aléatoire
    random_subgraph = create_random_subgraph(airport_graph, n, m)
    destination_pairs = generate_random_pairs(random_subgraph, j)

    # --- Code utilisant Remove_edges (anciennement A_star) mis en commentaire ---
    # if n == n_values[0] and m == m_values[0]:  # Visualisation seulement pour la première itération
    #     C = C_values[0]  # On prend la première valeur de C pour la visualisation
    #     G_prime, best_edge_removed, best_cost = remove_edges(random_subgraph, destination_pairs, C)
    #     shortest_paths = precompute_shortest_paths(G_prime, destination_pairs)
    #     visualize_graph_on_globe(random_subgraph, shortest_paths)
    #     print("\n=== Résultats de remove_edges Optimisé ===")
    #     print("Arête supprimée pour optimisation :", best_edge_removed)
    #     print("Meilleur coût moyen obtenu :", best_cost)
    #     print("Nombre d'arêtes restantes :", G_prime.number_of_edges())
    #     print("Liste des arêtes restantes :", list(G_prime.edges(data=True)))

    # Boucle sur différentes valeurs de C
    for C in C_values:
        print(f"\nTest avec C = {C}")

        # --- Code utilisant remove_edges mis en commentaire ---
        # start_time = time.time()
        # G_prime, best_edge_removed, best_cost = remove_edges(random_subgraph, destination_pairs, C)
        # remove_edges_time = time.time() - start_time
        # remove_edges_costs.append(best_cost)
        # remove_edges_times.append(remove_edges_time)
        # print(f"remove_edges - Coût: {best_cost}, Temps: {remove_edges_time:.4f}s")

        # Exécuter update_costs
        start_time = time.time()
        G_reweighted, rsubgraph = Update_costs(random_subgraph, destination_pairs, C, iterations=min(n, m))
        
        # Obtenir le graphe avec les prix et les temps
        G_all = copy.deepcopy(G_reweighted)
        add_prices(G_all, "../basic_datasets/prices.csv")
        add_times(G_all, "../basic_datasets/waiting_times.csv", average_speed=800)
        graph_to_json_file(G_all, "../json/G_all.json")

        update_costs_time = time.time() - start_time
        update_costs_cost = sum([nx.shortest_path_length(G_reweighted, start, end) for start, end in destination_pairs]) / len(destination_pairs) + C * len(G_reweighted.edges())
        update_costs_costs.append(update_costs_cost)
        update_costs_times.append(update_costs_time)

        print(f"Update costs - Coût: {update_costs_cost}, Temps: {update_costs_time:.4f}s")

        # Appel de visualize_graph_on_globe pour la première itération et pour la première valeur de C
        if n == n_values[0] and C == C_values[0]:
            # Calculer les plus courts chemins pour la visualisation
            shortest_paths = {}
            for start, end in destination_pairs:
                try:
                    path = nx.shortest_path(G_reweighted, start, end)
                    length = nx.shortest_path_length(G_reweighted, start, end)
                except nx.NetworkXNoPath:
                    path = []
                    length = float('inf')
                shortest_paths[(start, end)] = (path, length)
            #visualize_graph_on_globe(random_subgraph, shortest_paths)

# Tracer les résultats
plt.figure(figsize=(12, 5))

# Comparaison des coûts
plt.subplot(1, 2, 1)
# plt.plot(remove_edges_costs, 'o-', label="remove_edges")   # Code remove_edges mis en commentaire
plt.plot(update_costs_costs, 's-', label="Update costs")
plt.xlabel("C (Coût par arête)")
plt.ylabel("Coût total")
plt.title("Comparaison des coûts")
plt.legend()
plt.grid()

# Comparaison des temps d'exécution
plt.subplot(1, 2, 2)
# plt.plot(np.arange(len(remove_edges_costs)), remove_edges_times, 'o-', label="remove_edges")
plt.plot(np.arange(len(update_costs_times)), update_costs_times, 's-', label="Update costs")
plt.xlabel("C (Coût par arête)")
plt.ylabel("Temps d'exécution (s)")
plt.title("Comparaison des temps d'exécution")
plt.legend()
plt.grid()

plt.tight_layout()
plt.savefig("../graphs/resultats.png")  # Enregistre le graphique dans un fichier


test_disturbance(G_reweighted,random_subgraph,destination_pairs,C)

multi_optimize_and_disturb(random_subgraph,destination_pairs, C)