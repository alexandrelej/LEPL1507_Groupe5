import time
import matplotlib.pyplot as plt
import numpy as np
from create_random_graphes import create_airport_graph, create_random_subgraph, generate_random_pairs
from visualisation import visualize_graph_on_globe
# from A_star import Astar, precompute_shortest_paths 
from multiple_astar import approx_multiple_astar as update_costs
from epidemie import *
import json
from networkx.readwrite import json_graph
import networkx as nx
import os
import pandas as pd
import copy 


def graph_to_json_file(G, file_path):
    """
    Convertit un graphe NetworkX en JSON (format node-link) et l'écrit dans un fichier.
    
    Parameters:
        G (networkx.Graph): Le graphe à convertir.
        file_path (str): Le chemin du fichier dans lequel sauvegarder la représentation JSON.
    """
    data = json_graph.node_link_data(G)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def change_to_prices(G, prices_csv):
    """
    Crée une copie du graphe G où la clé 'distance' de chaque arête est remplacée par le prix du vol.
    """
    G_prices = copy.deepcopy(G)
    prices = pd.read_csv(prices_csv)

    for edge in G_prices.edges:
        start_node, end_node = edge
        price_row = prices[(prices['ID_start'] == start_node) & (prices['ID_end'] == end_node)]
        if not price_row.empty:
            price = price_row.iloc[0]['price_tag']
            G_prices.edges[start_node, end_node]['distance'] = price
        else:
            print(f"[Warning] Prix non trouvé pour le vol de {start_node} à {end_node}.")

    return G_prices


def change_to_times(G, waiting_times_csv, average_speed=800):
    """
    Crée une copie du graphe G où la clé 'distance' est remplacée par un temps de trajet
    (calculé à partir de la distance et du temps d’attente au départ).
    """
    G_times = copy.deepcopy(G)
    waiting_times = pd.read_csv(waiting_times_csv)

    # Créer un dictionnaire rapide des idle_time
    idle_time_dict = dict(zip(waiting_times['ID'], waiting_times['idle_time']))

    for edge in G_times.edges:
        start_node, end_node = edge
        distance = G_times.edges[start_node, end_node]['distance']
        flight_time = distance / average_speed

        idle_time = idle_time_dict.get(start_node, 0)
        total_time = flight_time + idle_time

        G_times.edges[start_node, end_node]['distance'] = total_time

    return G_times

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
n_values = [20]
m_values = [50]
j = 5
C_values = [2000]


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

    # --- Code utilisant remove_edges (anciennement A_star) mis en commentaire ---
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
        # astar_time = time.time() - start_time
        # astar_costs.append(best_cost)
        # astar_times.append(astar_time)
        # print(f"remove_edges - Coût: {best_cost}, Temps: {astar_time:.4f}s")

        # Exécuter update_costs
        start_time = time.time()
        G_mult, rsubgraph = update_costs(random_subgraph, destination_pairs, C, iterations=min(n, m))
        
        # Conversion du sous-graphe optimisé en JSON
        graph_to_json_file(G_mult, "../json/G_mult_distances.json")

        G_prices = change_to_prices(G_mult, "../basic_datasets/prices.csv")
        graph_to_json_file(G_prices, "../json/G_mult_with_prices.json")

        G_times = change_to_times(G_mult, "../basic_datasets/waiting_times.csv")
        graph_to_json_file(G_times, "../json/G_mult_with_times.json")

        multi_astar_time = time.time() - start_time
        multi_astar_cost = sum([nx.shortest_path_length(G_mult, start, end) for start, end in destination_pairs]) / len(destination_pairs) + C * len(G_mult.edges())
        multi_astar_costs.append(multi_astar_cost)
        multi_astar_times.append(multi_astar_time)

        print(f"update_costs - Coût: {multi_astar_cost}, Temps: {multi_astar_time:.4f}s")

        # Appel de visualize_graph_on_globe pour la première itération et pour la première valeur de C
        if n == n_values[0] and C == C_values[0]:
            # Calculer les plus courts chemins pour la visualisation
            shortest_paths = {}
            for start, end in destination_pairs:
                try:
                    path = nx.shortest_path(G_mult, start, end)
                    length = nx.shortest_path_length(G_mult, start, end)
                except nx.NetworkXNoPath:
                    path = []
                    length = float('inf')
                shortest_paths[(start, end)] = (path, length)
            visualize_graph_on_globe(random_subgraph, shortest_paths)

# Tracer les résultats
plt.figure(figsize=(12, 5))

# Comparaison des coûts
plt.subplot(1, 2, 1)
# plt.plot(astar_costs, 'o-', label="remove_edges")   # Code remove_edges mis en commentaire
plt.plot(multi_astar_costs, 's-', label="update_costs")
plt.xlabel("C (Coût par arête)")
plt.ylabel("Coût total")
plt.title("Comparaison des coûts")
plt.legend()
plt.grid()

# Comparaison des temps d'exécution
plt.subplot(1, 2, 2)
# plt.plot(np.arange(len(astar_costs)), astar_times, 'o-', label="remove_edges")
plt.plot(np.arange(len(multi_astar_times)), multi_astar_times, 's-', label="update_costs")
plt.xlabel("C (Coût par arête)")
plt.ylabel("Temps d'exécution (s)")
plt.title("Comparaison des temps d'exécution")
plt.legend()
plt.grid()

plt.tight_layout()
plt.savefig("resultats.png")  # Enregistre le graphique dans un fichier

# --- Test sur la propagation d'épidémie sur le graphe complet ---
print("\n=== Test de l'épidémie sur le graphe complet ===")
# On utilise ici le graphe complet airport_graph
G_after_epidemic = epidemic(random_subgraph)
G_robustesse = robustesse(random_subgraph)

    
results = average_simulations(random_subgraph, num_simulations=10, record_interval=5)

common_fractions = results["fractions"]
gcc_sizes = results["gscc_sizes"]
avg_mean = results["avg_paths"]
eff_mean = results["efficiencies"]
n_comp_mean = results["num_components"]

plt.figure(figsize=(16, 4))
    
plt.subplot(141)
plt.plot(common_fractions, gcc_sizes, marker='o', color='blue')
plt.xlabel("Fraction d'arêtes retirées")
plt.ylabel("Taille de la GCC")
plt.title("Taille de la composante géante (moyenne)")

plt.subplot(142)
plt.plot(common_fractions, avg_mean, marker='o', color='green')
plt.xlabel("Fraction d'arêtes retirées")
plt.ylabel("Longueur moyenne")
plt.title("Longueur moyenne des chemins (moyenne)")

plt.subplot(143)
plt.plot(common_fractions, eff_mean, marker='o', color='red')
plt.xlabel("Fraction d'arêtes retirées")
plt.ylabel("Efficacité globale")
plt.title("Efficacité globale du réseau (moyenne)")
    
plt.subplot(144)
plt.plot(common_fractions, n_comp_mean, marker='o', color='purple')
plt.xlabel("Fraction d'arêtes retirées")
plt.ylabel("Nombre de composantes")
plt.title("Nombre de composantes connexes (moyenne)")
    
plt.tight_layout()
plt.savefig("robustesse_edge_removal.png")