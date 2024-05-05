import numpy as np
import pprint
from colorama import Fore, Style
from prettytable import *

import copy



def menu_principal():
    print("\n----- BIENVENUE DANS NOTRE PROGRAMME DE RÉSOLUTION DE PROBLEMES DE TRANSPORT ! -----")
    print("Menu principal : (Saisir chiffre selon utilisation)\n")
    print(" 1 : Lecture d'un tableau et affichage")
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
    entetes_matrice_couts = ['Fournisseurs'] + [f"L{i+1}" for i in range(len(commandes))] + ['Provisions']
    tableau = PrettyTable(entetes_matrice_couts)
    
    # Pour chaque ligne dans la matrice des coûts, on ajoute le nom du fournisseur P_n, les coûts et la provision
    for i, couts in enumerate(matrice_des_couts):
        # Ajouter le nom du fournisseur (P1, P2, ...) à la ligne
        ligne = [f"S{i+1}"] + couts + [provisions[i]]
        tableau.add_row(ligne)
    
    # On ajoute la dernière ligne pour les commandes
    tableau.add_row(["Commandes"] + commandes + [""])
    tableau.set_style(SINGLE_BORDER)
    print(tableau)


def afficher_proposition_transport_tab_cout(proposition_transport, commandes):
    # On crée les entêtes comprenant une colonne pour les fournisseurs, suivies par une colonne pour chaque client
    entetes_matrice_couts = [f""] + [f"{Fore.GREEN}L{i+1}{Style.RESET_ALL}" for i in range(len(commandes))]
    tableau = PrettyTable(entetes_matrice_couts)
    
    # Pour chaque ligne dans la matrice des coûts, on ajoute le nom du fournisseur S_n
    for i, couts in enumerate(proposition_transport):
        # Convertir les coûts en chaînes de caractères
        couts_str = [str(c) for c in couts]
        # Ajouter le nom du fournisseur (S1, S2, ...) à la ligne
        ligne = [f"{Fore.GREEN}S{i+1}{Style.RESET_ALL}"] + couts_str
        
        # Coloration des cellules en rouge si la valeur est négative
        for j, cout in enumerate(couts):
            if cout < 0:
                ligne[j+1] = f"{Fore.RED}{cout}{Style.RESET_ALL}"
            else:
                ligne[j+1] = f"{Fore.BLUE}{cout}{Style.RESET_ALL}"
        
        tableau.add_row(ligne)
   
    tableau.set_style(SINGLE_BORDER)
    print(tableau)


def proposition_transport_nord_ouest(matrice_couts, provisions, commandes):
    # Initialisation des variables
    nb_fournisseurs = len(matrice_couts)
    nb_clients = len(commandes)
    transport = np.zeros((nb_fournisseurs, nb_clients), dtype=int)
    
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
    
    lignes_actives = np.ones(nb_lignes, dtype=bool)  # Lignes actives
    colonnes_actives = np.ones(nb_colonnes, dtype=bool)  # Colonnes actives
    
    while np.any(provisions) and np.any(commandes):
        penalites = np.zeros(nb_lignes + nb_colonnes)
        
        # Calcul des pénalités pour chaque ligne active
        for i in range(nb_lignes):
            if lignes_actives[i]:
                couts = matrice_couts_np[i, colonnes_actives]
                couts_valides = couts[couts > 0]  # ne pas tenir compte du zéro qui indique une colonne inactive
                if len(couts_valides) > 1:
                    couts_valides_tries = np.sort(couts_valides)
                    penalites[i] = couts_valides_tries[1] - couts_valides_tries[0]
                elif len(couts_valides) == 1:
                    penalites[i] = couts_valides[0]  # s'il n'existe qu'un seul coût, pénaliser par ce coût lui-même

        # Calcul des pénalités pour chaque colonne active
        for j in range(nb_colonnes):
            if colonnes_actives[j]:
                couts = matrice_couts_np[lignes_actives, j]
                couts_valides = couts[couts > 0]  # ne pas tenir compte du zéro qui indique une ligne inactive
                if len(couts_valides) > 1:
                    couts_valides_tries = np.sort(couts_valides)
                    penalites[nb_lignes + j] = couts_valides_tries[1] - couts_valides_tries[0]
                elif len(couts_valides) == 1:
                    penalites[nb_lignes + j] = couts_valides[0]  # s'il n'existe qu'un seul coût, pénaliser par ce coût lui-même
        # Trouver l'index avec la pénalité la plus élevée
        max_index = np.argmax(penalites)
        if penalites[max_index] == 0:
            break  # Arrêter s'il ne reste aucun mouvement valide (c'est-à-dire, toutes les pénalités sont nulles)
        
        if max_index < nb_lignes:
            i = max_index
            indices_valides = np.where(colonnes_actives)[0]
            j = indices_valides[np.argmin(matrice_couts_np[i, indices_valides])]
        else:
            j = max_index - nb_lignes
            indices_valides = np.where(lignes_actives)[0]
            i = indices_valides[np.argmin(matrice_couts_np[indices_valides, j])]
        
        # Allouer autant que possible
        quantite = min(provisions[i], commandes[j])
        transport[i, j] = quantite
        provisions[i] -= quantite
        commandes[j] -= quantite
        
        # Mettre à jour le statut actif
        if provisions[i] == 0:
            lignes_actives[i] = False
        if commandes[j] == 0:
            colonnes_actives[j] = False


    return transport

