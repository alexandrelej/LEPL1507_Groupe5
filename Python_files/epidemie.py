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

def robustesse(G):
    """
    Calcule un indice de robustesse basé sur le rayon spectral, le degré moyen et
    la connectivité (via la deuxième plus petite valeur propre de la matrice laplacienne, 
    appelée valeur de Fiedler).

    Un indice élevé indique un graphe potentiellement plus fragile (plus sensible à 
    la propagation d'une épidémie ou à la déconnexion lors de suppressions de nœuds), 
    tandis qu'un indice faible suggère une structure plus robuste.

    Retourne un dictionnaire contenant :
      - 'spectral_radius' : rayon spectral du graphe
      - 'average_degree'  : degré moyen
      - 'fiedler_value'   : valeur de Fiedler (connectivité)
      - 'robustness_index' : indice de robustesse calculé
      - 'interpretation'   : fourchette d'interprétation
    """
    
    # Calcul du rayon spectral
    A = nx.to_numpy_array(G)
    eigenvalues = np.linalg.eigvals(A)
    spectral_radius = max(abs(eigenvalues))
    
    # Calcul du degré moyen
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    average_degree = 2 * n_edges / n_nodes if n_nodes > 0 else 0

    # Calcul de la valeur de Fiedler (deuxième plus petite valeur propre de la matrice laplacienne)
    try:
        # Utilisation de la fonction pour obtenir la matrice laplacienne (sous forme numpy array)
        L = nx.laplacian_matrix(G).todense()
        lap_eigs = np.linalg.eigvals(L)
        lap_eigs = np.sort(np.real(lap_eigs))
        # La première valeur propre est toujours 0, la deuxième est la valeur de Fiedler
        fiedler_value = lap_eigs[1] if len(lap_eigs) > 1 else 0.0
    except Exception as e:
        print("Erreur lors du calcul de la valeur de Fiedler:", e)
        fiedler_value = 0.0

    # On définit un indice de robustesse qui augmente avec le rayon spectral et diminue avec le degré moyen et la connectivité.
    # Cette formule est indicative et peut être adaptée.
    # Par exemple, si le graphe est dense et bien connecté, average_degree et fiedler_value seront élevés et l'indice sera faible.
    robustness_index = spectral_radius / (average_degree * (1 + fiedler_value)) if average_degree > 0 else np.inf

    # Définition d'une interprétation en "fourchettes" (ces seuils sont arbitraires et à ajuster)
    if robustness_index < 0.25:
        interpretation = "Très robuste"
    elif robustness_index < 0.5:
        interpretation = "Robuste"
    elif robustness_index < 1:
        interpretation = "Peu robuste"
    else:
        interpretation = "Fragile"
    
    result = {
        'spectral_radius': spectral_radius,
        'average_degree': average_degree,
        'fiedler_value': fiedler_value,
        'robustness_index': robustness_index,
        'interpretation': interpretation
    }
    
    print("Rayon spectral         :", spectral_radius)
    print("Degré moyen            :", average_degree)
    print("Valeur de Fiedler      :", fiedler_value)
    print("Indice de robustesse   :", robustness_index)
    print("Interprétation         :", interpretation)
    
    return result

def robustness_metrics(G):
    """
    Calcule trois indicateurs de robustesse pour un graphe dirigé :
      - Taille de la plus grande composante fortement connexe (GSCC)
      - Longueur moyenne des plus courts chemins dans la GSCC
      - Efficacité globale
    """
    components = sorted(nx.strongly_connected_components(G), key=len, reverse=True)
    
    if not components:
        return 0, 0, 0  # Graphe vide

    largest_scc = G.subgraph(components[0]).copy()
    size_gscc = largest_scc.number_of_nodes()
    
    avg_path = nx.average_shortest_path_length(largest_scc) if size_gscc > 1 else 0
    efficiency = nx.global_efficiency(G.to_undirected())

    return size_gscc, avg_path, efficiency


def simulate_edge_removal(G, record_interval=1):
    """
    Supprime itérativement des arêtes et enregistre la robustesse du graphe à intervalles réguliers.
    Retourne :
      - La fraction d'arêtes retirées
      - La taille de la GSCC
      - La longueur moyenne des plus courts chemins
      - L'efficacité globale
      - Le nombre total de composantes fortement connexes
    """
    G_copy = G.copy()
    total_edges = G_copy.number_of_edges()
    
    results = {
        "fractions": [0.0],
        "gscc_sizes": [],
        "avg_paths": [],
        "efficiencies": [],
        "num_components": [],
    }

    # Mesure initiale
    gscc_size, avg_path, efficiency = robustness_metrics(G_copy)
    results["gscc_sizes"].append(gscc_size)
    results["avg_paths"].append(avg_path)
    results["efficiencies"].append(efficiency)
    results["num_components"].append(nx.number_strongly_connected_components(G_copy))

    edges_list = list(G_copy.edges())
    random.shuffle(edges_list)

    for i, edge in enumerate(edges_list):
        G_copy.remove_edge(*edge)

        if (i + 1) % record_interval == 0 or i == total_edges - 1:
            frac_removed = (i + 1) / total_edges
            gscc_size, avg_path, efficiency = robustness_metrics(G_copy)
            
            results["fractions"].append(frac_removed)
            results["gscc_sizes"].append(gscc_size)
            results["avg_paths"].append(avg_path)
            results["efficiencies"].append(efficiency)
            results["num_components"].append(nx.number_strongly_connected_components(G_copy))

    return results

# Moyenne sur 10 itérations où il retire des arêtes dans un ordre random

def average_simulations(G, num_simulations=10, record_interval=5, num_points=50):
    """
    Exécute plusieurs simulations de suppression itérative d'arêtes et calcule la moyenne des résultats.
    """
    all_results = [simulate_edge_removal(G, record_interval) for _ in range(num_simulations)]
    
    max_frac = max(res["fractions"][-1] for res in all_results)
    common_fractions = np.linspace(0, max_frac, num_points)
    
    def interpolate(metric):
        return np.mean([np.interp(common_fractions, res["fractions"], res[metric]) for res in all_results], axis=0)
    
    return {
        "fractions": common_fractions,
        "gscc_sizes": interpolate("gscc_sizes"),
        "avg_paths": interpolate("avg_paths"),
        "efficiencies": interpolate("efficiencies"),
        "num_components": interpolate("num_components"),
    }
