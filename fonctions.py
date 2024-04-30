import numpy as np
import pprint

from prettytable import *



def menu_principal():
    print("\n----- BIENVENUE DANS NOTRE PROGRAMME DE RÉSOLUTION DE PROBLEMES DE TRANSPORT ! -----")
    print("Menu principal : (Saisir chiffre selon utilisation)\n")
    print(" 1 : Lecture d'un tableau et affichage")
    print(" 2 : Fixer la proposition initiale")
    print(" 0 : Quitter\n")



def lire_donnees(chemin_fichier):
    with open(chemin_fichier, 'r') as fichier:
        contenu = fichier.readlines()
    
    # Initialisation de la matrice des coûts et des listes pour les provisions et les demandes
    matrice_des_couts = []
    provisions = []
    commandes = []

    for i, ligne in enumerate(contenu):
        valeurs = [int(val) for val in ligne.strip().split()]
        if i == 0:
            # La première ligne contient le nombre de fournisseurs et de clients, pas nécessaire si gestion autre part
             continue
        if i <= int(contenu[0].split()[0]):  # Utilise le premier nombre de la première ligne pour le nb de fournisseurs
            matrice_des_couts.append(valeurs[:-1])  # Toutes les valeurs sauf la dernière
            provisions.append(valeurs[-1])  # La dernière valeur est la provision du fournisseur
        else:
            # La dernière ligne traite les commandes des clients
            commandes = valeurs
    print(f"Matrice des coûts : {matrice_des_couts}")
    print(f"Provisions : {provisions}")
    print(f"Commandes : {commandes}")
    return matrice_des_couts, provisions, commandes


def selectionner_probleme():
    while True:
        choix = input("Choisissez le problème à résoudre (1 à 12) : ")
        if choix.isdigit() and 1 <= int(choix) <= 12:
            return int(choix)
        else:
            print("Entrée invalide. Veuillez entrer un nombre entre 1 et 12.")



def afficher_donnees(matrice_des_couts, provisions, commandes):
    # On crée les entêtes comprenant une colonne pour les fournisseurs, suivies par une colonne pour chaque client, et une pour les provisions
    entetes_matrice_couts = ['Fournisseurs'] + [f"C{i+1}" for i in range(len(commandes))] + ['Provisions']
    tableau = PrettyTable(entetes_matrice_couts)
    
    # Pour chaque ligne dans la matrice des coûts, on ajoute le nom du fournisseur P_n, les coûts et la provision
    for i, couts in enumerate(matrice_des_couts):
        # Ajouter le nom du fournisseur (P1, P2, ...) à la ligne
        ligne = [f"P{i+1}"] + couts + [provisions[i]]
        tableau.add_row(ligne)
    
    # On ajoute la dernière ligne pour les commandes
    tableau.add_row(["Commandes"] + commandes + [""])
    tableau.set_style(SINGLE_BORDER)
    print(tableau)


def proposition_transport_nord_ouest(matrice_couts, provisions, commandes):
    # Initialisation des variables
    nb_fournisseurs = len(matrice_couts)
    nb_clients = len(commandes)
    transport = np.zeros((nb_fournisseurs, nb_clients))
    
    # Calcul de la proposition de transport
    for i in range(nb_fournisseurs):
        for j in range(nb_clients):
            transport[i, j] = min(provisions[i], commandes[j])
            provisions[i] -= transport[i, j]
            commandes[j] -= transport[i, j]
    
    return transport


