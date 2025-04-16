import networkx as nx
import numpy as np
import cvxpy as cp
import time

def solve_flow(G: nx.DiGraph, Trajets: list[tuple[str, str]], C: float, flow_binaire=True, Choice_binaire=True, Initialise = False, Verbose=False) -> nx.DiGraph:
    """
    Résout le problème d'optimisation de flux sur un graphe dirigé.

    Paramètres :
    G (nx.DiGraph) : Un graphe dirigé avec des distances sur les arêtes.
    Trajets (list[tuple[str, str]]) : Une liste de couples représentant les nœuds de départ et d'arrivée des trajets.
    C (float) : Une constante utilisée dans la fonction objectif pour pénaliser le nombre d'arêtes choisies.
    flow_binaire (bool, optionnel) : Si True, les variables de flux sont binaires. Si False, les variables de flux sont positives. Par défaut : True.
    Choice_binaire (bool, optionnel) : Si True, les variables de choix sont binaires. Si False, elles sont positives. Par défaut : True.

    Retourne :
    nx.DiGraph : Un nouveau graphe dirigé contenant l’ensemble optimisé d’arêtes.
    """

    
    edge_to_id = {i: edge for i, edge in enumerate(G.edges())}
    id_to_edge = {edge: i for i, edge in enumerate(G.edges())}
    print(edge_to_id[0])
    id_to_node = {node: i for i, node in enumerate(G.nodes())}

    M = nx.incidence_matrix(G, oriented=True)
    n_edge = G.number_of_edges()
    n_node = G.number_of_nodes()
    n_traj = len(Trajets)
    distances = np.array([d['distance'] for u, v, d in G.edges(data=True)])

    # Créer les variables
    if Choice_binaire:
        Choice = cp.Variable(n_edge, boolean=True)
    else:
        Choice = cp.Variable(n_edge, nonneg=True)
    if flow_binaire:
        Flow = cp.Variable((n_edge, n_traj), boolean=True)
    else:
        Flow = cp.Variable((n_edge, n_traj), nonneg=True)

    # Créer les contraintes
    T = np.zeros((n_node, n_traj))
    for ind, Trajet in enumerate(Trajets):
        start = id_to_node[Trajet[0]]
        end = id_to_node[Trajet[1]]
        T[start][ind] = -1
        T[end][ind] = 1

    # Appliquer la contrainte AX <= b (contrainte matricielle)
    constraints = [M @ Flow == T]
    for i in range(n_traj):
        constraints.append(Flow[:, i] <= Choice)

    # Initaliser les variables avec Dijkstra
    if Initialise:
        for i in range(n_traj):
            start = Trajets[i][0]
            end = Trajets[i][1]
            shortest_path = nx.shortest_path(G, source=start, target=end, weight='distance')
            for j in range(len(shortest_path) - 1):
                edge_id = (shortest_path[j], shortest_path[j + 1])
                edge = id_to_edge[edge_id]
                Flow[edge, i] = 1
                Choice[edge] = 1

    # Créer l'objectif
    expression = cp.sum(distances @ Flow)/n_traj + C * cp.sum(Choice)
    objective = cp.Minimize(expression)

    # Créer le problème
    Problem = cp.Problem(objective, constraints)
    print("about to solve")

    # Measure the time taken to solve the problem
    start_time = time.time()
    # Résoudre le problème
    Problem.solve(solver=cp.GLPK_MI, verbose=Verbose, timeLimit=15, options=["--mipgap", "0.01"])
    end_time = time.time()
    print("solved")
    print(f"Time taken to solve the problem: {end_time - start_time} seconds")
    print("Parameters of the problem: flow_binaire =", flow_binaire, ", Choice_binaire =", Choice_binaire)
    # Vérifier que Choice est binaire si Choice_binaire est False
    if not Choice_binaire:
        if not np.all(np.isclose(Choice.value, 0) | np.isclose(Choice.value, 1)):
            print("Choice is not binary.")
            print("Choice.value =", Choice.value)
        else:
            print("Choice is stil binary.")
    
    # Reconstruire le nouveau graphe
    edges_to_take = np.where(Choice.value == True)[0]
    print("edges_to_take =", edges_to_take)
    print(G)

    new_G: nx.DiGraph = G.copy()
    new_G.clear_edges()
    
    for edge in edges_to_take:
        new_G.add_edge(edge_to_id[edge][0], edge_to_id[edge][1])
    print("new_G =", new_G)
    # Trouver la valeur optimale de l'objectif
    print("Valeur optimale de l'objectif :", Problem.value)
    return new_G