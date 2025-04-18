import networkx as nx
import numpy as np
import pandas as pd
import scipy.linalg
import scipy.sparse.linalg
import matplotlib.pyplot as plt
import json



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
with open("json/G_all.json", "r") as f:
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
import matplotlib.pyplot as plt

# Vos dictionnaires d'entrée
# init_eigvals        = {'ABC': -2.3, 'DEF': -1.8, ...}
# init_eigvecs        = {'ABC':  0.45, 'DEF':  0.32, ...}
# n_cc                = {'ABC':   3,   'DEF':   5,   ...}
# average_eigvals     = {'ABC': -1.9, 'DEF': -2.1, ...}

# 1) Transformer en amplitude (valeur absolue)
abs_init_vals = {n: abs(v) for n, v in init_eigvals.items()}
abs_avg_vals  = {n: abs(v) for n, v in average_eigvals.items()}

# 2) Trier les nœuds
nodes1 = sorted(
    abs_init_vals.keys(),
    key=lambda n: (abs_init_vals[n], init_eigvecs.get(n, 0)),
    reverse=True
)
vals1 = [abs_init_vals[n]    for n in nodes1]
vecs1 = [init_eigvecs[n]      for n in nodes1]

nodes2 = sorted(n_cc.keys(), key=lambda n: n_cc[n], reverse=True)
vals2  = [n_cc[n]            for n in nodes2]

nodes3 = sorted(abs_avg_vals.keys(), key=lambda n: abs_avg_vals[n], reverse=True)
vals3  = [abs_avg_vals[n]    for n in nodes3]
mean3  = sum(vals3) / len(vals3)

# 3) Création de la figure à 3 sous‑plots
fig, axes = plt.subplots(1, 3, figsize=(18, 6),constrained_layout=True)

# — Sous‑plot 1 : eigenvecs (barres) + amplitude eigenvals (ligne, axe droit)
ax1 = axes[0]
ax1.bar(nodes1, vecs1, width=0.6, alpha=0.7, label="Composante vecteur propre")
ax1.set_xlabel("Nœuds (triés par amplitude de valeur propre)")
ax1.set_ylabel("Composante de l'eigenvecteur")
ax1.set_yscale('log')
ax1.tick_params(axis='x', rotation=45)

ax1b = ax1.twinx()
ax1b.plot(nodes1, vals1, linestyle='--', marker='o', linewidth=2, label="Amplitude des valeurs propres")
ax1b.set_ylabel("Amplitude des valeurs propres")

ax1.set_title("Amplitude des valeurs propres vs. composantes\n(initial)")
# Légende à l'extérieur du sous‑plot 1
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1b.get_legend_handles_labels()
ax1.legend()

# — Sous‑plot 2 : n_cc histogramme
ax2 = axes[1]
ax2.bar(nodes2, vals2, width=0.6, color='tab:green')
ax2.set_xlabel("Nœuds (triés par n_cc)")
ax2.set_ylabel("Nombre de composantes connexes")
ax2.set_title("Composantes connexes\npar nœud")
ax2.tick_params(axis='x', rotation=45)

# — Sous‑plot 3 : average_eigvals histogramme + ligne de la moyenne
ax3 = axes[2]
ax3.bar(nodes3, vals3, width=0.6, color='tab:purple')
ax3.axhline(mean3, color='black', linestyle='--', linewidth=2, label=f"Moyenne = {mean3:.2f}")
ax3.set_xlabel("Nœuds (triés par amplitude de valeur propre moyenne)")
ax3.set_ylabel("Amplitude de la valeur propre moyenne")
ax3.set_title("Amplitude moyenne des valeurs propres\npar nœud")
ax3.tick_params(axis='x', rotation=45)
ax3.legend()


plt.savefig("combined_figure.png")
plt.show()
