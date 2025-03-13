import numpy as np
from create_random_graphes import create_airport_graph, create_random_subgraph, generate_random_pairs
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx
import random as rd
import time
import multiple_astar as ma
import matplotlib.colors as mcolors
from cycler import cycler
from scipy.optimize import linprog
from scipy.sparse import csc_matrix

# Chemins vers les fichiers CSV
airports_csv = "../basic_datasets/airports.csv"
routes_csv = "../basic_datasets/pre_existing_routes.csv"
n = 30
m = 100
j = 50
C = 3000

# Créer le graphe complet
airport_graph = create_airport_graph(airports_csv, routes_csv)
# Générer un sous-graphe aléatoire
G = create_random_subgraph(airport_graph, n, m)
G_reweighted = G.copy()
Trajets = generate_random_pairs(G, j)
# Créer la matrice d'incidence en sparse format
M = nx.incidence_matrix(G, oriented=True).toarray()
# double the number of columns to double each edge
M = np.concatenate((M, M), axis=1)
# Créer le vecteur des distances en sparse format
distances = np.array([d['distance'] for u, v, d in G.edges(data=True)])/j
# double the distances with the second edge being more expensive
distances = np.concatenate((distances, distances + C))
# Approximation multiple A* pour trouver le graphe optimal parmis plusieurs runs
multi_astar_cost_best = float('inf')
best_G_mult = None
for i in range(5):
    G_mult, rsubgraph = ma.approx_multiple_astar(G, Trajets, C, iterations=max(n, m))
    multi_astar_cost = sum([nx.shortest_path_length(G_mult, start, end, weight="distance") for start, end in Trajets]) / len(Trajets) + C * len(G_mult.edges())
    print("multi_astar_cost at iteration ",i," :", multi_astar_cost)
    if multi_astar_cost < multi_astar_cost_best:
        multi_astar_cost_best = multi_astar_cost
        best_G_mult = G_mult
print("Initial multi_astar_cost:", multi_astar_cost_best)

# Mapping des arêtes aux identifiants
edge_to_id = {i: edge for i, edge in enumerate(G.edges())}
id_to_edge = {edge: i for i, edge in enumerate(G.edges())}
id_to_node = {node: i for i, node in enumerate(G.nodes())}
node_to_id = {i: node for i, node in enumerate(G.nodes())}

# Définition d'une fonction pour obtenir les dual variables
def get_dual_variables(Trajet, H):
    """
    Compute the dual variables associated with capacity constraints
    of a minimum cost flow problem on a graph.
    
    Parameters:
    H (numpy array): Vector of edge capacities.
    Trajet (tuple): Tuple containing the start and end nodes of the path.
    
    Returns:
    dict: Dual variables for each edge in the graph.
    """
    # initialize the b vector as a sparse zeros vector
    t = np.zeros(G.number_of_nodes())
    # set the b vector to 1 and -1 for the start and end nodes of the path
    t[id_to_node[Trajet[0]]] = -1
    t[id_to_node[Trajet[1]]] = 1
    # set the upper bound of the constraints from H
    # so we clip the values to be in the interval (epsilon, 1-epsilon)
    epsilon = 1e-2
    epsilon = 0
    H_clipped = np.clip(H, epsilon, 1-epsilon)
    bounds = [(0, H_clipped[i]) for i in range(G.number_of_edges())]
    # Add the bounds for the second set of variables
    bounds += [(0, None) for i in range(G.number_of_edges())]
    # solve the linear programming problem using the HiGHS method, M_sparse and distances_sparse are the A_eq and c vectors
    res = linprog(c=distances, A_eq=M, b_eq=t, bounds=bounds, method='highs')
    # Check if the problem is feasible
    if not res.success:
        raise ValueError("The linear program is not feasible.")
    # get the total cost
    total_cost = res.fun
    # get the dual variables for the upper bounds (only the first m variables)
    dual_variables = res.upper.marginals[:m]
    return dual_variables, total_cost
