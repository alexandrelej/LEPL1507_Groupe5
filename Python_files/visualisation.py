import pydeck as pdk

def visualize_graph_on_globe(subgraph):
    """
    Visualise le graphe sur un globe terrestre à l'aide de pydeck.
    Affiche les poids des arêtes et ajoute un tooltip pour les arêtes.
    """
    # Extraire les informations des nœuds
    node_data = []
    for node in subgraph.nodes(data=True):
        node_data.append({
            'latitude': node[1]['latitude'],
            'longitude': node[1]['longitude'],
            'name': node[1]['name']
        })

    # Extraire les arêtes du sous-graphe avec les poids
    edge_data = []
    for edge in subgraph.edges(data=True):  # On prend aussi les données d'arête
        node1 = subgraph.nodes[edge[0]]
        node2 = subgraph.nodes[edge[1]]
        weight = edge[2].get('weight', 1)  # Par défaut, poids = 1 si non spécifié
        edge_data.append({
            'latitude1': node1['latitude'],
            'longitude1': node1['longitude'],
            'latitude2': node2['latitude'],
            'longitude2': node2['longitude'],
            'weight': weight,
            'node1': node1['name'],  # Ajouter le nom des nœuds
            'node2': node2['name'],  # Ajouter le nom des nœuds
        })

    # Créer les couches pour les points (nœuds) et les lignes (arêtes)
    points_layer = pdk.Layer(
        "ScatterplotLayer",
        node_data,
        get_position=["longitude", "latitude"],
        get_radius=50000,
        get_fill_color=[255, 0, 0],
        pickable=True,
        auto_highlight=True
    )

    # Créer une couche de lignes (arêtes) avec un poids variable
    lines_layer = pdk.Layer(
        "LineLayer",
        edge_data,
        get_source_position=["longitude1", "latitude1"],
        get_target_position=["longitude2", "latitude2"],
        get_width="weight",  # La largeur des arêtes est proportionnelle au poids
        get_color=[0, 255, 0],
        pickable=True,
        auto_highlight=True,
        tooltip={"text": "Poids: {weight}, Connexion: {node1} - {node2}"}  # Tooltip pour les arêtes
    )

    # Configure the view
    view_state = pdk.ViewState(
        latitude=20.0,
        longitude=0.0,
        zoom=1,
        pitch=50,
        bearing=0
    )

    # Créer le deck
    deck = pdk.Deck(
        layers=[points_layer, lines_layer],
        initial_view_state=view_state,
        tooltip={"text": "{name}"}
    )

    # Afficher la visualisation
    deck.to_html("airport_graph_on_globe.html")
