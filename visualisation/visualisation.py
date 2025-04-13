import pydeck as pdk
import os

# Définir le répertoire de sortie
output_dir = "visualisation"
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

    # Extraire les arêtes du graphe (en vert)
    edge_data = [
        {
            "latitude1": subgraph.nodes[u]["latitude"],
            "longitude1": subgraph.nodes[u]["longitude"],
            "latitude2": subgraph.nodes[v]["latitude"],
            "longitude2": subgraph.nodes[v]["longitude"],
            "distance": data.get("distance", 1)
        }
        for u, v, data in subgraph.edges(data=True)
    ]

    # Extraire les chemins empruntés (en bleu)
    path_data = []
    for (s, t), (path, _) in shortest_paths.items():
        if path:
            for i in range(len(path) - 1):
                path_data.append({
                    "latitude1": subgraph.nodes[path[i]]["latitude"],
                    "longitude1": subgraph.nodes[path[i]]["longitude"],
                    "latitude2": subgraph.nodes[path[i + 1]]["latitude"],
                    "longitude2": subgraph.nodes[path[i + 1]]["longitude"]
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

    lines_layer = pdk.Layer(
        "LineLayer",
        edge_data,
        get_source_position=["longitude1", "latitude1"],
        get_target_position=["longitude2", "latitude2"],  
        get_width=4,
        get_color=[0, 255, 0]  # Vert
    )


    # Couche des chemins empruntés (en bleu)
    path_layer = pdk.Layer(
        "LineLayer",
        path_data,
        get_source_position=["longitude1", "latitude1"],
        get_target_position=["longitude2", "latitude2"],
        get_width=4,
        get_color=[0, 0, 255]  # Bleu
    )

    # Configurer la vue
    view_state = pdk.ViewState(
        latitude=20.0,
        longitude=0.0,
        zoom=2,  # Zoom ajusté
        pitch=40,
        bearing=0
    )

    # Création du Deck2
    deck = pdk.Deck(
        layers=[points_layer, lines_layer, path_layer],
        initial_view_state=view_state,
        tooltip={"text": "{name}"}
    )


    # Export en HTML
    output_file = os.path.join(output_dir, "airport_graph_on_globe.html")
    deck.to_html(output_file)

    print(f"Visualisation enregistrée dans {output_file}")
