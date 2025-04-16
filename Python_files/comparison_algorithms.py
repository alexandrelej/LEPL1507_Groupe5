import time
import matplotlib.pyplot as plt
import numpy as np
from create_graphs import create_airport_graph, create_random_subgraph, generate_random_pairs
from remove_edges import Remove_edges
from update_costs import Update_costs
import networkx as nx

# Chemins vers les fichiers CSV
airports_csv = "../basic_datasets/airports.csv"
routes_csv = "../basic_datasets/pre_existing_routes.csv"

# Créer le graphe complet
airport_graph = create_airport_graph(airports_csv, routes_csv)

# Paramètres fixes
j = 20  # Nombre de paires de destinations
C = 2000  # Coût d'ajout d'une arête supplémentaire
num_runs = 5  # Nombre d'exécutions pour la moyenne



# Comparaison en fonction du nombre de nœuds avec un nombre d'arêtes fixe
n_values = [10, 20, 30, 40, 50, 60, 70, 75] # il y a 75 aéroports dans le fichier csv
m_fixed = 40  # Nombre d'arêtes constant

remove_edges_means_times_nodes = []
update_costs_means_times_nodes = []
remove_edges_means_costs_nodes = []
update_costs_means_costs_nodes = []

for n in n_values:
    remove_edges_times = []
    update_costs_times = []
    remove_edges_costs = []
    update_costs_costs = []

    print("\n### Test avec n =", n)

    for _ in range(num_runs):
        random_subgraph = create_random_subgraph(airport_graph, n, m_fixed)
        destination_pairs = generate_random_pairs(random_subgraph, j)

        start_time = time.time()
        G_prime, edges_removed, best_cost = Remove_edges(random_subgraph, destination_pairs, C)
        elapsed_time = time.time() - start_time

        remove_edges_times.append(elapsed_time)
        remove_edges_costs.append(best_cost)

        start_time = time.time()
        G_reweighted, rsubgraph = Update_costs(random_subgraph, destination_pairs, C, iterations=30)
        elapsed_time = time.time() - start_time 
        update_costs_cost = sum([nx.shortest_path_length(G_reweighted, start, end) for start, end in destination_pairs]) / len(destination_pairs) + C * len(G_reweighted.edges())

        update_costs_times.append(elapsed_time)
        update_costs_costs.append(update_costs_cost)

    remove_edges_means_times_nodes.append(np.mean(remove_edges_times))
    update_costs_means_times_nodes.append(np.mean(update_costs_times))
    remove_edges_means_costs_nodes.append(np.mean(remove_edges_costs))
    update_costs_means_costs_nodes.append(np.mean(update_costs_costs))


# Comparaison en fonction du nombre d'arêtes avec un nombre de nœuds fixe
m_values = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500] # il y a 1791 arêtes dans le fichier csv
n_fixed = 75  # Nombre de nœuds constant

remove_edges_means_times_edges = []
update_costs_means_times_edges = []
remove_edges_means_costs_edges = []
update_costs_means_costs_edges = []

for m in m_values:
    remove_edges_times = []
    update_costs_times = []
    remove_edges_costs = []
    update_costs_costs = []

    print("\n### Test avec m =", m)

    for _ in range(num_runs):
        random_subgraph = create_random_subgraph(airport_graph, n_fixed, m)
        destination_pairs = generate_random_pairs(random_subgraph, j)

        start_time = time.time()
        G_prime, edges_removed, best_cost = Remove_edges(random_subgraph, destination_pairs, C)
        elapsed_time = time.time() - start_time

        remove_edges_times.append(elapsed_time)
        remove_edges_costs.append(best_cost)

        start_time = time.time()
        G_reweighted, rsubgraph = Update_costs(random_subgraph, destination_pairs, C, iterations=30)
        elapsed_time = time.time() - start_time 
        update_costs_cost = sum([nx.shortest_path_length(G_reweighted, start, end) for start, end in destination_pairs]) / len(destination_pairs) + C * len(G_reweighted.edges())

        update_costs_times.append(elapsed_time)
        update_costs_costs.append(update_costs_cost)

    remove_edges_means_times_edges.append(np.mean(remove_edges_times))
    update_costs_means_times_edges.append(np.mean(update_costs_times))
    remove_edges_means_costs_edges.append(np.mean(remove_edges_costs))
    update_costs_means_costs_edges.append(np.mean(update_costs_costs))