def table_couts_potentiels(proposition_transport, matrice_couts):
    nb_fournisseurs, nb_clients = proposition_transport.shape
    couts_potentiels = np.zeros((nb_fournisseurs, nb_clients), dtype=int)
    dictionnaire_equation = {"L1":0} #Valeur initiale L1 = 0
    #D'abord toutes les valeurs différentes de 0 dans la proposition de transport
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
            
    #Ensuite le reste des cases 
    for j in range(nb_fournisseurs):
        for i in range(nb_clients):
            if proposition_transport[j][i] == 0:
                couts_potentiels[j][i] = dictionnaire_equation[f"S{j+1}"] - dictionnaire_equation[f"L{i+1}"]

    
    return couts_potentiels

def calculer_couts_potentiels_graphe(proposition_transport, matrice_couts, graphe):
    
    nb_fournisseurs, nb_clients = proposition_transport.shape
    couts_potentiels = np.zeros((nb_fournisseurs, nb_clients), dtype=int)
    matrice_couts = np.array(matrice_couts)

    
    dictionnaire_potentiels = {"L1": 0}
    
    # Établir une file d'attente de nœuds à visiter
    list_to_visit = ['L1']
    visited = set()

    while list_to_visit:
        current_node = list_to_visit.pop(0)
        if current_node not in visited:
            visited.add(current_node)
            if current_node.startswith('S'):
                source_index = int(current_node[1:]) - 1
                for neighbor in graphe[current_node]:
                    client_index = int(neighbor[1:]) - 1
                    if neighbor not in dictionnaire_potentiels:
                        dictionnaire_potentiels[neighbor] = matrice_couts[source_index, client_index] + dictionnaire_potentiels[current_node]
                        list_to_visit.append(neighbor)
            else:
                client_index = int(current_node[1:]) - 1
                for neighbor in graphe[current_node]:
                    source_index = int(neighbor[1:]) - 1
                    if neighbor not in dictionnaire_potentiels:
                        dictionnaire_potentiels[neighbor] = dictionnaire_potentiels[current_node] - matrice_couts[source_index, client_index]
                        list_to_visit.append(neighbor)
    
    # Calculer les coûts potentiels pour chaque connexion possible
    for i in range(nb_fournisseurs):
        for j in range(nb_clients):
            si_noeud = f"S{i+1}"
            li_noeud = f"L{j+1}"
            couts_potentiels[i, j] = dictionnaire_potentiels.get(si_noeud, np.inf) - dictionnaire_potentiels.get(li_noeud, np.inf)
            couts_potentiels[i, j] = -couts_potentiels[i, j]

    return couts_potentiels

def table_couts_marginaux(matrice_couts, tab_couts_potentiels):
    # Initialisation des variables
    nb_fournisseurs, nb_clients = tab_couts_potentiels.shape
    couts_marginaux = np.zeros((nb_fournisseurs, nb_clients), dtype=int)

    # Calcul des coûts marginaux
    for i in range(nb_fournisseurs):
        for j in range(nb_clients):
            couts_marginaux[i][j] = matrice_couts[i][j] - tab_couts_potentiels[i][j]
    
    return couts_marginaux

def construire_graphe_biparti(proposition_transport):
    # Utilisation d'un dictionnaire pour stocker les sommets et les arêtes
    # Ceci est une liste d'adjacence
    graphe = {}
    nb_fournisseurs, nb_clients = proposition_transport.shape
    for i in range(nb_fournisseurs):
        graphe[f"S{i+1}"] = []
        for j in range(nb_clients):
            if proposition_transport[i][j] != 0:
                graphe[f"S{i+1}"].append(f"L{j+1}")
    
    for j in range(nb_clients):
        graphe[f"L{j+1}"] = []
        for i in range(nb_fournisseurs):
            if proposition_transport[i][j] != 0:
                graphe[f"L{j+1}"].append(f"S{i+1}")
    
    return graphe

def verifier_graphe_biparti_arete(graphe):
    # On verifie nb_aretes == nb_sommets - 1
    nb_sommets = len(graphe)
    nb_aretes = 0
    
    # Compter aretes (attention graphe non orienté donc on compte chaque arete une seule fois)
    for sommet, voisins in graphe.items():
        nb_aretes += len(voisins)

    # On divise par 2 car on a compté chaque arête deux fois
    nb_aretes //= 2 

    print(f"Nombre de sommets : {nb_sommets}")
    print(f"Nombre d'arêtes : {nb_aretes}")

    return nb_aretes == nb_sommets - 1


