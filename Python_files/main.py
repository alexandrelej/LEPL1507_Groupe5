import create_graphe
import create_random_graphes
import A_star
import json
import networkx as nx

airports = create_graphe.load_airports("../basic_datasets/airports.csv")
connections = create_graphe.load_connections("../basic_datasets/pre_existing_routes.csv")

G = create_graphe.CreateGraphe(airports,connections)
J = create_random_graphes.generate_random_pairs(G, 20)
C = 1000

G,_,_ = A_star.Astar(G,J,C)

# Conversion du graphe en dictionnaire et sauvegarder en JSON pour ne pas run le programme chaque fois que l'utilisateur demande un trajet
with open("../json/graph.json", "w") as f:
    json.dump(nx.node_link_data(G), f)
