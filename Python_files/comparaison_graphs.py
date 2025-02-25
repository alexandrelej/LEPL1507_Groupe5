import time
import matplotlib.pyplot as plt
import numpy as np
from create_random_graphes import create_airport_graph, create_random_subgraph, generate_random_pairs
from visualisation import visualize_graph_on_globe
from A_star import Astar, precompute_shortest_paths
from multiple_astar import approx_multiple_astar
import networkx as nx

# Chemins vers les fichiers CSV
airports_csv = "../basic_datasets/airports.csv"
routes_csv = "../basic_datasets/pre_existing_routes.csv"

# Créer le graphe complet
airport_graph = create_airport_graph(airports_csv, routes_csv)

# Lire les valeurs de n et m depuis l'input sous forme "10 20 30"
n_values = list(map(int, input("Liste des nombres de nœuds (séparés par espace) : ").split()))
m_values = list(map(int, input("Liste des nombres d'arêtes (séparés par espace) : ").split()))
j = int(input("Nombre de chemins requis (paires de destinations) = "))
C_values = list(map(int, input("Liste des différents coûts pour une arête supplémentaire : ").split()))


num_runs = 5  # Nombre d'exécutions pour la moyenne

astar_means_times_nodes = []
multi_astar_means_times_nodes = []
astar_means_costs_nodes = []
multi_astar_means_costs_nodes = []
astar_means_times_edges = []
multi_astar_means_times_edges = []
astar_means_costs_edges = []
multi_astar_means_costs_edges = []

for n, m in zip(n_values, m_values):

    astar_times_nodes = []
    multi_astar_times_nodes = []
    astar_costs_nodes = []
    multi_astar_costs_nodes = []
    astar_times_edges = []
    multi_astar_times_edges = []
    astar_costs_edges = []
    multi_astar_costs_edges = []

    for _ in range(num_runs):
        print(f"\n### Test avec n = {n}, m = {m} ###")

        random_subgraph = create_random_subgraph(airport_graph, n, m)
        destination_pairs = generate_random_pairs(random_subgraph, j)

        start_time = time.time()
        G_prime, edges_removed, best_cost = Astar(random_subgraph, destination_pairs, C_values[0])
        elapsed_time = time.time() - start_time

        print(f"Astar - Coût: {best_cost}, Temps: {elapsed_time:.4f}s")

        astar_times_nodes.append(elapsed_time)
        astar_costs_nodes.append(best_cost)
        astar_times_edges.append(elapsed_time)
        astar_costs_edges.append(best_cost)

        start_time = time.time()
        G_mult, rsubgraph = approx_multiple_astar(random_subgraph, destination_pairs, C_values[0], iterations=30)
        elapsed_time = time.time() - start_time 
        multi_astar_cost = sum([nx.shortest_path_length(G_mult, start, end) for start, end in destination_pairs])/len(destination_pairs) + C_values[0] * len(G_mult.edges())

        print(f"Mult Astar - Coût: {multi_astar_cost}, Temps: {elapsed_time:.4f}s")

        multi_astar_times_nodes.append(elapsed_time)
        multi_astar_costs_nodes.append(multi_astar_cost)
        multi_astar_times_edges.append(elapsed_time)
        multi_astar_costs_edges.append(multi_astar_cost)

    # Calcul des moyennes
    astar_means_times_nodes.append(np.mean(astar_times_nodes))
    astar_means_times_edges.append(np.mean(astar_times_edges))
    multi_astar_means_times_nodes.append(np.mean(multi_astar_times_nodes))
    multi_astar_means_times_edges.append(np.mean(multi_astar_times_edges))
    astar_means_costs_nodes.append(np.mean(astar_costs_nodes))
    astar_means_costs_edges.append(np.mean(astar_costs_edges))
    multi_astar_means_costs_nodes.append(np.mean(multi_astar_costs_nodes))
    multi_astar_means_costs_edges.append(np.mean(multi_astar_costs_edges))


# Tracer les résultats
plt.figure(figsize=(8, 6))

