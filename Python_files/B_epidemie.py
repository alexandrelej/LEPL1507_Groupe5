import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random

def epidemic(G):
    # Calcul de la centralité par vecteur propre
    centrality = nx.eigenvector_centrality(G, max_iter=1000)
    node_to_remove = max(centrality, key=centrality.get)
    print("Aéroport à retirer (nœud):", node_to_remove)

    # Calcul du rayon spectral = plus grande valeur propre
    A = nx.to_numpy_array(G)
    eigenvalues = np.linalg.eigvals(A)
    spectral_radius = max(abs(eigenvalues))
    print("Rayon spectral avant retrait:", spectral_radius)

    G_removed = G.copy()
    # Retire noeud qui baisse le plus le rayon spectral
    G_removed.remove_node(node_to_remove)

    A_removed = nx.to_numpy_array(G_removed)
    eigenvalues_removed = np.linalg.eigvals(A_removed)
    spectral_radius_removed = max(abs(eigenvalues_removed))
    print("Rayon spectral après retrait:", spectral_radius_removed)

    return G_removed

