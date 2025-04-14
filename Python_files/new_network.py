import networkx as nx
import numpy as np
import time
import random
from update_costs import Update_costs
from create_graphs import create_airport_graph, create_random_subgraph, generate_random_pairs


def new_network(airports_csv, routes_csv, C, j=20):
    """
    Create a new network with the given parameters.

    Parameters:
        airport_csv (str): Path to the airport.csv file.
        routes_csv (str): Path to the pre_existing_routes.csv file.
        C (int): Cost per route.
        j (int): Number of destination pairs to generate.

    Returns:
        int: The cost of the objective function.
        list: A list of selected routes + creation of a CSV file containing those selected routes.
    """
    
    # Create the complete graph
    airport_graph = create_airport_graph(airports_csv, routes_csv)

    # Generate a random subgraph
    random_subgraph = create_random_subgraph(airport_graph, n=50, m=200) # to comment if we want the whole data to create the new network
    destination_pairs = generate_random_pairs(random_subgraph, j)

    # Generate the new network
    G_reweighted, rsubgraph = Update_costs(random_subgraph, destination_pairs, C)
    cost = sum([nx.shortest_path_length(G_reweighted, start, end) for start, end in destination_pairs]) / len(destination_pairs) + C * len(G_reweighted.edges())

    # Creation of a CSV file containing the selected routes
    with open('../basic_datasets/new_routes.csv', 'w') as f:
        f.write("start,end,distance\n")
        for start, end in G_reweighted.edges():
            distance = G_reweighted[start][end]['distance']
            f.write(f"{start},{end},{distance}\n")

    return cost, G_reweighted.edges()


final_cost, new_routes = new_network("../basic_datasets/airports.csv", "../basic_datasets/pre_existing_routes.csv", C=2000)
print(final_cost)
print(new_routes)
print(len(new_routes))