# Définition d'une fonction pour "pousser" les valeurs de H vers les entiers
def grad_push_to_int(H, alpha):
    """
    Push the values of H towards integers.
    
    Parameters:
    H (numpy array): Vector of edge capacities.
    alpha (float): Strength of the push.
    
    Returns:
    numpy array: Vector of a gradient pushing the values of H towards integers.
    """
    return alpha * np.sign(1 - 2 * H)
# Définition de la fonction coût et de son gradient basé sur les dual variables
def df(H , frac : int, mode : str = "dual"):
    """
    Calcule la valeur de la fonction coût et son gradient pour un vecteur H donné.
    On laisse la possibilité d'utiliser une méthode de gradient stochastique.
    
    Parameters:
    H (numpy array): Vecteur des poids des arêtes.
    frac (int): Fraction des trajets à utiliser pour le calcul du gradient.
    
    Returns:
    value (float): Valeur de la fonction coût.
    grad (numpy array): Gradient de la fonction coût.
    """
    sample = rd.sample(Trajets, j//frac)
    # si mode = "used_paths", on compte le nombre de fois qu'une arête est utilisée
    if mode == "used_paths":
        # On repondère les arêtes du graphe
        for edge_id in G_reweighted.edges():
            G_reweighted.edges[edge_id]['distance'] += j*C*(1-H[id_to_edge[edge_id]])
        value = sum([nx.shortest_path_length(G_reweighted, start, end, weight="distance") for start, end in Trajets])/j + np.sum(H)*C
        grad = np.ones_like(H)
        for trajet in sample:
            start = trajet[0]
            end = trajet[1]
            path = nx.astar_path(G_reweighted,start,end,weight="distance")
            for i in range(len(path) - 1):
                grad[id_to_edge[(path[i],path[i+1])]] -= frac
        # On repondère les arêtes du graphe
        for edge_id in G_reweighted.edges():
            G_reweighted.edges[edge_id]['distance'] -= j*C*(1-H[id_to_edge[edge_id]])
        grad = grad/np.linalg.norm(grad)
    # si mode = "dual", on calcule les variables duales
    if mode == "dual":
        grad = np.ones_like(H)
        value = np.sum(H)*C
        for trajet in sample:
            dual_vars, cost = get_dual_variables(trajet, H)
            value+=cost*frac
            for i in range(m):
                grad[i] += dual_vars[i]*frac/C
        #renormalize the gradient to have norm of 1
        grad = grad/np.linalg.norm(grad)
    return value, grad*dim**(1/2)

# --- Paramètres ---
num_runs = 5            # Nombre de descentes simultanées
dim = m                 # Dimension de H
lr = 0.05              # Taux d'apprentissage
num_iter = 100           # Nombre d'itérations
alpha = 0.1             # Force du "push" vers les entiers

# --- Initialisation ---
# Chaque run a le même H (initialisé aléatoirement dans [0,1])
if True:
    Hs = np.random.rand(num_runs, dim)
    rand = np.random.rand(dim)
    for run in range(num_runs):
        Hs[run] = rand
else:
    Hs = np.zeros((num_runs, dim))
    for run in range(num_runs):
        for edge_id in best_G_mult.edges():
            Hs[run][id_to_edge[edge_id]] = 1
        Hs[run] += (np.random.rand(dim)-1/2)*1.1
        Hs[run] = np.clip(Hs[run], 0, 1)

# On stocke l'évolution de H pour chaque run et à chaque itération
history_H = np.zeros((num_iter, num_runs, dim))
# On stocke l'évolution des valeurs de f(H) (fonction coût) pour chaque run
cost_history = np.zeros((num_iter, num_runs))
improved_cost = np.zeros(num_runs)

# --- Exécution de la descente de gradient pour chaque run ---
start_time = time.time()
mode = "dual"
for it in range(num_iter):
    
    for r in range(num_runs):
        frac = 1
        if r == 0:
            if it < num_iter//3:
                mode = "dual"
            else:
                mode = "used_paths"
        if r == 1:
            mode = "dual"
        if r == 2:
            mode = "used_paths"
        if r == 3:
            mode = rd.choice(["dual","used_paths"])
        if r == 4:
            if it%2 == 0:
                mode = "dual"
            else:
                mode = "used_paths"
        # Calcul de la fonction coût et de son gradient
        value, grad = df(Hs[r], frac, mode)
        if r == 5:
            value_1, grad_1 = (df(Hs[r], frac, "dual"))
            value_2, grad_2 = (df(Hs[r], frac, "used_paths"))
            value, grad = (value_1+value_2)/2, (grad_1+grad_2)/2
        # Mise à jour de H pour le run r
        Hs[r] = Hs[r] - lr * grad
        # S'assurer que H reste dans [0,1]
        Hs[r] = np.clip(Hs[r], 0, 1)
        
        # Stockage
        history_H[it, r, :] = Hs[r]
        cost_history[it, r] = value

for r in range(num_runs):
    H = (Hs[r]>rd.uniform(0,1)  ).astype(bool) # rounding
    G_small, _ = ma.approx_multiple_astar(G, Trajets, C, iterations=1, H=H, mode="longest")
    improved_cost[r] = sum([nx.shortest_path_length(G_small, start, end, weight="distance") for start, end in Trajets])/len(Trajets) + C * len(G_small.edges())
    print("improved_cost of run ",r," :", improved_cost[r])
end_time = time.time()
print(f"Temps d'exécution : {end_time - start_time:.2f}s")

# --- Visualisation par animation ---
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Sous-figure 1 : Évolution des fonctions coût (courbes pour chaque run)
ax_cost = axes[0]
lines = []
ax_cost.plot([0, num_iter], [multi_astar_cost_best, multi_astar_cost_best], label="Multi_star", linewidth=5)
ax_cost.set_prop_cycle(cycler(color=mcolors.TABLEAU_COLORS))
for r in range(num_runs):
    line, = ax_cost.plot([], [], label=f"Run {r}", marker='o', markersize=4)
    lines.append(line)
    ax_cost.plot([0, num_iter], [improved_cost[r], improved_cost[r]], label=f"improved Run {r}", markersize=4)
ax_cost.set_xlim(0, num_iter)
ax_cost.set_ylim(min(multi_astar_cost_best, np.min(cost_history))*0.9, max(multi_astar_cost_best,np.max(cost_history))*1.1)
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
    sc = ax_scatter.scatter(x_coords, history_H[0, r, :], label=f"Run {r}")
    scatters.append(sc)
ax_scatter.set_xlim(-1, dim+1)
ax_scatter.set_ylim(-0.2, 1.2)
ax_scatter.set_xlabel("Dimension")
ax_scatter.set_ylabel("Valeur de H")
ax_scatter.set_title("Valeurs de H (scatter plot)")
ax_scatter.legend()

# Fonction d'update de l'animation
def update(frame):
    """
    Met à jour les graphiques pour chaque frame de l'animation.
    
    Parameters:
    frame (int): Numéro de la frame actuelle.
    
    Returns:
    list: Liste des objets graphiques mis à jour.
    """
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

# --- Sauvegarde de l'image finale ---
fig_final, ax_final = plt.subplots(figsize=(10, 6))
for r in range(num_runs):
    ax_final.plot(np.arange(num_iter), cost_history[:,r], label=f"Descente {r}", marker='o')
ax_final.set_xlim(-1, num_iter)
ax_final.set_ylim(min(multi_astar_cost_best, np.min(cost_history))*0.9, max(multi_astar_cost_best,np.max(cost_history))*1.1)
ax_final.set_xlabel("Itération")
ax_final.set_ylabel("Valeur de f(H)")
ax_final.set_title("Évolution des fonctions coût")
ax_final.legend()
fig_final.savefig("final_optimization_comparison.png")
plt.close(fig_final)