def graphe_biparti_contient_cycle(graphe):
    # Parcourir le graphe en utilisant la recherche en largeur pour détecter les cycles
    def bfs(sommet, visite, parent, chemin):
        visite[sommet] = True
        chemin.append(sommet)
        for voisin in graphe[sommet]:
            if not visite[voisin]:
                cycle = bfs(voisin, visite, sommet, chemin)
                if cycle:
                    return cycle
            elif voisin != parent:
                chemin.append(voisin)
                # Trouver l'index du sommet où le cycle commence
                cycle_debut_index = chemin.index(voisin)
                # Extraire le cycle à partir de cet index
                cycle = chemin[cycle_debut_index:]
                print("Cycle détecté :", cycle)
                return cycle
        chemin.pop()
        return None

    visite = {sommet: False for sommet in graphe}
    for sommet in visite:
        if not visite[sommet]:
            chemin = []
            cycle = bfs(sommet, visite, None, chemin)
            if cycle:
                return cycle
    return None



def graphe_biparti_est_un_arbre(proposition_transport, graphe):

    return verifier_graphe_biparti_arete(graphe) and not graphe_biparti_contient_cycle(graphe)

# Si le graphe contient |V | − p arêtes (avec p > 1), on va artificiellement rajouter les
# p − 1 arêtes ayant les plus petits coûts de transport permettant de former un graphe
# maximalement acyclique.
def rajouter_aretes(proposition_transport, matrice_couts, graphe):
    if not isinstance(matrice_couts, np.ndarray):
        matrice_couts = np.array(matrice_couts)  # Convertir en tableau numpy si ce n'est pas le cas

    indices_non_relie = np.nonzero(proposition_transport == 0)
    i_indices, j_indices = indices_non_relie

    couts_non_relies = matrice_couts[i_indices, j_indices]
    sorted_indices = np.argsort(couts_non_relies)
    sorted_i_indices = i_indices[sorted_indices]
    sorted_j_indices = j_indices[sorted_indices]

    # Proceed with adding edges
    for i, j in zip(sorted_i_indices, sorted_j_indices):
        proposition_transport_temp = proposition_transport.copy()
        graphe_temp = copy.deepcopy(graphe)
        graphe_temp[f'S{i+1}'].append(f'L{j+1}')
        graphe_temp[f'L{j+1}'].append(f'S{i+1}')

        if not graphe_biparti_contient_cycle(graphe_temp):
            graphe[f'S{i+1}'].append(f'L{j+1}')
            graphe[f'L{j+1}'].append(f'S{i+1}')
            print(f'Ajout de l\'arête (S{i+1}, L{j+1})')
            if verifier_graphe_biparti_arete(graphe):
                break

    return proposition_transport

def ajouter_arete_specifique(proposition_transport, graphe, arete):
    i, j = arete
    graphe[f'S{i+1}'].append(f'L{j+1}')
    graphe[f'L{j+1}'].append(f'S{i+1}')

    print(f'Ajout de l\'arête (S{i+1}, L{j+1})')

    return proposition_transport

def trouver_valeur_negative(tab_couts_marginaux):
    # Converti tab en numpy
    tab_np = np.array(tab_couts_marginaux)
    # Trouve la valeur la plus négative et son index
    valeur_negative = np.min(tab_np)
    index_valeur_negative = np.where(tab_np == valeur_negative)
    # Converti l'index en arete du graphe
    arete = (index_valeur_negative[0][0], index_valeur_negative[1][0])
    print(f"La valeur la plus négative est {valeur_negative} pour l'arête S{arete[0]+1} - L{arete[1]+1}")
    if valeur_negative >= 0:
        print("\nLa proposition de transport est optimale\n")

    return (arete, valeur_negative)

def maximisation(proposition_balas_hammer, graphe, arete, cycle):
    # Prendre le maximum des lignes et colonnes de la case de l'arête
    i, j = arete
    max_ligne = np.max(proposition_balas_hammer[i])
    max_colonne = np.max(proposition_balas_hammer[:, j])
    quantite = min(max_ligne, max_colonne)
    print(f"Quantité maximale à déplacer : {quantite}")

    # Mettre à jour la proposition de transport (+ ou - sur le cycle)
    # Le cycle recu est ['S1', 'L1', 'S3', 'L3', 'S1'] il faut extraire les indices
    if cycle:
        cycle_indices = [int(s[1:]) - 1 for s in cycle]
        print(cycle_indices)
        for k in range(len(cycle_indices) - 1):
            #source, client = cycle_indices[k + 1], cycle_indices[k]
            if k % 2 == 0:
                source, client = cycle_indices[k + 1], cycle_indices[k]
                print(f'Arete en cours : S{source+1} - L{client+1}')
                proposition_balas_hammer[client, source] -= quantite
                print(f"Quantité ajoutée : {quantite}")
            else:
                client, source = cycle_indices[k + 1], cycle_indices[k]
                print(f'Arete en cours : L{client+1} - S{source+1}')
                proposition_balas_hammer[client, source] += quantite
                print(f"Quantité retirée : {quantite}")


    return proposition_balas_hammer

def calculer_cout_total(proposition_transport, matrice_couts):
    # Afficher les détails du calcul du coût total
    # On aurait pu simplement faire np.sum(proposition_transport * matrice_couts)
    total = 0
    for i in range(len(proposition_transport)):
        for j in range(len(proposition_transport[i])):
            total += proposition_transport[i][j] * matrice_couts[i][j]
    return total
