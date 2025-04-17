import random
import networkx as nx
from update_costs import Update_costs

def compute_cost(G: nx.DiGraph, C: float) -> float:
    """
    Calcule le coût total d’un graphe en combinant la somme pondérée des arêtes et une pénalité
    proportionnelle au nombre d'arêtes. 
    
    Retourne le coût total (float).
    """
    return G.size(weight="weight") + C * len(G.edges)


def disturbance(G_reweighted: nx.DiGraph, random_subgraph: nx.DiGraph, trajets: list[tuple[str, str]], C: float, iterations: int = 1):
    """
    Perturbe un sous-graphe en retirant aléatoirement un nœud «sûr» (ne bloquant aucun trajet),
    puis relance l’optimisation. Si le coût diminue, la nouvelle solution est conservée.
    
    Retourne :
      - le nouveau graphe optimisé,
      - un booléen indiquant une amélioration,
      - le nouveau coût,
      - la différence de coût.
    """
    
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
    """
    Applique la fonction de perturbation plusieurs fois afin d’explorer l’espace des solutions 
    et améliorer itérativement le graphe initial. Affiche les évolutions du coût.

    Retourne le graphe final optimisé après perturbations.
    """
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
    """
    Lance plusieurs optimisations indépendantes, fusionne les résultats, optimise à nouveau 
    le graphe fusionné, puis applique une phase de perturbation pour réduire le coût final.

    Retourne le graphe final optimisé.
    """
    
    print("→ Phase 1 : Exécution multiple de Update_costs")
    graphs = []
    best_graph = None
    best_cost = float("inf")

    for i in range(5):
        g, _ = Update_costs(random_subgraph, trajets, C)
        cost = compute_cost(g, C)
        graphs.append(g)

        print(f"  - Run {i+1} → Nodes: {len(g.nodes)}, Cost: {cost:.2f}")

        if cost < best_cost:
            best_cost = cost
            best_graph = g

    print(f"→ Meilleur graphe initial → Cost: {best_cost:.2f}, Nodes: {len(best_graph.nodes)}")

    # ---------------------
    print("\n→ Phase 2 : Fusion des graphes")
    fused_graph = nx.DiGraph()
    for g in graphs:
        fused_graph = nx.compose(fused_graph, g)

    print(f"  - Fused graph → Nodes: {len(fused_graph.nodes)}, Edges: {len(fused_graph.edges)}")

    # ---------------------
    print("\n→ Phase 3 : Nouvelle optimisation sur graphe fusionné")
    optimized_graph, _ = Update_costs(fused_graph, trajets, C)
    optimized_cost = compute_cost(optimized_graph, C)
    print(f"  - Optimized → Nodes: {len(optimized_graph.nodes)}, Cost: {optimized_cost:.2f}")

    # ---------------------
    print("\n→ Phase 4 : Comparaison avec le meilleur des exécutions initiales")
    if optimized_cost < best_cost:
        print(f"✅ Le graphe fusionné optimisé est meilleur ({optimized_cost:.2f} < {best_cost:.2f})")
        best_graph = optimized_graph
        best_cost = optimized_cost
    else:
        print(f"❌ Le meilleur graphe initial reste le plus performant ({best_cost:.2f})")


    print("\n→ Phase 5 : Perturbation")
    final_graph = test_disturbance(best_graph, fused_graph, trajets, C)

    return final_graph
