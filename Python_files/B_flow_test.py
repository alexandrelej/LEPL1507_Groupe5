import sys
import os
import B_flow
import time
import matplotlib.pyplot as plt
from create_random_graphes import create_airport_graph, create_random_subgraph, generate_random_pairs
#from visualisation.visualisation import visualize_graph_on_globe


# Chemins vers les fichiers CSV
airports_csv = "../basic_datasets/airports.csv"
routes_csv = "../basic_datasets/pre_existing_routes.csv"

# Créer le graphe complet
airport_graph = create_airport_graph(airports_csv, routes_csv)
print("A")

# Define different sizes and parameters for testing
graph_sizes = [(20, 50, 30), (30, 75, 45), (40, 100, 60)]
flow_binaire_options = [True, False]
choice_binaire_options = [True, False]
C_values = [1000, 5000, 10000]

# Initialize lists to store performance data
performance_data = []

# Loop over different graph sizes and parameter combinations
for (n, m, j) in graph_sizes:
    print(f"Testing with graph size: n={n}, m={m}, j={j}")
    random_subgraph = create_random_subgraph(airport_graph, n, m)
    destination_pairs = generate_random_pairs(random_subgraph, j)
    
    print("Sous-graphe aléatoire :")
    print("Nombre de nœuds :", random_subgraph.number_of_nodes())
    print("Nombre d'arêtes :", random_subgraph.number_of_edges())
    print("Liste des nœuds :", list(random_subgraph.nodes(data=True)))
    print("Liste des arêtes :", list(random_subgraph.edges(data=True)))
    print(f"Paires de destinations (avec chemin) : {destination_pairs}")

    for flow_binaire in flow_binaire_options:
        for choice_binaire in choice_binaire_options:
            for C in C_values:
                print(f"Testing solve_flow with flow_binaire={flow_binaire}, choice_binaire={choice_binaire}, C={C}")
                start_time = time.time()
                solved_graph = B_flow.solve_flow(random_subgraph, destination_pairs, C, flow_binaire=flow_binaire, Choice_binaire=choice_binaire,Initialise=True)
                end_time = time.time()
                time_taken = end_time - start_time
                print(f"Time taken: {time_taken} seconds")
                
                # Store performance data
                performance_data.append((n, m, j, flow_binaire, choice_binaire, C, time_taken))
                #visualize_graph_on_globe(solved_graph)

# Plot performance data
plt.figure(figsize=(12, 8))
for (n, m, j, flow_binaire, choice_binaire, C, time_taken) in performance_data:
    label = f"n={n}, m={m}, j={j}, flow_binaire={flow_binaire}, choice_binaire={choice_binaire}, C={C}"
    plt.scatter(C, time_taken, label=label)

plt.xlabel("C value")
plt.ylabel("Time taken (seconds)")
plt.title("Performance of solve_flow with different parameters")
plt.legend()
plt.show()
