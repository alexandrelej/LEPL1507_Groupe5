import csv
import networkx as nx
from update_costs import Update_costs
from create_graphs import create_airport_graph, create_random_subgraph, generate_random_pairs, add_prices, add_times, graph_to_json_file
import copy
import os 


def new_network(airports_csv, routes_csv, C, j=None, wanted_journeys_csv=None):
    """
    Crée un nouveau réseau avec les paramètres donnés.

    Paramètres :
        airports_csv (str) : Chemin vers le fichier airports.csv.
        routes_csv (str) : Chemin vers le fichier pre_existing_routes.csv.
        C (int) : Coût par trajet.
        j (int, optionnel) : Nombre de paires à générer aléatoirement.
        wanted_journeys_csv (str, optionnel) : Chemin vers un CSV de paires start,end.

    Si `wanted_journeys_csv` existe, lit les paires. Sinon, génère `j` paires et les écrit dans ce fichier.

    Retourne :
        cost (float) : Valeur de la fonction objectif.
        edges (list) : Liste des arêtes du nouveau réseau.
    """
    # Création du graphe complet
    airport_graph = create_airport_graph(airports_csv, routes_csv)
    print("Nombre de nœuds dans le graphe :", len(airport_graph.nodes()))
    print("Nombre d'arêtes dans le graphe :", len(airport_graph.edges()))

    # Collecte des paires de destination
    if wanted_journeys_csv:
        if os.path.exists(wanted_journeys_csv):
            # Le fichier existe → on le lit
            destination_pairs = []
            with open(wanted_journeys_csv, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None)  # sauter l'en-tête s'il existe
                for row in reader:
                    if len(row) >= 2:
                        destination_pairs.append((row[0], row[1]))
        elif j is not None:
            # Le fichier n'existe pas → on le génère
            destination_pairs = generate_random_pairs(airport_graph, j, wanted_journeys_csv)
        else:
            raise ValueError("Le fichier des paires n'existe pas, et aucun nombre `j` n’a été fourni pour en générer.")
    else:
        raise ValueError("Vous devez fournir le chemin `wanted_journeys_csv`.")

    # Mise à jour des coûts et sous-graphe rechargé
    G_reweighted, rsubgraph = Update_costs(airport_graph, destination_pairs, C)
    # Calcul du coût objectif
    avg_path_cost = sum(nx.shortest_path_length(G_reweighted, s, t) for s, t in destination_pairs) / len(destination_pairs)
    cost = avg_path_cost + C * G_reweighted.number_of_edges()

    # Export des nouvelles routes en CSV
    new_routes_csv = '../basic_datasets/new_routes.csv'
    with open(new_routes_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['start', 'end', 'distance'])
        for u, v, data in G_reweighted.edges(data=True):
            writer.writerow([u, v, data.get('distance')])

    # Sauvegarde du graphe complet en JSON
    G_all = copy.deepcopy(G_reweighted)
    G_all.graph['destination_pairs'] = destination_pairs
    add_prices(G_all, '../basic_datasets/prices.csv')
    add_times(G_all, '../basic_datasets/waiting_times.csv', average_speed=800)
    graph_to_json_file(G_all, '../json/all.json')

    return cost, list(G_reweighted.edges())

final_cost, new_routes = new_network(
    airports_csv="../basic_datasets/airports.csv",
    routes_csv="../basic_datasets/pre_existing_routes.csv",
    C=4,
    j=100,
    wanted_journeys_csv="../basic_datasets/wanted_journeys.csv"
)

print(final_cost)
print(new_routes)
new_routes_list = list(new_routes)
print(len(new_routes_list))
