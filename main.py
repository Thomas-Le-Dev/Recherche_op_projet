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
        print(f'Il y a {len(tabs)+1} tableaux de contraintes disponibles\n')
        matrice_des_couts, provisions, commandes = lire_donnees(f"problemes/probleme{numero_probleme}.txt")
        print(f"Problème {numero_probleme} sélectionné.\n")
        afficher_donnees(matrice_des_couts, provisions, commandes)

        proposition_nord_ouest = proposition_transport_nord_ouest(matrice_des_couts, provisions.copy(), commandes.copy())
        proposition_balas_hammer = proposition_transport_balas_hammer(matrice_des_couts, provisions.copy(), commandes.copy())
        print("\nTableau de la proposition transport nord ouest :\n")
        afficher_proposition_transport_tab_cout(proposition_nord_ouest, commandes)
        print("\nTableau de la proposition transport balas hammer :\n")
        afficher_proposition_transport_tab_cout(proposition_balas_hammer, commandes)

        choix_transport = int(input("Choisissez la : \n1 pour nord-ouest\n2 Pour balas-hammer\n"))
        if choix_transport == 1:
            graphe = construire_graphe_biparti(proposition_nord_ouest)
            if not verifier_graphe_biparti_arete(graphe):
                print("Le graphe n'est pas connexe")
                # Ajouter des aretes pour rendre le graphe connexe
                rajouter_aretes(proposition_nord_ouest, matrice_des_couts, graphe)
            couts_potentiels = table_couts_potentiels(proposition_nord_ouest, matrice_des_couts)
            couts_marginaux = table_couts_marginaux(matrice_des_couts, couts_potentiels)
            min_tab_marginaux = trouver_valeur_negative(couts_marginaux)
            print("\nTableau des coûts potentiels :\n")
            afficher_proposition_transport_tab_cout(couts_potentiels, commandes)
            print("\nTableau des coûts marginaux :\n")
            afficher_proposition_transport_tab_cout(couts_marginaux, commandes)
            print(min_tab_marginaux)

        elif choix_transport == 2:
            graphe = construire_graphe_biparti(proposition_balas_hammer)
            if not verifier_graphe_biparti_arete(graphe):
                print("Le graphe n'est pas connexe")
                # Ajouter des aretes pour rendre le graphe connexe
                rajouter_aretes(proposition_balas_hammer, matrice_des_couts, graphe)
            else:
                print("Le graphe est connexe")
            
            if not graphe_biparti_contient_cycle(graphe):
                print("Le graphe est acyclique")

            else:
                print("Le graphe contient un cycle")

            couts_potentiels = calculer_couts_potentiels_graphe(proposition_balas_hammer, matrice_des_couts, graphe)
            #couts_potentiels = table_couts_potentiels(proposition_balas_hammer, matrice_des_couts)
            couts_marginaux = table_couts_marginaux(matrice_des_couts, couts_potentiels)
            min_tab_marginaux = trouver_valeur_negative(couts_marginaux)

            print("\nTableau des coûts potentiels :\n")
            afficher_proposition_transport_tab_cout(couts_potentiels, commandes)
            print("\nTableau des coûts marginaux :\n")
            afficher_proposition_transport_tab_cout(couts_marginaux, commandes)

            while min_tab_marginaux[1] < 0:
                arete = min_tab_marginaux[0]
                ajouter_arete_specifique(proposition_balas_hammer, graphe, arete)
                if not graphe_biparti_contient_cycle(graphe):
                    print("Le graphe est acyclique")

                else:
                    print("Le graphe contient un cycle")
                    # def trouver_valeur_maximale(graphe, cycle, proposition_transport, matrice_couts, provisions, commandes):
                    print(graphe_biparti_contient_cycle(graphe))
                    proposition_balas_hammer = maximisation(proposition_balas_hammer, graphe, arete, graphe_biparti_contient_cycle(graphe))
                    print("\nTableau de la proposition transport balas hammer :\n")
                    afficher_proposition_transport_tab_cout(proposition_balas_hammer, commandes)

                    couts_potentiels = calculer_couts_potentiels_graphe(proposition_balas_hammer, matrice_des_couts, graphe)
                    couts_marginaux = table_couts_marginaux(matrice_des_couts, couts_potentiels)
                    min_tab_marginaux = trouver_valeur_negative(couts_marginaux)

                    
                    print("\nTableau des coûts potentiels :\n")
                    afficher_proposition_transport_tab_cout(couts_potentiels, commandes)
                    print("\nTableau des coûts marginaux :\n")
                    afficher_proposition_transport_tab_cout(couts_marginaux, commandes)
                    
            
            print('La solution optimale est : ')
            afficher_proposition_transport_tab_cout(proposition_balas_hammer, commandes)