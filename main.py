# Importation des librairies
from pathlib import Path
import os
import time
import scipy.io
import json
import math
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import sys
import subprocess
import threading
import pygame
from filelock import FileLock, Timeout

import lecture_bd
import py_register



def importer_donnees():
    
    '''Importation et definitions des variables'''
    
    with open('Variables.json', 'r') as f:
        variables = json.load(f)

    pathname = variables["pathname"]
    basename = variables["basename"]
    nb_case = variables["nb_case"]
    knn = variables["knn"]
    chemin_interface = variables["chemin_interface"]
    chemin_communication = variables["chemin_communication"]

    C = []
    # Vérification du dossier
    listing = os.listdir( variables["pathname_db"])
    if listing:
        # Charger la base de données
        for i in range(nb_case):
            C.append(lecture_bd.read("C" + str(i + 1)))
            for k in range(len(C[i])):
                C[i][k] = C[i][k] / np.max(C[i][k])
        print("Les données ont été chargées.")
    else:   
        raise ValueError("Le dossier des données est vide.")


    return pathname, basename, C, nb_case, knn, chemin_interface, chemin_communication


def afficher_resultats(max_index, nb_cases):
    
    ''' Affichage des cases (plot) non utilisé '''
    # Calculer le nombre de lignes et de colonnes nécessaires en fonction du nombre total de cases
    nb_colonnes = math.ceil(math.sqrt(nb_cases))
    nb_lignes = math.ceil(nb_cases / nb_colonnes)
    

    fig, axs = plt.subplots(nb_lignes, nb_colonnes)
    fig.suptitle('Signal acquis')

    for i, ax in enumerate(axs.flat):
        if i < nb_cases:
            if i == max_index:
                ax.imshow([[i + 1]], cmap='hot', interpolation='nearest')
                text_color = 'white'
            else:
                ax.imshow([[i + 1]], cmap='cool', interpolation='nearest')
                text_color = 'black'
            ax.text(0.5, 0.5, str(i + 1), fontsize=20, color=text_color,
                    ha='center', va='center', transform=ax.transAxes)
        ax.axis('off')

    plt.show()
    return


def traitement_moyenne(X,C,nb_case):
    '''Methode Moyenne de traitement du signal'''
    
    # Normalisation
    X[-1] = X[-1] / np.max(abs(X[-1]))
    # Intercorrelation puis moyennage entre le signal et la base de données
    moy = []
    for j in range(nb_case):
        temp = []
        for k in range(len(C[j])):
            c_cor = py_register.xcorr(X[-1], C[j][k], scale='none')
            temp.append(np.max(c_cor[0]))
        moy.append(np.mean(temp))
    # Determination de differentes caractéristiques
    max_value = max(moy)
    std_value = np.std(moy)
    return moy.index(max_value)


def traitement_mediane(X,C,nb_case):
    ''' Methode Mediane de traitement du signal '''
    
    # Normalisation
    X[-1] = X[-1] / np.max(abs(X[-1]))
    # Intercorrelation puis moyennage entre le signal et la base de données
    med = []
    for j in range(nb_case):
        temp = []
        for k in range(len(C[j])):
            c_cor = py_register.xcorr(X[-1], C[j][k], scale='none')
            temp.append(np.max(c_cor[0]))
        med.append(np.median(temp))
    # Determination de differentes caractéristiques
    max_value = max(med)
    std_value = np.std(med)
    return med.index(max_value)
    

def traitement_knn(X, C, nb_case, knn):
    ''' Methode KNN de traitement du signal '''
    
    # Normalisation
    X[-1] = X[-1] / np.max(abs(X[-1]))
    
    # Intercorrelation puis moyennage entre le signal et la base de données
    vect = []
    cases_maxi = []
    i = 0
    elements_max = []
    
    # Calcul de l'intercorrélation
    for j in range(nb_case):
        for k in range(len(C[j])):
            c_cor = py_register.xcorr(X[-1], C[j][k], scale='none')
            vect.append([np.max(c_cor[0]), j])
    vect = np.array(vect)
    
    #Determination de la case
    while len(elements_max) != 1 or i < knn: # "or" pour que les conditions valent TRUE tant que les 2 ne sont pas respectées (opérateur logique)
        elements_max=[]
        
        #Determination des maximums
        index_max_value = np.argmax(vect[:, 0])
        case_associe = vect[index_max_value, 1]
        cases_maxi.append(case_associe)
        
        vect = np.delete(vect, index_max_value, axis=0)
        #Compteur de la case qui apparait le plus
        compteur = Counter(cases_maxi)
        max_occurrences = max(compteur.values())
        elements_max = [elem for elem, count in compteur.items() if count == max_occurrences]

        i += 1
    return elements_max[0]


def obtenir_liste_fichiers(pathname, basename):
    '''Liste des chemins des differents signaux'''
    
    paths = []
    listing = os.listdir(pathname)
    for filename in listing:
        if filename.startswith(basename) and filename.endswith(".mat"):
            paths.append([int(os.stat(pathname + filename).st_mtime), pathname + filename])
    return paths


def lecture_fichiers(X,paths,k):
    '''Lis les signaux à comparer'''
    
    time.sleep(0.1)  # le temps que le logiciel finisse d'écrire le fichier
    reader = scipy.io.loadmat(paths[k, 1]) #lecture du .mat
    tpd = reader['tpd']['Data'][0, 0].ravel()
    X.append(tpd)
    os.remove(paths[k, 1])
    return

def ecrire_json(chemin_fichier, donnees):
    '''Ecrit la case dans le fichier pour pygame'''
    
    with FileLock(chemin_fichier + ".lock"):
        with open(chemin_fichier, 'w') as fichier:
            json.dump(donnees, fichier)
    return



def main():
    try:
        while True:
            X = []
            paths = obtenir_liste_fichiers(pathname,basename)

            if len(paths) != 0: #Si le dossier des signaux n'est pas vide
                paths = np.sort(paths, axis=0)  #Trie chronologique
                for k in range(paths.shape[0]): #Pour chaque fichier dans le dossier

                    start = time.time()

                    lecture_fichiers(X,paths,k)
                    
#                    case = traitement_moyenne(X,C,nb_case,knn)
#                    case = traitement_mediane(X,C,nb_case,knn)
                    case = traitement_knn(X,C,nb_case,knn)
                    
#                    afficher_resultats(case, nb_case) #grâce aux plots

                    X=[] # On vide X pour économiser la mémoire

                    # Calcul du temps d'exécution du traitement du signal
                    
                    
                    ecrire_json(chemin_communication, {"case_touchee": case+1})
                    end = time.time()
                    elapsed = end - start
                    print(f"le signal est de la classe : {case + 1} en {elapsed:.2}s")
                    time.sleep(0.1)
                    

    except KeyboardInterrupt:
        print("Reader stopped")

if __name__ == "__main__":
    
    #importation des variables
    pathname, basename, C, nb_case, knn, chemin_interface, chemin_communication = importer_donnees()
    
    # Lance pygame
    processus_interface = subprocess.Popen([sys.executable, chemin_interface])

    #lance la determination des cases
    main()
