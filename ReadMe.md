# Projet 4 — Mathématiques appliquées (LEPL1507)

Ce projet vise à optimiser un réseau aérien mondial en minimisant la fonction objectif suivante : 
$$
f(E) = \frac{1}{N} \sum_{(A_t, A_l) \in J} \text{dist}(A_t, A_l \mid E) + C \cdot |E|
$$

Notre approche consiste à implémenter plusieurs algorithmes, à comparer leurs performances et à analyser les résultats afin de déterminer la meilleure méthode d’optimisation.

**Auteurs :** Joachim De Favereau, Alexandre Lejeune, Florent Thyrion & Charlotte Weynants

---

## 📚 Table des matières

- [Introduction](#introduction)
- [Structure du code](#structure-du-code)
- [Paramètres](#paramètres)
- [Exécution](#exécution)
- [Sorties](#sorties)
- [Interface utilisateur](#interface-utilisateur)

---

## 🧭 Introduction

L’objectif du projet est de construire un réseau de connexions optimales entre aéroports qui respecte certaines contraintes tout en minimisant le nombre de connexions recquises.  
Cela s’inscrit dans une optique de **développement durable**, en limitant les trajets inutiles tout en garantissant un certain nombre de connexions.

---

## 🗂️ Structure du code

| Fichier / Dossier                 | Description |
|----------------------------------|-------------|
| `basic_datasets/`                | Contient les données d'entrée au format CSV |
| ├── `airports.csv`               | Liste des aéroports disponibles |
| ├── `pre_existing_routes.csv`    | Connexions existantes entre les aéroports |
| ├── `waiting_times.csv`          | Temps d’attente moyen par escale |
| ├── `prices.csv`                 | Prix des billets pour chaque connexion |
| ├── `capacities_airports.csv`    | Capacité maximale de chaque aéroport |
| ├── `capacities_connexions.csv`  | Capacité maximale de chaque connexion |
| └── `new_routes.csv`             | Connexions retenues dans le réseau final |
| `python_files/`                  | Contient l’ensemble des scripts Python |
| ├── `create_graphs.py`           | Création des graphes à partir des fichiers CSV et ajout des prix et temps pour la conversion au format JSON |
| ├── `remove_edges.py`            | Implémentation de l’algorithme "Remove Edges" |
| ├── `update_costs.py`            | Implémentation de l’algorithme "Update Costs" |
| ├── `disturbance_result.py`      | Amélioration du réseau par perturbations successives |
| ├── `comparison_algorithms.py`   | Comparaison des algorithmes selon différents critères |
| ├── `direct.py`                  | Solveur direct du problème |
| ├── `direct_test.py`             | Tests du solveur direct |
| ├── `A_major_event.py`           | Simulation d’un événement majeur (ex. : fermeture d’un hub) |
| ├── `B_epidemie.py`              | Simulation d’une épidémie |
| ├── `C_robustesse.py`            | Analyse de la robustesse globale du réseau |
| ├── `main_test.py`               | Étude des objectifs secondaires |
| └── `new_network.py`             | Génère le nouveau réseau optimisé |
| `interface_utilisateur/`         | Interface web pour l’utilisation du réseau |
| ├── `find_shortest_path.py`      | Fonctions pour obtenir les distances, temps et prix des arêtes et pour trouver le chemin le plus court |
| ├── `index.html`                 | Page principale de l'interface |
| ├── `old_index.html`             |  |
| └── `visu.jpg`                   | Image dans l'interface utilisateur |
| `json/`                          | Graphe du nouveau réseau au format JSON |
| └── `all.json`                   | Informations complètes sur les arêtes (distance, coût, temps) |
| `graphs/`                        | Graphiques d’analyse |
| ├── `comparison_C.png`           | Temps et coût en fonction de la valeur de `C` |
| ├── `comparison_J.png`           | Temps et coût en fonction de la taille de la liste `J` |
| ├── `comparison_N_M.png`         | Influence du nombre d’aéroports et connexions |
| ├── `major_events.png`           | Flots maximaux lors d’un événement majeur |
| └── `robustesse_edge_removal.png`| Analyse de la robustesse en cas de suppression d’arêtes |


## ✈️ Fonctionnalités et options

Le script repose sur deux fichiers d'entrée au format CSV :
- `airports.csv` : liste des aéroports disponibles,
- `pre_existing_routes.csv` : connexions existantes entre ces aéroports.

Ces fichiers influencent directement :
- le **temps d'exécution** (selon le nombre d’aéroports et de connexions),
- le **réseau final** généré.

---

### Paramètres personnalisables :
- **C** (*coût d’une arête*) : représente le coût d'ajouter une connexion au réseau.  
  - Plage typique : entre **500** et **3000**.  
  - **500** favorise les trajets les plus courts possibles.  
  - **3000** privilégie la réduction du nombre total de connexions.
  
- **|J|** (*nombre de trajets à assurer*) :  
  Correspond au nombre de voyages qui doivent pouvoir être réalisés dans le réseau final.  
  - Doit être inférieur au nombre total de connexions.
  - Plus |J| est grand, plus le réseau sera dense.

---

## ⚙️ Compilation

Pour générer le nouveau réseau à partir des fichiers CSV, il suffit de lancer le script suivant :

`new_network.py`

---

## 📤 Sorties

- La **liste des connexions sélectionnées** est affichée dans le terminal.
- Un **fichier `new_routes.csv`** est généré, contenant les nouvelles connexions du réseau.

---

## 🌐 Interface utilisateur

Un lien dans le rapport final permet d’accéder à une **interface web** pour rechercher un trajet optimal.

1. **Choisir un critère d’optimisation** :
   - Distance  
   - Temps  
   - Prix  

2. **Sélectionner** :
   - Un **aéroport de départ**
   - Un **aéroport d’arrivée**

3. **Afficher le meilleur trajet** :
   - Liste des aéroports intermédiaires parcourus
   - Distance, durée ou coût total du trajet selon le critère choisi

