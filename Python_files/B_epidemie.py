import networkx as nx
import numpy as np
import pandas as pd
import scipy.linalg
import scipy.sparse.linalg
import matplotlib.pyplot as plt
import json

# number of wanted nodes to display
# in the final graph
number_of_nodes = 20

def add_transmition(G : nx.DiGraph, populations_csv, capacities_csv):
    pop = pd.read_csv(populations_csv)
    capa = pd.read_csv(capacities_csv)
    for edge in G.edges:
        start, end = edge
        capacitie = capa[(capa['ID_start'] == start) & (capa['ID_end'] == end)]['connexion capacity'].values
        population = pop[(pop['airportsID'] == start)]['capacity'].values
        G.edges[edge]["transmition"] = capacitie[0]/population[0]

def compute_laplacian(G : nx.DiGraph):

    # Calcul de la matrice d'adjacence pondérée
    A = nx.to_numpy_array(G, weight='transmition').T

    # Calcul de la matrice des degrés (degrés sortants)
    D = np.diag(A.sum(axis=1))

    # Calcul du Laplacien non normalisé
    L = A-D
    return L

def evaluate_sensibility(G : nx.DiGraph):
    L = compute_laplacian(G)
    print(L)
    eigval, eigvec = scipy.sparse.linalg.eigs(L, k = 1, which='LM')
    eigval = np.real(eigval)

    #print("Eigenvalues of the Laplacian matrix:", eigval)
    return eigval[0]

# Charger le fichier JSON du graphe
with open("json/all.json", "r") as f:
    graph_data = json.load(f)

# Construire le graphe initial
G = nx.DiGraph()
for link in graph_data["links"]:
    G.add_edge(link["source"], link["target"], distance=link["distance"])

add_transmition(G, "basic_datasets/capacities_airports.csv", "basic_datasets/capacities_connexions.csv")
init_eigvals = {}
init_eigvecs = {}
Connected_components = list(nx.weakly_connected_components(G))
average_eigval = 0
for i, component in enumerate(Connected_components):
    subgraph = G.subgraph(component)
    eigval, eigvec = scipy.sparse.linalg.eigs(compute_laplacian(subgraph), k = 1, which='LM')
    eigval = np.real(eigval)
    eigvec = np.real(eigvec)
    for j, node in enumerate(component):
        init_eigvals[node] = eigval[0]
        init_eigvecs[node] = abs(eigvec[j][0])
    average_eigval += eigval[0]*len(component)
average_eigval /= len(G.nodes())

average_eigvals = {}
n_cc = {}
for node in G.nodes():
    average_eigvals[node] = 0
    G_copy = G.copy()
    G_copy.remove_node(node)
    Connected_components = list(nx.weakly_connected_components(G_copy))
    n_cc[node] = len(Connected_components)
    for i, component in enumerate(Connected_components):
        size = len(component)
        if size == 1:
            continue
        subgraph = G_copy.subgraph(component)
        eigval, _ = scipy.sparse.linalg.eigs(compute_laplacian(subgraph), k = 1, which='LM')
        eigval = np.real(eigval)
        average_eigvals[node] += eigval[0]*size
    average_eigvals[node] /= len(G.nodes())

# Plot the results 

n = number_of_nodes  # nombre de nœuds à afficher pour chaque graphique

# 1) Calculer les amplitudes
abs_init_vals = {node: abs(val) for node, val in init_eigvals.items()}
abs_avg_vals  = {node: abs(val) for node, val in average_eigvals.items()}

# 2) Sélection top-n pour chaque critère

# — Critère 1 : plus grandes contributions à la norme L2 de init_eigvecs
vec2 = {node: comp**2 for node, comp in init_eigvecs.items()}
# tri par vec2 décroissant
top1 = [node for node, _ in sorted(vec2.items(), key=lambda x: x[1], reverse=True)][:n]
# on peut ensuite re-trier ces n selon l’amplitude de init_eigvals si on veut
top1.sort(key=lambda node: abs_init_vals[node], reverse=True)

# — Critère 2 : plus grand impact sur le nombre de composantes connexes
top2 = [node for node, comp in sorted(n_cc.items(), key=lambda x: x[1], reverse=True)][:n]

# --- Critère 3 : top-n par Δ valeur propre moyenne
# Supposons que vous avez : orig_mean = valeur propre moyenne initiale
delta = {
    node: abs(init_eigvals[node]) - abs(average_eigvals[node])
    for node in init_eigvals
}
top3 = sorted(delta, key=delta.get, reverse=True)[:n]
delta_vals = [delta[node] for node in top3]

# 3) Préparer les séries de valeurs
vals1 = [abs_init_vals[node] for node in top1]
vecs1 = [init_eigvecs[node]   for node in top1]

vals2 = [n_cc[node] for node in top2]
vals3 = [abs_avg_vals[node] for node in top3]
mean3 = abs(average_eigval)

# 4) Tracé en 1 ligne de 3 sous‑plots
fig, axes = plt.subplots(1, 3, figsize=(18, 6), constrained_layout=True)

# — Sous‑plot 1 : eigenvecs & amplitudes eigenvals
ax1 = axes[0]
ax1.bar(top1, vecs1, width=0.6, alpha=0.7, label="Composante vecteur propre")
ax1.set_xlabel("Nœuds (top n par contribution eigenvec)")
ax1.set_ylabel("Composante de l'eigenvecteur")
ax1.tick_params(axis='x', rotation=90)

ax1b = ax1.twinx()
ax1b.plot(top1, vals1, linestyle='--', marker='o', linewidth=2,
          label="Amplitude des valeurs propres")
ax1b.set_ylabel("Amplitude des valeurs propres (jour⁻¹)")

ax1.set_title(f"Top {n} contributions eigenvec\ntriés par |λ|")
# Légende hors du plot
l1, lb1 = ax1.get_legend_handles_labels()
l2, lb2 = ax1b.get_legend_handles_labels()
ax1.legend()

# — Sous‑plot 2 : n_cc
ax2 = axes[1]
ax2.bar(top2, vals2, width=0.6, color='tab:green')
ax2.set_xlabel("Nœuds (top n par n_cc)")
ax2.set_ylabel("Nombre de composantes connexes")
ax2.set_title(f"Top {n} impact sur la connexité")
ax1.set_yscale('log')
ax2.tick_params(axis='x', rotation=90)

# --- Figure 3 (Lollipop Chart)
ax3 = axes[2]
y_pos = list(range(len(top3)))
ax3.hlines(y=y_pos, xmin=0, xmax=delta_vals, color='gray', linewidth=1)
ax3.plot(delta_vals, y_pos, 'o', markersize=8, color='purple')
ax3.set_yticks(y_pos)
ax3.set_yticklabels(top3)
ax3.set_xlabel("Δ |λ| moyenne (frein à la diffusion)")
ax3.set_title(f"Top {n} nœuds ralentissant la diffusion")
ax3.grid(axis='x', linestyle='--', alpha=0.7)

plt.savefig("graphs/epidemie.png")
plt.show()