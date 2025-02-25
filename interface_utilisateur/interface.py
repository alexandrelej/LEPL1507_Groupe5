import tkinter as tk
from PIL import Image, ImageTk
import json
import networkx as nx
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Python_files')))
import A_star

critere_minimisation = ""
aeroport_depart = ""
aeroport_arrivee = ""

def afficher_reponse():
    global critere_minimisation, aeroport_depart, aeroport_arrivee
    
    critere_minimisation = var_reponse.get()
    aeroport_depart = entry_depart.get() 
    aeroport_arrivee = entry_arrivee.get()  
    

    label_resultat.config(text=f"Critère choisi : {critere_minimisation}\n"
                              f"Aéroport de départ : {aeroport_depart}\n"
                              f"Aéroport d'arrivée : {aeroport_arrivee}")
    
    if critere_minimisation == "Temps total du trajet" or critere_minimisation == "Prix des billets":
        label_resultat.config(text="Pas encore d'algo, patience...")
    
    elif critere_minimisation == "Distance parcourue":
        with open("../json/graph.json", "r") as f:
            data = json.load(f)
            G = nx.node_link_graph(data)
            
            # Vérifier si les nœuds existent dans le graphe
            if aeroport_depart not in G or aeroport_arrivee not in G:
                label_resultat.config(text="Erreur : l'un des aéroports n'existe pas dans le graphe.")
            else:
                try:
                    path = nx.shortest_path(G, source=aeroport_depart, target=aeroport_arrivee, weight="distance")
                    path_string = " -> ".join(path)
                    label_resultat.config(text=path_string)
                except nx.NetworkXNoPath:
                    label_resultat.config(text=f"Erreur : aucun chemin trouvé entre {aeroport_depart} et {aeroport_arrivee}.")

root = tk.Tk()
root.title("Amélioration du trafic aérien national")
root.geometry("600x400")  


image_path = "../images/avion-20966179.png"  
image = Image.open(image_path)
image = image.resize((150, 100))  
photo = ImageTk.PhotoImage(image)

label_image = tk.Label(root, image=photo)
label_image.grid(row=0, column=0, columnspan=2, pady=10) 


label_question = tk.Label(root, text="Quel critère souhaitez-vous minimiser ?", font=("Arial", 12))
label_question.grid(row=1, column=0, columnspan=2, pady=10)


var_reponse = tk.StringVar(value="Distance parcourue") 

choix1 = tk.Radiobutton(root, text="Distance parcourue", variable=var_reponse, value="Distance parcourue", font=("Arial", 10))
choix2 = tk.Radiobutton(root, text="Temps total du trajet", variable=var_reponse, value="Temps total du trajet", font=("Arial", 10))
choix3 = tk.Radiobutton(root, text="Prix des billets", variable=var_reponse, value="Prix des billets", font=("Arial", 10))

choix1.grid(row=2, column=0, padx=10, pady=2)
choix2.grid(row=3, column=0, padx=10, pady=2)
choix3.grid(row=4, column=0, padx=10, pady=2)


label_depart = tk.Label(root, text="Aéroport de départ :")
label_depart.grid(row=5, column=0, pady=5, sticky="e")  

entry_depart = tk.Entry(root, font=("Arial", 10))
entry_depart.grid(row=5, column=1, pady=5, padx=5) 

label_arrivee = tk.Label(root, text="Aéroport d'arrivée :")
label_arrivee.grid(row=6, column=0, pady=5, sticky="e") 

entry_arrivee = tk.Entry(root, font=("Arial", 10))
entry_arrivee.grid(row=6, column=1, pady=5, padx=5) 


bouton_valider = tk.Button(root, text="Valider", command=afficher_reponse, font=("Arial", 10))
bouton_valider.grid(row=7, column=0, columnspan=2, pady=10)

label_resultat = tk.Label(root, text="", font=("Arial", 10))
label_resultat.grid(row=8, column=0, columnspan=2, pady=10)

root.mainloop()






