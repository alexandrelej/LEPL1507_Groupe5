import random
import networkx as nx
from update_costs import Update_costs

def compute_cost(G: nx.DiGraph, C: float) -> float:
    return G.size(weight="weight") + C * len(G.nodes)

def disturbance(G_reweighted: nx.DiGraph, random_subgraph: nx.DiGraph, trajets: list[tuple[str, str]], C: float, iterations: int = 1):
    cost_before = compute_cost(G_reweighted, C)
    candidate_nodes = list(set(G_reweighted.nodes).intersection(random_subgraph.nodes))

    safe_nodes = []
    for node in candidate_nodes:
        temp_graph = random_subgraph.copy()
        temp_graph.remove_node(node)

        valid = True
        for start, end in trajets:
            if start not in temp_graph or end not in temp_graph or not nx.has_path(temp_graph, start, end):
                valid = False
                break
        if valid:
            safe_nodes.append(node)

    if not safe_nodes:
        return G_reweighted, False, cost_before, 0.0

    node_to_remove = random.choice(safe_nodes)
    disturbed_subgraph = random_subgraph.copy()
    disturbed_subgraph.remove_node(node_to_remove)

    new_G_reweighted, _ = Update_costs(disturbed_subgraph, trajets, C, iterations)
    cost_after = compute_cost(new_G_reweighted, C)
    improved = cost_after < cost_before
    cost_diff = cost_before - cost_after

    return new_G_reweighted, improved, cost_after, cost_diff

def test_disturbance(G_reweighted, random_subgraph, listJ, C):
    n_iter = len(G_reweighted.nodes)
    current_graph = G_reweighted
    current_cost = compute_cost(current_graph, C)

    print(f"[Initial] Cost: {current_cost:.2f} | Nodes: {len(current_graph.nodes)}")

    for i in range(n_iter):
        new_graph, improved, new_cost, delta = disturbance(current_graph, random_subgraph, listJ, C)

        if improved:
            print(f"[Iteration {i+1}] Improved! ΔCost = {delta:.2f} | New Cost = {new_cost:.2f}")
            current_graph = new_graph
            current_cost = new_cost
        else:
            print(f"[Iteration {i+1}] No improvement.")

    print(f"\n[Final] Cost: {current_cost:.2f} | Nodes: {len(current_graph.nodes)}")
    return current_graph

def multi_optimize_and_disturb(random_subgraph, trajets, C):
    print("→ Phase 1 : Exécution multiple de approx_multiple_astar")
    graphs = []
    for i in range(5):
        g, _ = Update_costs(random_subgraph, trajets, C)
        graphs.append(g)
        print(f"  - Run {i+1} → Nodes: {len(g.nodes)}, Cost: {compute_cost(g, C):.2f}")

    print("→ Phase 2 : Fusion des graphes")
    fused_graph = nx.DiGraph()
    for g in graphs:
        fused_graph = nx.compose(fused_graph, g)

    print(f"  - Fused graph → Nodes: {len(fused_graph.nodes)}, Edges: {len(fused_graph.edges)}")

    print("→ Phase 3 : Nouvelle optimisation sur graphe fusionné")
    optimized_graph, _ = approx_multiple_astar(fused_graph, trajets, C)
    print(f"  - Optimized → Nodes: {len(optimized_graph.nodes)}, Cost: {compute_cost(optimized_graph, C):.2f}")

    print("→ Phase 4 : Perturbation")
    final_graph = test_disturbance(optimized_graph, fused_graph, trajets, C)

    return final_graph