# Comparaison en fonction du nombre de trajets requis
j_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100] 
m_fixed_for_j = 100  # Nombre d'arêtes constant
n_fixed_for_j = 50  # Nombre de nœuds constant

remove_edges_means_times_j = []
update_costs_means_times_j = []
remove_edges_means_costs_j = []
update_costs_means_costs_j = []

for j in j_values:
    remove_edges_times = []
    update_costs_times = []
    remove_edges_costs = []
    update_costs_costs = []

    print("\n### Test avec j =", j)

    for _ in range(num_runs):
        random_subgraph = create_random_subgraph(airport_graph, n_fixed_for_j, m_fixed_for_j)
        destination_pairs = generate_random_pairs(random_subgraph, j)

        start_time = time.time()
        G_prime, edges_removed, best_cost = Remove_edges(random_subgraph, destination_pairs, C)
        elapsed_time = time.time() - start_time

        remove_edges_times.append(elapsed_time)
        print("Remove_edges time",elapsed_time)
        remove_edges_costs.append(best_cost)
        print("Remove_edges cost",best_cost)
        print("Nombre de vols restants",len(G_prime.edges()))

        start_time = time.time()
        G_reweighted, rsubgraph = Update_costs(random_subgraph, destination_pairs, C, iterations=30)
        elapsed_time = time.time() - start_time 
        update_costs_cost = sum([nx.shortest_path_length(G_reweighted, start, end) for start, end in destination_pairs]) / len(destination_pairs) + C_values[0] * len(G_reweighted.edges())

        update_costs_times.append(elapsed_time)
        print("Update costs time",elapsed_time)
        update_costs_costs.append(update_costs_cost)
        print("Update costs cost",update_costs_cost)

    remove_edges_means_times_j.append(np.mean(remove_edges_times))
    update_costs_means_times_j.append(np.mean(update_costs_times))
    remove_edges_means_costs_j.append(np.mean(remove_edges_costs))
    update_costs_means_costs_j.append(np.mean(update_costs_costs))


# Comparaison en fonction du cout C
C_values = [500, 1000, 1500, 2000, 2500]
m_fixed_for_C = 100  # Nombre d'arêtes constant
n_fixed_for_C = 50  # Nombre de nœuds constant

remove_edges_means_times_C = []
update_costs_means_times_C = []
remove_edges_means_costs_C = []
update_costs_means_costs_C = []

for c in C_values:
    remove_edges_times = []
    update_costs_times = []
    remove_edges_costs = []
    update_costs_costs = []

    print("\n### Test avec C =", c)

    for _ in range(num_runs):
        random_subgraph = create_random_subgraph(airport_graph, n_fixed_for_C, m_fixed_for_C)
        destination_pairs = generate_random_pairs(random_subgraph, j)

        start_time = time.time()
        G_prime, edges_removed, best_cost = Remove_edges(random_subgraph, destination_pairs, c)
        elapsed_time = time.time() - start_time

        remove_edges_times.append(elapsed_time)
        print("Remove_edges time",elapsed_time)
        remove_edges_costs.append(best_cost)
        print("Remove_edges cost",best_cost)
        print("Nombre de vols restants",len(G_prime.edges()))

        start_time = time.time()
        G_reweighted, rsubgraph = Update_costs(random_subgraph, destination_pairs, c, iterations=30)
        elapsed_time = time.time() - start_time 
        update_costs_cost = sum([nx.shortest_path_length(G_reweighted, start, end) for start, end in destination_pairs]) / len(destination_pairs) + c * len(G_reweighted.edges())

        update_costs_times.append(elapsed_time)
        print("Update costs time",elapsed_time)
        update_costs_costs.append(update_costs_cost)
        print("Update costs cost",update_costs_cost)

    remove_edges_means_times_j.append(np.mean(remove_edges_times))
    update_costs_means_times_j.append(np.mean(update_costs_times))
    remove_edges_means_costs_j.append(np.mean(remove_edges_costs))
    update_costs_means_costs_j.append(np.mean(update_costs_costs))



