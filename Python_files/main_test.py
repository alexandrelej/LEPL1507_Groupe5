import time
import matplotlib.pyplot as plt
import numpy as np
from create_random_graphes import create_airport_graph, create_random_subgraph, generate_random_pairs
from visualisation import visualize_graph_on_globe
from A_star import Astar, precompute_shortest_paths
from multiple_astar import approx_multiple_astar
import networkx as nx

debug = False
# Chemins vers les fichiers CSV
airports_csv = "../basic_datasets/airports.csv"
routes_csv = "../basic_datasets/pre_existing_routes.csv"

# Créer le graphe complet
airport_graph = create_airport_graph(airports_csv, routes_csv)

# Lire les valeurs de n et m depuis l'input sous forme "10 20 30"
n_values = list(map(int, input("Liste des nombres de nœuds (séparés par espace) : ").split()))
m_values = list(map(int, input("Liste des nombres d'arêtes (séparés par espace) : ").split()))
j = int(input("Nombre de chemins requis (paires de destinations) = "))
C_values = list(map(int, input("Liste des différentes coûts pour une arête supplémentaire : ").split()))

astar_costs = []
multi_astar_costs = []
astar_times = []
multi_astar_times = []
# Boucler sur différentes tailles de sous-graphes
for n, m in zip(n_values, m_values):
    print(f"\n### Test avec n = {n}, m = {m} ###")

    # Générer un sous-graphe aléatoire
    random_subgraph = create_random_subgraph(airport_graph, n, m)
    destination_pairs = generate_random_pairs(random_subgraph, j)

    if debug:
        # Exécuter et visualiser A* une seule fois pour n et m fixés
        if n == n_values[0] and m == m_values[0]:  # Visualisation seulement pour la première itération
            C = C_values[0]  # On prend la première valeur de C pour la visualisation
            G_prime, best_edge_removed, best_cost = Astar(random_subgraph, destination_pairs, C)
            shortest_paths = precompute_shortest_paths(G_prime, destination_pairs)
            visualize_graph_on_globe(random_subgraph, shortest_paths)
            print("\n=== Résultats de l'A* Optimisé ===")
            print("Arête supprimée pour optimisation :", best_edge_removed)
            print("Meilleur coût moyen obtenu :", best_cost)
            print("Nombre d'arêtes restantes :", G_prime.number_of_edges())
            print("Liste des arêtes restantes :", list(G_prime.edges(data=True)))



    # Boucle sur différentes valeurs de C
    for C in C_values:
        print(f"\nTest avec C = {C}")

        # Exécuter A*
        start_time = time.time()
        G_prime, best_edge_removed, best_cost = Astar(random_subgraph, destination_pairs, C)
        astar_time = time.time() - start_time
        astar_costs.append(best_cost)
        astar_times.append(astar_time)

        print(f"Astar - Coût: {best_cost}, Temps: {astar_time:.4f}s")

        # Exécuter Mult_multiple_astar
        start_time = time.time()
        G_mult, rsubgraph = approx_multiple_astar(random_subgraph, destination_pairs, C,iterations=max(n, m))
        multi_astar_time = time.time() - start_time
        multi_astar_cost = sum([nx.shortest_path_length(G_mult,start,end) for start, end in destination_pairs])/len(destination_pairs) + C * len(G_mult.edges())
        multi_astar_costs.append(multi_astar_cost)
        multi_astar_times.append(multi_astar_time)

        print(f"Mult Astar - Coût: {multi_astar_cost}, Temps: {multi_astar_time:.4f}s")

# Tracer les résultats
plt.figure(figsize=(12, 5))

# Comparaison des coûts
plt.subplot(1, 2, 1)
plt.plot(np.arange(len(astar_costs)), astar_costs, 'o-', label="A*")
plt.plot(np.arange(len(astar_costs)), multi_astar_costs, 's-', label="Mult A*")
plt.xlabel("C (Coût par arête)")
plt.ylabel("Coût total")
plt.title("Comparaison des coûts")
plt.legend()
plt.grid()

# Comparaison des temps d'exécution
plt.subplot(1, 2, 2)
plt.plot(np.arange(len(astar_costs)), astar_times, 'o-', label="A*")
plt.plot(np.arange(len(astar_costs)), multi_astar_times, 's-', label="Mult A*")
plt.xlabel("C (Coût par arête)")
plt.ylabel("Temps d'exécution (s)")
plt.title("Comparaison des temps d'exécution")
plt.legend()
plt.grid()

plt.tight_layout()
plt.savefig("resultats.png")  # Enregistre le graphique dans un fichier