def proposition_transport_balas_hammer(matrice_couts, provisions, commandes):
    matrice_couts_np = np.array(matrice_couts)  # Convertir la liste en une matrice NumPy
    nb_lignes, nb_colonnes = len(provisions), len(commandes)
    transport = np.full((nb_lignes, nb_colonnes), -1)
    
    while np.any(transport == -1):
        penalites = []    
        # Calcul des pénalités pour chaque ligne
        for i in range(nb_lignes):
            valeurs = sorted(matrice_couts_np[i][:nb_colonnes])
            penalites.append(abs(valeurs[0] - valeurs[1]))
        
        # Calcul des pénalités pour chaque colonne
        for i in range(nb_colonnes):
            valeurs = sorted([matrice_couts_np[j][i] for j in range(nb_lignes)])
            penalites.append(abs(valeurs[0] - valeurs[1])) 

        # Trouver l'index de la ligne/colonne avec la plus grande pénalité
        max_penalites_index = np.argmax(penalites)
        max_penalites = penalites[max_penalites_index]
        
        # Si la plus grande pénalité est négative ou nulle, la solution est optimale
        #if max_penalites <= 0:
            #break

        if max_penalites_index < nb_lignes:
            ligne = max_penalites_index
            colonne = np.argmin(matrice_couts_np[ligne,:])
        else:
            colonne = max_penalites_index - nb_lignes
            ligne = np.argmin(matrice_couts_np[:,colonne])
        
        # Allocation maximale permise à la case avec le coût de transport le plus bas
        quantite = min(provisions[ligne], commandes[colonne])
        
        # Mise a jour des quantite de provisions et commandes
        provisions[ligne] -= quantite
        commandes[colonne] -= quantite
    
        # Remplacement du reste de la ligne par 0 sauf la case affectée
        if provisions[ligne] == 0:
            matrice_couts_np[ligne,:] = 0
            transport[ligne,:] = 0
        
        # Remplacement du reste de la colonne par 0 sauf la case affectée
        if commandes[colonne] == 0:
            matrice_couts_np[:,colonne][matrice_couts_np[:,colonne] != np.inf] = 0
            transport[:,colonne][matrice_couts_np[:,colonne] != np.inf] = 0
        transport[ligne, colonne] = quantite
        
        """
        # Exclure les lignes et les colonnes avec des quantités nulles de la prochaine itération
        indices_lignes_non_nulles = np.where(np.sum(transport, axis=1) > 0)[0]
        indices_colonnes_non_nulles = np.where(np.sum(transport, axis=0) > 0)[0]
        matrice_couts_np = matrice_couts_np[indices_lignes_non_nulles[:, None], :][:, indices_colonnes_non_nulles]
        provisions = provisions[indices_lignes_non_nulles]
        commandes = commandes[indices_colonnes_non_nulles]
        transport = transport[indices_lignes_non_nulles[:, None], indices_colonnes_non_nulles]
        """
        break
    return transport

def table_couts_potentiels(proposition_transport, matrice_couts):
    nb_fournisseurs, nb_clients = proposition_transport.shape
    couts_potentiels = np.zeros((nb_fournisseurs, nb_clients))
    dictionnaire_equation = {"L1":0} #Valeur initiale L1 = 0
    #D'abord toutes les valeurs différentes de 0 dans le tab nord ouest
    for i in range(0, nb_fournisseurs):
        for j in range(0, nb_clients):
            if proposition_transport[i][j] != 0:
                couts_potentiels[i][j] = matrice_couts[i][j]

    #Remplissage dico
    for j in range(nb_fournisseurs):
        for i in range(nb_clients):
            if proposition_transport[j][i] != 0:
                if(f"S{j+1}" in dictionnaire_equation):
                    dictionnaire_equation[f"L{i+1}"] = dictionnaire_equation[f"S{j+1}"] - matrice_couts[j][i]
                else:
                    dictionnaire_equation[f"S{j+1}"] = matrice_couts[j][i] + dictionnaire_equation[f"L{i+1}"]
    pprint.pprint(dictionnaire_equation)
            
    #Ensuite le reste des cases 
    for j in range(nb_fournisseurs):
        for i in range(nb_clients):
            if proposition_transport[j][i] == 0:
                couts_potentiels[j][i] = dictionnaire_equation[f"S{j+1}"] - dictionnaire_equation[f"L{i+1}"]

    
    return couts_potentiels


def table_couts_marginaux(matrice_couts, tab_couts_potentiels):
    # Initialisation des variables
    nb_fournisseurs, nb_clients = tab_couts_potentiels.shape
    couts_marginaux = np.zeros((nb_fournisseurs, nb_clients))

    # Calcul des coûts marginaux
    for i in range(nb_fournisseurs):
        for j in range(nb_clients):
            couts_marginaux[i][j] = matrice_couts[i][j] - tab_couts_potentiels[i][j]
    
    return couts_marginaux