###### Tracé des résultats en fonction du nombre de nœuds et d'arêtes #####
plt.figure(figsize=(10, 8))

# Coût en fonction du nombre de nœuds
plt.subplot(2, 2, 1)
plt.plot(n_values, remove_edges_means_costs_nodes, 's-', label="Algorithme Remove edges")
plt.plot(n_values, update_costs_means_costs_nodes, 'o-', label="Algorithme Update costs")
plt.xlabel("Nombre de nœuds")
plt.ylabel("Coût total du réseau")
plt.title("Coût du réseau en fonction du nombre de nœuds")
plt.legend()
plt.grid()
info_text = "Paramètres fixes :\n- |E| = {m_fixed}\n- |J| = {j}\n- C = {C}".format(m_fixed=m_fixed, j=j, C=C)
plt.annotate(info_text, xy=(0.05, 0.95), xycoords='axes fraction',
             fontsize=10, bbox=dict(boxstyle="round", facecolor="white", alpha=0.5),
             verticalalignment='top', horizontalalignment='left')



# Temps d'exécution en fonction du nombre de nœuds
plt.subplot(2, 2, 2)
plt.plot(n_values, remove_edges_means_times_nodes, 'o-', label="Algorithme Remove edges")
plt.plot(n_values, update_costs_means_times_nodes, 's-', label="Algorithme Update costs")
plt.xlabel("Nombre de nœuds")
plt.ylabel("Temps d'exécution (s)")
plt.title("Temps d'exécution en fonction du nombre de nœuds")
plt.legend()
plt.grid()
info_text = "Paramètres fixes :\n- |E| = {m_fixed}\n- |J| = {j}\n- C = {C}".format(m_fixed=m_fixed, j=j, C=C)
plt.annotate(info_text, xy=(0.05, 0.05), xycoords='axes fraction',
             fontsize=10, bbox=dict(boxstyle="round", facecolor="white", alpha=0.5))


# Coût en fonction du nombre d'arêtes
plt.subplot(2, 2, 3)
plt.plot(m_values, remove_edges_means_costs_edges, 's-', label="Algorithme Remove edges")
plt.plot(m_values, update_costs_means_costs_edges, 'o-', label="Algorithme Update costs")
plt.xlabel("Nombre d'arêtes")
plt.ylabel("Coût total du réseau")
plt.title("Coût total du réseau en fonction du nombre d'arêtes")
plt.legend()
plt.grid()
info_text = "Paramètres fixes :\n- |V| = {n_fixed}\n- |J| = {j}\n- C = {C}".format(n_fixed=n_fixed, j=j, C=C)
plt.annotate(info_text, xy=(0.05, 0.05), xycoords='axes fraction',
             fontsize=10, bbox=dict(boxstyle="round", facecolor="white", alpha=0.5))


# Temps d'exécution en fonction du nombre d'arêtes
plt.subplot(2, 2, 4)
plt.plot(m_values, remove_edges_means_times_edges, 'o-', label="Algorithme Remove edges")
plt.plot(m_values, update_costs_means_times_edges, 's-', label="Algorithme Update costs")
plt.xlabel("Nombre d'arêtes")
plt.ylabel("Temps d'exécution (s)")
plt.title("Temps d'exécution en fonction du nombre d'arêtes")
plt.legend()
plt.grid()
info_text = "Paramètres fixes :\n- |V| = {n_fixed}\n- |J| = {j}\n- C = {C}".format(n_fixed=n_fixed, j=j, C=C)
plt.annotate(info_text, xy=(0.05, 0.05), xycoords='axes fraction',
             fontsize=10, bbox=dict(boxstyle="round", facecolor="white", alpha=0.5))


plt.tight_layout()
plt.savefig("../graphs/comparison_N_M.png")
plt.show()



