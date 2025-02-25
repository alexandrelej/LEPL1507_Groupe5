import pydeck as pdk
import os

# Définir le répertoire de sortie
output_dir = "../visualisation"
os.makedirs(output_dir, exist_ok=True)

def visualize_graph_on_globe(subgraph, shortest_paths):
    """
    Visualise le graphe avec pydeck en mettant en évidence les chemins empruntés.
    """

    # Extraire les informations des nœuds
    node_data = [
        {
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "name": data["name"]
        }
        for _, data in subgraph.nodes(data=True)
    ]

    # Extraire les arêtes du graphe
    edge_data = []
    path_edges = set()  # Set pour stocker les arêtes du chemin le plus court

    # Extraire les chemins empruntés et stocker leurs arêtes
    for (s, t), (path, _) in shortest_paths.items():
        if path:
            for i in range(len(path) - 1):
                path_edges.add((path[i], path[i + 1]))  # Ajouter l'arête au set path_edges

    # Ajouter les arêtes du graphe
    for u, v, data in subgraph.edges(data=True):
        # Vérifier si l'arête fait partie du plus court chemin
        color = [0, 0, 255] if (u, v) in path_edges or (v, u) in path_edges else [0, 255, 0]  # Bleu pour les arêtes du chemin le plus court, vert sinon
        edge_data.append({
            "latitude1": subgraph.nodes[u]["latitude"],
            "longitude1": subgraph.nodes[u]["longitude"],
            "latitude2": subgraph.nodes[v]["latitude"],
            "longitude2": subgraph.nodes[v]["longitude"],
            "weight": data.get("weight", 1),
            "color": color
        })

    # Couche des nœuds (en rouge)
    points_layer = pdk.Layer(
        "ScatterplotLayer",
        node_data,
        get_position=["longitude", "latitude"],
        get_radius=50000,
        get_fill_color=[255, 0, 0],  # Rouge
        pickable=True,
        auto_highlight=True
    )

    # Couche des arêtes (vertes ou bleues)
    lines_layer = pdk.Layer(
        "LineLayer",
        edge_data,
        get_source_position=lambda d: [d["longitude1"], d["latitude1"]],
        get_target_position=lambda d: [d["longitude2"], d["latitude2"]],
        get_width=4,
        get_color="color"  # Utilise la couleur définie dans "color"
    )

    # Configurer la vue
    view_state = pdk.ViewState(
        latitude=20.0,
        longitude=0.0,
        zoom=2,  # Zoom ajusté
        pitch=40,
        bearing=0
    )

    # Création du Deck
    deck = pdk.Deck(
        layers=[points_layer, lines_layer],
        initial_view_state=view_state,
        tooltip={"text": "{name}"}
    )

    # Export en HTML
    output_file = os.path.join(output_dir, "airport_graph_on_globe.html")
    deck.to_html(output_file)

    print(f"Visualisation enregistrée dans {output_file}")
