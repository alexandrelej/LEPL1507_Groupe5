import tkinter as tk

def afficher_reponse():
    reponse = var_reponse.get()
    label_resultat.config(text=f"Vous avez choisi : {reponse}")

# Création de la fenêtre principale
root = tk.Tk()
root.title("Amélioration du trafic aérien national")
root.geometry("500x300")  # Définit la taille de la fenêtre (largeur x hauteur)

# Ajout d'un label avec une question
label_question = tk.Label(root, text="Quel critère souhaitez-vous minimiser ?", font=("Arial", 12))
label_question.pack(pady=10)

# Variable pour stocker la réponse
var_reponse = tk.StringVar(value="Distance parcourue")  # Valeur par défaut

# Création des boutons radio
choix1 = tk.Radiobutton(root, text="Distance parcourue", variable=var_reponse, value="Distance parcourue", font=("Arial", 10))
choix2 = tk.Radiobutton(root, text="Temps total du trajet", variable=var_reponse, value="Temps total du trajet", font=("Arial", 10))
choix3 = tk.Radiobutton(root, text="Prix des billets", variable=var_reponse, value="Prix des billets", font=("Arial", 10))

# Affichage des boutons radio
choix1.pack(pady=2)
choix2.pack(pady=2)
choix3.pack(pady=2)

# Bouton pour valider la réponse
bouton_valider = tk.Button(root, text="Valider", command=afficher_reponse, font=("Arial", 10))
bouton_valider.pack(pady=5)

# Zone d'affichage de la réponse
label_resultat = tk.Label(root, text="", font=("Arial", 10))
label_resultat.pack(pady=10)

# Lancement de la boucle principale
root.mainloop()




