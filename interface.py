import pygame
import sys
import time
import json
import os
import threading
from filelock import FileLock, Timeout

#===============================#
''' Importation des variables '''
#===============================#

with open('Variables.json', 'r') as f:
    variables = json.load(f)

background = variables["background"]
titre = variables["titre"]
pig = variables["pig"]
pig_h = variables["pig_head"]

chemin_animal_couleur = variables["chemin_animal_couleur"]
chemin_animal_noir = variables["chemin_animal_noir"]
chemin_animal_audio = variables["chemin_animal_audio"]
chemin_communication = variables["chemin_communication"]

dic_animal_classe = {
    1: "cheval_gravity", 2: "chevre_gravity", 3: "chat_gravity",
    4: "chien_gravity", 5: "coq_gravity", 6: "vache_gravity"
}
dic_animal = {
    1: "cheval", 2: "chevre", 3: "chat",
    4: "chien", 5: "coq", 6: "vache"
}

dic_animal_images_noir = {}
dic_animal_images_couleurs = {}

def lire_fichier_audio(animal):
    chemin_fichier_audio = chemin_animal_audio + animal + ".mp3"
    pygame.mixer.init()
    pygame.mixer.music.load(chemin_fichier_audio)
    pygame.mixer.music.play()

def anime_animal(classe):
    '''Prend la classe déterminée par KNN en entrée et anime sur l'interface l'animal correspondant avec le son'''
    return dic_animal[classe], dic_animal_classe[classe]

def lire_json(chemin_fichier):
    with FileLock(chemin_fichier + ".lock"):
        with open(chemin_fichier, 'r') as fichier:
            return json.load(fichier)

def ecrire_json(chemin_fichier, donnees):
    with FileLock(chemin_fichier + ".lock"):
        with open(chemin_fichier, 'w') as fichier:
            json.dump(donnees, fichier)

#============================#
''' Initialisation du jeu '''
#============================#

pygame.init()
screen = pygame.display.set_mode((928, 360))
pygame.display.set_caption('Projet Clavier - Les animaux de la ferme')
clock = pygame.time.Clock()

# Chargement du fond d'écran
farm_bg = pygame.image.load(background).convert()
title_im = pygame.image.load(titre).convert_alpha()
pig_im = pygame.image.load(pig).convert_alpha()
pig_head = pygame.image.load(pig_h).convert_alpha()
pygame.display.set_icon(pig_head)

# Chargement des images puis initialisation de leurs emplacements et de leurs valeurs
for i in range(len(dic_animal)):
    dic_animal_images_noir[i + 1] = pygame.image.load(chemin_animal_noir + dic_animal[i + 1] + "_noir.png").convert_alpha()
    dic_animal_images_couleurs[i + 1] = pygame.image.load(chemin_animal_couleur + dic_animal[i + 1] + ".png").convert_alpha()

cheval = dic_animal_images_noir[1]
cheval_rect = cheval.get_rect(midbottom=(800, 330))
cheval_gravity = 0

chevre = dic_animal_images_noir[2]
chevre_rect = chevre.get_rect(midbottom=(400, 280))
chevre_gravity = 0

chat = dic_animal_images_noir[3]
chat_rect = chat.get_rect(midbottom=(250, 350))
chat_gravity = 0

chien = dic_animal_images_noir[4]
chien_rect = chien.get_rect(midbottom=(100, 315))
chien_gravity = 0

coq = dic_animal_images_noir[5]
coq_rect = coq.get_rect(midbottom=(520, 345))
coq_gravity = 0

vache = dic_animal_images_noir[6]
vache_rect = vache.get_rect(midbottom=(610, 280))
vache_gravity = 0

#==============================================#
''' Definition d'un événement case touchée '''
#==============================================#

NOUVELLE_CASE_EVENEMENT = pygame.USEREVENT + 1

def generer_nouvelle_case_evenement(numero_case):
    pygame.event.post(pygame.event.Event(NOUVELLE_CASE_EVENEMENT, {'numero_case': numero_case}))

def surveiller_case_touchee():
    # Boucle pour surveiller le fichier en continu
    while True:
        if os.path.exists(chemin_communication):
            # Lire l'information sur la case touchée depuis le fichier JSON
            case = lire_json(chemin_communication)
            case_touchee = case.get("case_touchee")
            
            if case_touchee is not None:
                generer_nouvelle_case_evenement(case_touchee)  # Déclenche l'événement
                ecrire_json(chemin_communication, {"case_touchee": 'null'})

        # Attendre avant de vérifier à nouveau
        time.sleep(0.05)

# Créer et démarrer un thread pour surveiller les cases touchées
thread_surveillance = threading.Thread(target=surveiller_case_touchee)
thread_surveillance.daemon = True  # Permet d'arrêter le thread lorsque le programme principal se termine
thread_surveillance.start()

#===============================#
''' Démarrage de l'interface '''
#===============================#

while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == NOUVELLE_CASE_EVENEMENT:
            numero_case = event.dict['numero_case']
            if numero_case != 'null':
                animal = anime_animal(numero_case)[0]  # Prend l'animal
                animal_gravity = anime_animal(numero_case)[1]  # Prend l'animal à faire sauter
                locals()[animal_gravity] = -8  # Fait sauter l'animal

                lire_fichier_audio(animal)  # Joue l'audio de l'animal
                locals()[animal] = dic_animal_images_couleurs[numero_case]  # Convertit les animaux en couleurs

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Reset des couleurs des animaux
                cheval = dic_animal_images_noir[1]
                chevre = dic_animal_images_noir[2]
                chat = dic_animal_images_noir[3]
                chien = dic_animal_images_noir[4]
                coq = dic_animal_images_noir[5]
                vache = dic_animal_images_noir[6]

    screen.blit(farm_bg, (0, 0))  # Image de fond
    screen.blit(pig_im, (145, 3))
    screen.blit(title_im, (20, 5))

    #=======================================#
    ''' Gestion de la gravité des animaux '''
    #=======================================#

    # CHEVAL
    cheval_gravity += 1
    cheval_rect.y += cheval_gravity
    if cheval_rect.bottom >= 330:
        cheval_rect.bottom = 330
    screen.blit(cheval, cheval_rect)

    # CHEVRE
    chevre_gravity += 1
    chevre_rect.y += chevre_gravity
    if chevre_rect.bottom >= 280:
        chevre_rect.bottom = 280
    screen.blit(chevre, chevre_rect)

    # CHAT
    chat_gravity += 1
    chat_rect.y += chat_gravity
    if chat_rect.bottom >= 350:
        chat_rect.bottom = 350
    screen.blit(chat, chat_rect)

    # CHIEN
    chien_gravity += 1
    chien_rect.y += chien_gravity
    if chien_rect.bottom >= 315:
        chien_rect.bottom = 315
    screen.blit(chien, chien_rect)

    # COQ
    coq_gravity += 1
    coq_rect.y += coq_gravity
    if coq_rect.bottom >= 345:
        coq_rect.bottom = 345
    screen.blit(coq, coq_rect)

    # VACHE
    vache_gravity += 1
    vache_rect.y += vache_gravity
    if vache_rect.bottom >= 280:
        vache_rect.bottom = 280
    screen.blit(vache, vache_rect)

    pygame.display.update()
    clock.tick(60)

if __name__ == "__main__":
    pass
