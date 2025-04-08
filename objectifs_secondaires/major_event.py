import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import json

# Charger le fichier JSON du graphe
with open("json/graph.json", "r") as f:
    graph_data = json.load(f)

# Construire le graphe initial
G = nx.DiGraph()
for link in graph_data["links"]:
    G.add_edge(link["source"], link["target"], distance=link["distance"])

# Charger les capacités des aéroports
df_airports = pd.read_csv("basic_datasets/capacities_airports.csv")  # Colonne: "airport", "capacity"
airport_capacities = dict(zip(df_airports["airportsID"], df_airports["capacity"]))

# Charger les capacités des routes
df_connections = pd.read_csv("basic_datasets/capacities_connexions.csv")  # Colonnes: "source", "target", "capacity"
for _, row in df_connections.iterrows():
    if G.has_edge(row["ID_start"], row["ID_end"]):
        G[row["ID_start"]][row["ID_end"]]["connexion capacity"] = row["connexion capacity"]


def preprocess_and_max_flow(G, airport_capacities, J):
    """
    Transforme le graphe G en dédoublant les aéroports et applique l'algorithme de Ford-Fulkerson 
    sur chaque trajet de la liste J pour retourner le flot maximal de chaque trajet.

    :param G: networkx.DiGraph() - Graphe initial avec les routes aériennes et leurs capacités
    :param airport_capacities: dict - Dictionnaire {aéroport: capacité max journalière}
    :param J: list of tuples - Liste de trajets (départ, arrivée)
    :return: dict - Flot maximal pour chaque trajet de J
    """
    # Création d'un graphe transformé avec duplication des aéroports
    G_transformed = nx.DiGraph()

    # Dédoubler chaque nœud (aéroport)
    for airport, capacity in airport_capacities.items():
        # Création des nœuds doublés : original -> in_node, duplicata -> out_node
        in_node, out_node = f"{airport}_in", f"{airport}_out"
        G_transformed.add_edge(in_node, out_node, capacity=capacity)  # Arête entre in et out avec capacité aéroport

    # Ajouter les arêtes avec capacités
    for u, v, data in G.edges(data=True):
        G_transformed.add_edge(f"{u}_out", f"{v}_in", capacity=data["connexion capacity"])

    # Calcul du flot maximal pour chaque trajet
    max_flows = {}
    for (start, end) in J:
        # Convertir les trajets pour correspondre aux nouveaux noms de nœuds
        source, sink = f"{start}_in", f"{end}_out"

        # Calcul du flot maximal avec Ford-Fulkerson
        flow_value, _ = nx.maximum_flow(G_transformed, source, sink, capacity="capacity")
        max_flows[(start, end)] = flow_value  # Stocker le flot maximal pour ce trajet

    return max_flows

# Exemple de trajets à analyser
J = [("YYZ", "BOS"), ("FRA", "ADD"), ("HND", "SFO"), ("BOM", "SIN"), ("MAD", "DOH")]

# Calcul du flot maximal
resultats = preprocess_and_max_flow(G, airport_capacities, J)

# Affichage des résultats
for trajet, flot in resultats.items():
    print(f"Flot maximal de {trajet[0]} à {trajet[1]} : {flot}")



# Trier les résultats par flot max décroissant
sorted_results = sorted(resultats.items(), key=lambda x: x[1], reverse=True)
trajets, flots = zip(*sorted_results)

# Transformer les tuples en chaînes
trajets_labels = [f"{start} → {end}" for start, end in trajets]

# Calcul des statistiques
mean_flow = np.mean(flots)
min_flow = np.min(flots)
max_flow = np.max(flots)
std_dev = np.std(flots)

# Création de l'histogramme
plt.figure(figsize=(10, 6))
plt.vlines(trajets_labels, ymin=0, ymax=flots, color="skyblue", linewidth=3, label="Flot max par trajet")
plt.axhline(mean_flow, color="red", linestyle="dashed", linewidth=2, label=f"Moyenne = {mean_flow:.2f}")

# Ajouter la légende avec les stats
plt.legend(title=f"Min: {min_flow}, Max: {max_flow}, Écart-type: {std_dev:.2f}")

# Labels et titre
plt.xlabel("Trajets")
plt.ylabel("Flot Maximal (nombre de personnes simultanément sur le réseau)")
plt.title("Histogramme des flots maximaux par trajet")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()

# Sauvegarder l'histogramme
plt.savefig("objectifs_secondaires/major_event.png")

