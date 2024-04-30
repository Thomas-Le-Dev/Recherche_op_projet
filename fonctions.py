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
    matrice_couts_np = np.array(matrice_couts, dtype=float)
    nb_lignes, nb_colonnes = len(provisions), len(commandes)
    transport = np.zeros((nb_lignes, nb_colonnes), dtype=int)
    
    active_rows = np.ones(nb_lignes, dtype=bool)  # Lignes actives
    active_cols = np.ones(nb_colonnes, dtype=bool)  # Colonnes actives
    
    while np.any(provisions) and np.any(commandes):
        penalites = np.zeros(nb_lignes + nb_colonnes)
        
        # Calcul des pénalités pour chaque ligne active
        for i in range(nb_lignes):
            if active_rows[i]:
                costs = matrice_couts_np[i, active_cols]
                valid_costs = costs[costs > 0]  # ignore zero as it indicates inactive column
                if len(valid_costs) > 1:
                    sorted_costs = np.sort(valid_costs)
                    penalites[i] = sorted_costs[1] - sorted_costs[0]
                elif len(valid_costs) == 1:
                    penalites[i] = valid_costs[0]  # if only one cost exists, penalize by that cost itself

        # Calcul des pénalités pour chaque colonne active
        for j in range(nb_colonnes):
            if active_cols[j]:
                costs = matrice_couts_np[active_rows, j]
                valid_costs = costs[costs > 0]  # ignore zero as it indicates inactive row
                if len(valid_costs) > 1:
                    sorted_costs = np.sort(valid_costs)
                    penalites[nb_lignes + j] = sorted_costs[1] - sorted_costs[0]
                elif len(valid_costs) == 1:
                    penalites[nb_lignes + j] = valid_costs[0]  # if only one cost exists, penalize by that cost itself

        # Find the index with the highest penalty
        max_index = np.argmax(penalites)
        if penalites[max_index] == 0:
            break  # Break if no valid moves left (i.e., all penalties are zero)
        
        if max_index < nb_lignes:
            i = max_index
            valid_indices = np.where(active_cols)[0]
            j = valid_indices[np.argmin(matrice_couts_np[i, valid_indices])]
        else:
            j = max_index - nb_lignes
            valid_indices = np.where(active_rows)[0]
            i = valid_indices[np.argmin(matrice_couts_np[valid_indices, j])]
        
        # Allocate as much as possible
        quantite = min(provisions[i], commandes[j])
        transport[i, j] = quantite
        provisions[i] -= quantite
        commandes[j] -= quantite
        
        # Update active status
        if provisions[i] == 0:
            active_rows[i] = False
        if commandes[j] == 0:
            active_cols[j] = False


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
