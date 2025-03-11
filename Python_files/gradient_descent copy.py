import numpy as np
from create_random_graphes import create_airport_graph, create_random_subgraph, generate_random_pairs
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx
import random as rd


# Chemins vers les fichiers CSV
airports_csv = "../basic_datasets/airports.csv"
routes_csv = "../basic_datasets/pre_existing_routes.csv"
n = 30
m = 100
j = 30
C = 1000
# Créer le graphe complet
airport_graph = create_airport_graph(airports_csv, routes_csv)
# Générer un sous-graphe aléatoire
G = create_random_subgraph(airport_graph, n, m)
Trajets = generate_random_pairs(G, j)


edge_to_id = {i: edge for i, edge in enumerate(G.edges())}
id_to_edge = {edge: i for i, edge in enumerate(G.edges())}
# Définition d'une fonction d'exemple : f(H) = somme((H-0.5)^2)
def df(H):
    value = np.sum(H)
    G_reweighted = G.copy()
    N = len(Trajets)
    for edge_id in G_reweighted.edges():
        G_reweighted.edges[edge_id]['distance'] += N*C*(1-H[id_to_edge[edge_id]])
    
    grad = np.ones_like(H)
    for trajet in Trajets:
        start = trajet[0]
        end = trajet[1]
        path = nx.astar_path(G_reweighted,start,end,weight="distance")
        value+= nx.astar_path_length(G_reweighted,start,end,weight="distance")
        for i in range(len(path) - 1):
                    grad[id_to_edge[(path[i],path[i+1])]] -= 1
        

    return value, grad
def get_alpha(i,iter):
    alpha = 0.2
    return alpha
# Fonction de gradient pour pousser H vers les valeurs entières (0 ou 1)
def grad_push_to_int(H, alpha):
    # Pour H_i < 0.5, 1 - 2H_i > 0 : on pousse vers 0
    # Pour H_i > 0.5, 1 - 2H_i < 0 : on pousse vers 1
    return alpha * np.sign(1 - 2 * H)
# --- Paramètres ---
num_runs = 3          # Nombre de descentes simultanées
dim = m              # Dimension de H
lr = 0.01             # Taux d'apprentissage
num_iter = 100        # Nombre d'itérations
alpha = 0.1           # Force du "push" vers les entiers
# --- Initialisation ---
# Chaque run a son propre vecteur H (initialisé aléatoirement dans [0,1])
Hs = np.random.rand(num_runs, dim)
# On stocke l'évolution de H pour chaque run et à chaque itération
history_H = np.zeros((num_iter, num_runs, dim))
# On stocke l'évolution des valeurs de f(H) (fonction coût) pour chaque run
cost_history = np.zeros((num_iter, num_runs))

# --- Exécution de la descente de gradient pour chaque run ---
for it in range(num_iter):
    for r in range(num_runs):
        # Calcul de la fonction coût et de son gradient
        value, grad = df(Hs[r])
        # Calcul du gradient "push" pour forcer H vers 0 ou 1
        push_grad = grad_push_to_int(Hs[r], alpha)
        # Mise à jour de H pour le run r
        Hs[r] = Hs[r] - lr * (grad + push_grad)
        # S'assurer que H reste dans [0,1]
        Hs[r] = np.clip(Hs[r], 0, 1)
        # Stockage
        history_H[it, r, :] = Hs[r]
        cost_history[it, r] = value

# --- Visualisation par animation ---
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Sous-figure 1 : Évolution des fonctions coût (courbes pour chaque run)
ax_cost = axes[0]
lines = []
for r in range(num_runs):
    line, = ax_cost.plot([], [], label=f"Run {r}", marker='o', markersize=4)
    lines.append(line)
ax_cost.set_xlim(0, num_iter)
ax_cost.set_ylim(np.min(cost_history)*0.9, np.max(cost_history)*1.1)
ax_cost.set_xlabel("Itération")
ax_cost.set_ylabel("Valeur de f(H)")
ax_cost.set_title("Évolution des fonctions coût")
ax_cost.legend()

# Sous-figure 2 : Scatter plot pour visualiser les valeurs de H par run
ax_scatter = axes[1]
# Couleurs pour distinguer chaque run
colors = ['red', 'green', 'blue']
# Création d'un scatter plot pour chaque run
scatters = []
x_coords = np.arange(dim)  # L'axe des x correspond aux indices de dimensions
for r in range(num_runs):
    sc = ax_scatter.scatter(x_coords, history_H[0, r, :], color=colors[r], label=f"Run {r}")
    scatters.append(sc)
ax_scatter.set_xlim(-1, dim+1)
ax_scatter.set_ylim(-0.2, 1.2)
ax_scatter.set_xlabel("Dimension")
ax_scatter.set_ylabel("Valeur de H")
ax_scatter.set_title("Valeurs de H (scatter plot)")
ax_scatter.legend()

# Fonction d'update de l'animation
def update(frame):
    # Mise à jour des courbes de la fonction coût
    for r, line in enumerate(lines):
        line.set_data(np.arange(frame + 1), cost_history[:frame + 1, r])
    ax_cost.set_title(f"Évolution des fonctions coût (itération {frame})")
    
    # Mise à jour des scatter plots
    for r, sc in enumerate(scatters):
        # On met à jour la position verticale des points pour chaque run
        offsets = np.column_stack((x_coords, history_H[frame, r, :]))
        sc.set_offsets(offsets)
    
    return lines + scatters

ani = animation.FuncAnimation(fig, update, frames=num_iter, interval=100, blit=True)

plt.tight_layout()
plt.show()