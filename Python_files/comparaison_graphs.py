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

# Paramètres fixes
j = 15  # Nombre de paires de destinations
C_values = [2000]  # Coût d'ajout d'une arête supplémentaire
num_runs = 10  # Nombre d'exécutions pour la moyenne

# Comparaison en fonction du nombre de nœuds avec un nombre d'arêtes fixe
n_values = [10, 20, 30, 40, 50, 60, 70] # il y a 75 aéroports dans le fichier csv
m_fixed = 40  # Nombre d'arêtes constant

astar_means_times_nodes = []
multi_astar_means_times_nodes = []
astar_means_costs_nodes = []
multi_astar_means_costs_nodes = []

for n in n_values:
    astar_times = []
    multi_astar_times = []
    astar_costs = []
    multi_astar_costs = []

    print("\n### Test avec n =", n)

    for _ in range(num_runs):
        random_subgraph = create_random_subgraph(airport_graph, n, m_fixed)
        destination_pairs = generate_random_pairs(random_subgraph, j)

        start_time = time.time()
        G_prime, edges_removed, best_cost = Astar(random_subgraph, destination_pairs, C_values[0])
        elapsed_time = time.time() - start_time

        astar_times.append(elapsed_time)
        astar_costs.append(best_cost)

        start_time = time.time()
        G_mult, rsubgraph = approx_multiple_astar(random_subgraph, destination_pairs, C_values[0], iterations=30)
        elapsed_time = time.time() - start_time 
        multi_astar_cost = sum([nx.shortest_path_length(G_mult, start, end) for start, end in destination_pairs]) / len(destination_pairs) + C_values[0] * len(G_mult.edges())

        multi_astar_times.append(elapsed_time)
        multi_astar_costs.append(multi_astar_cost)

    astar_means_times_nodes.append(np.mean(astar_times))
    multi_astar_means_times_nodes.append(np.mean(multi_astar_times))
    astar_means_costs_nodes.append(np.mean(astar_costs))
    multi_astar_means_costs_nodes.append(np.mean(multi_astar_costs))

# Comparaison en fonction du nombre d'arêtes avec un nombre de nœuds fixe
m_values = [100, 120, 140, 160, 180, 200]
n_fixed = 50  # Nombre de nœuds constant

astar_means_times_edges = []
multi_astar_means_times_edges = []
astar_means_costs_edges = []
multi_astar_means_costs_edges = []

for m in m_values:
    astar_times = []
    multi_astar_times = []
    astar_costs = []
    multi_astar_costs = []

    print("\n### Test avec m =", m)

    for _ in range(num_runs):
        random_subgraph = create_random_subgraph(airport_graph, n_fixed, m)
        destination_pairs = generate_random_pairs(random_subgraph, j)

        start_time = time.time()
        G_prime, edges_removed, best_cost = Astar(random_subgraph, destination_pairs, C_values[0])
        elapsed_time = time.time() - start_time

        astar_times.append(elapsed_time)
        astar_costs.append(best_cost)

        start_time = time.time()
        G_mult, rsubgraph = approx_multiple_astar(random_subgraph, destination_pairs, C_values[0], iterations=30)
        elapsed_time = time.time() - start_time 
        multi_astar_cost = sum([nx.shortest_path_length(G_mult, start, end) for start, end in destination_pairs]) / len(destination_pairs) + C_values[0] * len(G_mult.edges())

        multi_astar_times.append(elapsed_time)
        multi_astar_costs.append(multi_astar_cost)

    astar_means_times_edges.append(np.mean(astar_times))
    multi_astar_means_times_edges.append(np.mean(multi_astar_times))
    astar_means_costs_edges.append(np.mean(astar_costs))
    multi_astar_means_costs_edges.append(np.mean(multi_astar_costs))



# Comparaison en fonction du nombre de trajets requis
j_values = [5, 10, 15, 20, 25, 30]
m_fixed = 150  # Nombre d'arêtes constant
n_fixed = 50  # Nombre de nœuds constant

astar_means_times_j = []
multi_astar_means_times_j = []
astar_means_costs_j = []
multi_astar_means_costs_j = []