##### Tracé des résultats en fonction du nombre de trajets #####
plt.figure(figsize=(10, 4))

# Coût en fonction du nombre de trajets
plt.subplot(1, 2, 1)
plt.plot(j_values, remove_edges_means_costs_j, 's-', label="Algorithme Remove edges")
plt.plot(j_values, update_costs_means_costs_j, 'o-', label="Algorithme Update costs")
plt.xlabel("Nombre de trajets")
plt.ylabel("Coût total du réseau")
plt.title("Coût total du réseau en fonction du nombre de trajets")
plt.legend()
plt.grid()
info_text = "Paramètres fixes :\n- |V| = {n_fixed_for_j}\n- |E| = {m_fixed_for_j}\n- C = {C}".format(n_fixed_for_j=n_fixed_for_j, m_fixed_for_j=m_fixed_for_j, C=C)
plt.annotate(info_text, xy=(0.1, 0.1), xycoords='axes fraction',
             fontsize=10, bbox=dict(boxstyle="round", facecolor="white", alpha=0.5))


# Temps d'exécution en fonction du nombre de trajets    
plt.subplot(1, 2, 2)
plt.loglog(j_values, remove_edges_means_times_j, 'o-', label="Algorithme Remove edges")
plt.loglog(j_values, update_costs_means_times_j, 's-', label="Algorithme Update costs")
plt.xlabel("Nombre de trajets")
plt.ylabel("Temps d'exécution (s)")
plt.title("Temps d'exécution en fonction du nombre de trajets")
plt.legend()
plt.grid()
info_text = "Paramètres fixes :\n- |V| = {n_fixed_for_j}\n- |E| = {m_fixed_for_j}\n- C = {C}".format(n_fixed_for_j=n_fixed_for_j, m_fixed_for_j=m_fixed_for_j, C=C)
plt.annotate(info_text, xy=(0.05, 0.05), xycoords='axes fraction',
             fontsize=10, bbox=dict(boxstyle="round", facecolor="white", alpha=0.5))

plt.tight_layout()
plt.savefig("../graphs/comparison_J.png")
plt.show()



##### Tracé des résultats en fonction du coût C #####
plt.figure(figsize=(10, 8))

# Coût en fonction du coût C
plt.subplot(2, 1, 1)
plt.plot(C_values, remove_edges_costs, 'o-', label="Algorithme Remove edges")
plt.plot(C_values, update_costs_costs, 's-', label="Algorithme Update costs")
plt.xlabel("C (coût par arête)")
plt.ylabel("Coût total du réseau")
plt.title("Coût total du réseau en fonction du côut C par arête")
plt.legend()
plt.grid()
info_text = "Paramètres fixes :\n- |V| = {n_fixed_for_C}\n- |E| = {m_fixed_for_C}\n- |J| = {j}".format(n_fixed_for_C=n_fixed_for_C, m_fixed_for_C=m_fixed_for_C, j=j)
plt.annotate(info_text, xy=(0.05, 0.05), xycoords='axes fraction',
             fontsize=10, bbox=dict(boxstyle="round", facecolor="white", alpha=0.5))

# Comparaison des temps d'exécution
plt.subplot(2, 1, 2)
plt.plot(C_values, remove_edges_times, 'o-', label="Algorithme Remove edges")
plt.plot(C_values, update_costs_times, 's-', label="Algorithme Update costs")
plt.xlabel("C (coût par arête)")
plt.ylabel("Temps d'exécution (s)")
plt.title("Temps d'exécution en fonction du coût C par arête")
plt.legend()
plt.grid()
info_text = "Paramètres fixes :\n- |V| = {n_fixed_for_C}\n- |E| = {m_fixed_for_C}\n- |J| = {j}".format(n_fixed_for_C=n_fixed_for_C, m_fixed_for_C=m_fixed_for_C, j=j)
plt.annotate(info_text, xy=(0.05, 0.05), xycoords='axes fraction',
             fontsize=10, bbox=dict(boxstyle="round", facecolor="white", alpha=0.5))

plt.tight_layout()
plt.savefig("../graphs/comparison_C.png")
plt.show()
