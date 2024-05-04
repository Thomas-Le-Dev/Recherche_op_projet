import random
import time 

# Importer fonctions
from fonctions import proposition_transport_nord_ouest, proposition_transport_balas_hammer

import matplotlib.pyplot as plt

# LA FONCTION TIME.CLOCK() EST DEPRECIEE, UTILISER TIME.PERF_COUNTER() A LA PLACE

valeurs_n_test = [10, 40, 10**2] #4*10**2] #, 10**3, 4*10**3, 10**4]

def generer_matrice_couts(n):
    # Génère une matrice de coûts de taille n x n
    # Les coûts sont des entiers aléatoires entre 1 et 100
    matrice_couts = []
    for i in range(n):
        ligne = []
        for j in range(n):
            ligne.append(random.randint(1, 100))
        matrice_couts.append(ligne)
    return matrice_couts


def generer_provisions_commandes(n):
    """
    Génère les provisions (Pi) et les commandes (Cj) pour un nombre donné n.

    Args:
        n (int): Le nombre de périodes pour lesquelles générer les valeurs.

    Returns:
        tuple: Un tuple contenant deux tableaux:
            * provisions: Un tableau contenant les valeurs des provisions (Pi).
            * commandes: Un tableau contenant les valeurs des commandes (Cj).
    """

    # Générer une matrice aléatoire
    matrice_aleatoire = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]

    # Initialiser les provisions et les commandes
    provisions = [0] * n
    commandes = [0] * n

    # Remplir les tableaux
    for i in range(n):
        for j in range(n):
            provisions[i] += matrice_aleatoire[i][j]
            commandes[j] += matrice_aleatoire[i][j]

    # Renvoyer les résultats
    # Verifier que les sommes des provisions et des commandes sont égales
    print(f"Somme des provisions: {sum(provisions)}")
    print(f"Somme des commandes: {sum(commandes)}")
    return provisions, commandes

def test_nord_ouest(matrices_couts, matrice_provisions, matrice_commandes):
    # Mesurer le temps d'exécution
    debut = time.perf_counter()
    proposition = proposition_transport_nord_ouest(matrices_couts, matrice_provisions.copy(), matrice_commandes.copy())
    fin = time.perf_counter()

    return debut, fin

def test_balas_hammer(matrices_couts, matrice_provisions, matrice_commandes):
    # Mesurer le temps d'exécution
    debut = time.perf_counter()
    proposition = proposition_transport_balas_hammer(matrices_couts, matrice_provisions.copy(), matrice_commandes.copy())
    fin = time.perf_counter()

    return debut, fin

def test_marche_pied_nord_ouest(matrices_couts, matrice_provisions, matrice_commandes):
    # Mesurer le temps d'exécution
    debut = time.perf_counter()


    return debut

def test_marche_pied_balas_hammer(matrices_couts, matrice_provisions, matrice_commandes):
    # Mesurer le temps d'exécution
    debut = time.perf_counter()


    return debut


def plot_nuage_points(temps_nord_ouest, temps_balas_hammer):
    # Afficher nuage de points
    # Une fois les valeurs stockées, vous tracerez en fonction de n, les nuages de points (les 100 valeurs pour une même abscisse) suivants : temps d'exécution de la méthode du nord-ouest et temps d'exécution de la méthode de Balas-Hammer.
    # Utilisation de matplotlib.pyplot.scatter(x, y) pour tracer les nuages de points.

    # Faire un plot pour chaque methode
    # Afficher les temps pour Balas-Hammer

    for i in range(len(valeurs_n_test)):
        n = valeurs_n_test[i]
        plt.scatter([n] * 100, temps_nord_ouest[i], color='blue', label='Nord-Ouest')

    # Ajouter titre
    plt.title("Temps d'exécution de la méthode du nord-ouest en fonction de n")
    # Sauvegarder dans un fichier
    plt.savefig("nuage_points_nord_ouest.png")

    # Clear plot
    plt.clf()

    for i in range(len(valeurs_n_test)):
        n = valeurs_n_test[i]
        plt.scatter([n] * 100, temps_balas_hammer[i], color='red', label='Balas-Hammer')

    # Ajouter titre
    plt.title("Temps d'exécution de la méthode de Balas-Hammer en fonction de n")
    # Sauvegarder dans un fichier
    plt.savefig("nuage_points_balas_hammer.png")

def main():
    # Tester les fonctions pour chaque valeur de n, et ce 100 fois

    # Stocker temps pour chaque test (chaque valeur de n et chaque test)
    temps_nord_ouest = []
    temps_balas_hammer = []

    for n in valeurs_n_test:
        print(f"Test pour n = {n}")

        temps_nord_ouest_n = []
        temps_balas_hammer_n = []

        for i in range(100):
            print(f"Test numéro {i+1}")
            # Générer les matrices de coûts, de provisions et de commandes
            matrices_couts = generer_matrice_couts(n)
            matrice_provisions, matrice_commandes = generer_provisions_commandes(n)

            # Tester la fonction nord-ouest
            debut_nord_ouest, fin_nord_ouest = test_nord_ouest(matrices_couts, matrice_provisions, matrice_commandes)
            temps_nord_ouest_n.append(fin_nord_ouest - debut_nord_ouest)
            print(f"Temps d'exécution: {fin_nord_ouest - debut_nord_ouest} secondes")

            # Tester la fonction balas-hammer
            debut_balas_hammer, fin_balas_hammer = test_balas_hammer(matrices_couts, matrice_provisions, matrice_commandes)
            temps_balas_hammer_n.append(fin_balas_hammer - debut_balas_hammer)
            print(f"Temps d'exécution: {fin_balas_hammer - debut_balas_hammer} secondes")

            '''            # Tester la fonction marche à pied nord-ouest
            debut_marche_pied_nord_ouest = test_marche_pied_nord_ouest(matrices_couts, matrice_provisions, matrice_commandes)
            print(f"Temps d'exécution: {time.perf_counter() - debut_marche_pied_nord_ouest} secondes")

            # Tester la fonction marche à pied balas-hammer
            debut_marche_pied_balas_hammer = test_marche_pied_balas_hammer(matrices_couts, matrice_provisions, matrice_commandes)
            print(f"Temps d'exécution: {time.perf_counter() - debut_marche_pied_balas_hammer} secondes")
            '''

        # Ajouter les temps pour n à la liste
        temps_nord_ouest.append(temps_nord_ouest_n)
        temps_balas_hammer.append(temps_balas_hammer_n)
    
    plot_nuage_points(temps_nord_ouest, temps_balas_hammer)



if __name__ == "__main__":
    main()