for j in j_values:
    astar_times = []
    multi_astar_times = []
    astar_costs = []
    multi_astar_costs = []

    print("\n### Test avec j =", j)

    for _ in range(num_runs):
        random_subgraph = create_random_subgraph(airport_graph, n_fixed, m_fixed)
        destination_pairs = generate_random_pairs(random_subgraph, j)

        start_time = time.time()
        G_prime, edges_removed, best_cost = Astar(random_subgraph, destination_pairs, C_values[0])
        elapsed_time = time.time() - start_time

        astar_times.append(elapsed_time)
        astar_costs.append(best_cost)

        start_time = time.time()
        G_mult, rsubgraph = approx_multiple_astar(random_subgraph, destination_pairs, C_values[0], iterations=30)
        elapsed_time = time.time() - start_time 
        multi_astar_cost = sum([nx.shortest_path_length(G_mult, start, end) for start, end in destination_pairs]) / len(destination_pairs) + C_values[0] * len(G_mult.edges())

        multi_astar_times.append(elapsed_time)
        multi_astar_costs.append(multi_astar_cost)

    astar_means_times_j.append(np.mean(astar_times))
    multi_astar_means_times_j.append(np.mean(multi_astar_times))
    astar_means_costs_j.append(np.mean(astar_costs))
    multi_astar_means_costs_j.append(np.mean(multi_astar_costs))


# Tracé des résultats
plt.figure(figsize=(10, 8))

# Coût en fonction du nombre de nœuds
plt.subplot(2, 2, 1)
plt.plot(n_values, astar_means_costs_nodes, 's-', label="Coût total A*")
plt.plot(n_values, multi_astar_means_costs_nodes, 'o-', label="Coût total Mult A*")
plt.xlabel("Nombre de nœuds")
plt.ylabel("Coût total")
plt.title("Coût en fonction du nombre de nœuds")
plt.legend()
plt.grid()

# Temps d'exécution en fonction du nombre de nœuds
plt.subplot(2, 2, 2)
plt.plot(n_values, astar_means_times_nodes, 'o-', label="Temps A*")
plt.plot(n_values, multi_astar_means_times_nodes, 's-', label="Temps Mult A*")
plt.xlabel("Nombre de nœuds")
plt.ylabel("Temps (s)")
plt.title("Temps d'exécution en fonction du nombre de nœuds")
plt.legend()
plt.grid()

# Coût en fonction du nombre d'arêtes
plt.subplot(2, 2, 3)
plt.plot(m_values, astar_means_costs_edges, 's-', label="Coût total A*")
plt.plot(m_values, multi_astar_means_costs_edges, 'o-', label="Coût total Mult A*")
plt.xlabel("Nombre d'arêtes")
plt.ylabel("Coût total")
plt.title("Coût en fonction du nombre d'arêtes")
plt.legend()
plt.grid()

# Temps d'exécution en fonction du nombre d'arêtes
plt.subplot(2, 2, 4)
plt.plot(m_values, astar_means_times_edges, 'o-', label="Temps A*")
plt.plot(m_values, multi_astar_means_times_edges, 's-', label="Temps Mult A*")
plt.xlabel("Nombre d'arêtes")
plt.ylabel("Temps (s)")
plt.title("Temps d'exécution en fonction du nombre d'arêtes")
plt.legend()
plt.grid()

plt.tight_layout()
plt.savefig("comparaison_noeuds_aretes.png")
plt.show()

# Tracé des résultats
plt.figure(figsize=(10, 8))

# Coût en fonction du nombre de trajets
plt.subplot(2, 1, 1)
plt.plot(j_values, astar_means_costs_j, 's-', label="Coût total A*")
plt.plot(j_values, multi_astar_means_costs_j, 'o-', label="Coût total Mult A*")
plt.xlabel("Nombre de trajets")
plt.ylabel("Coût total")
plt.title("Coût en fonction du nombre de trajets")
plt.legend()
plt.grid()

# Temps d'exécution en fonction du nombre de trajets    
plt.subplot(2, 1, 2)
plt.plot(j_values, astar_means_times_j, 'o-', label="Temps A*")
plt.plot(j_values, multi_astar_means_times_j, 's-', label="Temps Mult A*")
plt.xlabel("Nombre de trajets")
plt.ylabel("Temps (s)")
plt.title("Temps d'exécution en fonction du nombre de trajets")
plt.legend()
plt.grid()

plt.tight_layout()
plt.savefig("comparaison_#trajets.png")
plt.show()


# Comparaison des coûts et des temps d'exécution pour différentes valeurs de C

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

plt.figure(figsize=(10, 8))

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
plt.savefig("comparaison_C.png")
plt.show()
