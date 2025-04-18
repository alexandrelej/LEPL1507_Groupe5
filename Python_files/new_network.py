import csv
import networkx as nx
from update_costs import Update_costs
from create_graphs import create_airport_graph, create_random_subgraph, generate_random_pairs, add_prices, add_times, graph_to_json_file
import copy


def new_network(airports_csv, routes_csv, C,  wanted_journeys_csv):
    """
    Crée un nouveau réseau avec les paramètres donnés.

    Paramètres :
        airport_csv (str) : Chemin vers le fichier airport.csv.
        routes_csv (str) : Chemin vers le fichier pre_existing_routes.csv.
        C (int) : Coût par trajet.
        j (int) : Nombre de paires de destinations à générer.

    Retourne :
        int : Le coût de la fonction objectif.
        list : Une liste des trajets sélectionnés + création d’un fichier CSV contenant ces trajets.
    """
    
    # Create the complete graph
    airport_graph = create_airport_graph(airports_csv, routes_csv)
    print("Number of nodes in the graph:", len(airport_graph.nodes()))
    print("Number of edges in the graph:", len(airport_graph.edges()))
    
    # Generate a random subgraph
    #random_subgraph = create_random_subgraph(airport_graph, n=75, m=1500) # to comment if we want the whole data to create the new network

    #destination_pairs = generate_random_pairs(random_subgraph, j)
    destination_pairs = []
    with open(wanted_journeys_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # saute l’en‑tête
        for row in reader:
            start, end = row
            destination_pairs.append((start, end))

    # Generate the new network
    #G_reweighted, rsubgraph = Update_costs(random_subgraph, destination_pairs, C)
    G_reweighted, rsubgraph = Update_costs(airport_graph, destination_pairs, C)
    cost = sum([nx.shortest_path_length(G_reweighted, start, end) for start, end in destination_pairs]) / len(destination_pairs) + C * len(G_reweighted.edges())

    # Creation of a CSV file containing the selected routes
    with open('../basic_datasets/new_routes.csv', 'w') as f:
        f.write("start,end,distance\n")
        for start, end in G_reweighted.edges():
            distance = G_reweighted[start][end]['distance']
            f.write(f"{start},{end},{distance}\n")

    # Save the graph to a json file
    G_all = copy.deepcopy(G_reweighted)
    # Ajout des paires de destinations au graphe (en les convertissant en liste de listes)
    G_all.graph["destination_pairs"] = [tuple(pair) for pair in destination_pairs]
    add_prices(G_all, "../basic_datasets/prices.csv")
    add_times(G_all, "../basic_datasets/waiting_times.csv", average_speed=800)
    graph_to_json_file(G_all, "../json/all.json")

    return cost, G_reweighted.edges()


final_cost, new_routes = new_network("../basic_datasets/airports.csv", "../basic_datasets/pre_existing_routes.csv", C=4, wanted_journeys_csv="../basic_datasets/wanted_journeys.csv")
print(final_cost)
print(new_routes)
new_routes_list = list(new_routes)  # Conversion en liste pour compter
print(len(new_routes_list))         # Impression du nombre d'arêtes