# Graphe du coût en fonction du nombre de nœuds
plt.subplot(2, 2, 1)
plt.plot(n_values, astar_means_costs_nodes, 's-', label="Coût total A*")
plt.plot(n_values, multi_astar_means_costs_nodes, 'o-', label="Coût total Mult A*")
plt.xlabel("Nombre de nœuds")
plt.ylabel("Coût total")
plt.title("Coût en fonction du nombre de nœuds")
plt.legend()
plt.grid()

# Graphe du temps d'exécution en fonction du nombre de nœuds
plt.subplot(2, 2, 2)
plt.plot(n_values, astar_means_times_nodes, 'o-', label="Temps d'exécution A*")
plt.plot(n_values, multi_astar_means_times_nodes, 's-', label="Temps d'exécution Mult A*")
plt.xlabel("Nombre de nœuds")
plt.ylabel("Temps (s)")
plt.title("Temps d'exécution en fonction du nombre de nœuds")
plt.legend()
plt.grid()

# Graphe du coût en fonction du nombre d'arêtes
plt.subplot(2, 2, 3)
plt.plot(m_values, astar_means_costs_edges, 's-', label="Coût total A*")
plt.plot(m_values, multi_astar_means_costs_edges, 'o-', label="Coût total Mult A*")
plt.xlabel("Nombre d'arêtes")
plt.ylabel("Coût total")
plt.title("Coût en fonction du nombre d'arêtes")
plt.legend()
plt.grid()

# Graphe du temps d'exécution en fonction du nombre d'arêtes
plt.subplot(2, 2, 4)
plt.plot(m_values, astar_means_times_edges, 'o-', label="Temps d'exécution A*")
plt.plot(m_values, multi_astar_means_times_edges, 's-', label="Temps d'exécution Mult A*")
plt.xlabel("Nombre d'arêtes")
plt.ylabel("Temps (s)")
plt.title("Temps d'exécution en fonction du nombre d'arêtes")
plt.legend()
plt.grid()

plt.tight_layout()
plt.savefig("comparaison_noeuds_aretes.png")
plt.show()

astar_costs = []
astar_times = []
multi_astar_costs = []
multi_astar_times = []

for C in C_values:
    print(f"\nTest avec C = {C}")

    start_time = time.time()
    G_prime, edges_removed, best_cost = Astar(random_subgraph, destination_pairs, C)
    astar_time = time.time() - start_time
    astar_costs.append(best_cost)
    astar_times.append(astar_time)

    print(f"Astar - Coût: {best_cost}, Temps: {astar_time:.4f}s")

    start_time = time.time()
    G_mult, rsubgraph = approx_multiple_astar(random_subgraph, destination_pairs, C, iterations=30)
    multi_astar_time = time.time() - start_time
    multi_astar_cost = sum([nx.shortest_path_length(G_mult, start, end) for start, end in destination_pairs])/len(destination_pairs) + C * len(G_mult.edges())
    multi_astar_costs.append(multi_astar_cost)
    multi_astar_times.append(multi_astar_time)

    print(f"Mult Astar - Coût: {multi_astar_cost}, Temps: {multi_astar_time:.4f}s")

plt.figure(figsize=(8, 6))

# Comparaison des coûts
plt.subplot(2, 1, 1)
plt.plot(C_values, astar_costs, 'o-', label="A*")
plt.plot(C_values, multi_astar_costs, 's-', label="Mult A*")
plt.xlabel("C (Coût par arête)")
plt.ylabel("Coût total")
plt.title("Comparaison des coûts")
plt.legend()
plt.grid()

# Comparaison des temps d'exécution
plt.subplot(2, 1, 2)
plt.plot(C_values, astar_times, 'o-', label="A*")
plt.plot(C_values, multi_astar_times, 's-', label="Mult A*")
plt.xlabel("C (Coût par arête)")
plt.ylabel("Temps d'exécution (s)")
plt.title("Comparaison des temps d'exécution")
plt.legend()
plt.grid()

plt.tight_layout()
plt.savefig("resultats.png")
plt.show()
