import os
from fonctions import *

menu = 2
while menu != 0:
    menu_principal() # Affichage du menu principal
    menu = int(input("Quelle action souhaitez-vous effectuer ? "))
    # Vérification de la validité de l'entrée utilisateur
    while menu < 0 or menu > 2:
        menu = int(input("Nous ne comprenons pas votre demande. Veuillez entrer 0 ou 1.\nQuelle action voulez vous faire ? "))
    
    if menu == 0:
        print("\nAU REVOIR !\n\nFermeture du programme.\n")

    elif menu == 1:
        # Sélection et affichage d'un tableau de contraintes
        numero_probleme = selectionner_probleme()
        tabs = range(1, 12)
        print(f'Il y a {len(tabs)+1} tableaux de contraintes disponibles')
        matrice_des_couts, provisions, commandes = lire_donnees(f"problemes/probleme{numero_probleme}.txt")
        print(f"Problème {numero_probleme} sélectionné.")
        afficher_donnees(matrice_des_couts, provisions, commandes)

        proposition_nord_ouest = proposition_transport_nord_ouest(matrice_des_couts, provisions.copy(), commandes.copy())
        proposition_balas_hammer = proposition_transport_balas_hammer(matrice_des_couts, provisions.copy(), commandes.copy())
        print("\nTableau de la proposition transport nord ouest :\n")
        print(proposition_nord_ouest)
        print("\nTableau de la proposition transport balas hammer :\n")
        print(proposition_balas_hammer)

        choix_transport = int(input("Choisissez la : \n1 pour nord-ouest\n2 Pour balas-hammer\n"))
        if choix_transport == 1:
            couts_potentiels = table_couts_potentiels(proposition_nord_ouest, matrice_des_couts)
            couts_marginaux = table_couts_marginaux(matrice_des_couts, couts_potentiels)
            print("\nTableau des coûts potentiels :\n")
            print(couts_potentiels)
            print("\nTableau des coûts marginaux :\n")
            print(couts_marginaux)
        elif choix_transport == 2:
            couts_potentiels = table_couts_potentiels(proposition_balas_hammer, matrice_des_couts)
            couts_marginaux = table_couts_marginaux(matrice_des_couts, couts_potentiels)
            print("\nTableau des coûts potentiels :\n")
            print(couts_potentiels)
            print("\nTableau des coûts marginaux :\n")
            print(couts_marginaux)
