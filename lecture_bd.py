# Importation des librairies
from pathlib import Path
import os
import time
import scipy.io
import numpy as np
import json

# Importation des variables
with open('Variables.json', 'r') as f:
    variables = json.load(f)

# Fonction qui revoie les signaux d'un dossier
def read(classe):
    # Définition des variables locales
    X = []
    pathname = variables["pathname_db"] + classe + "\\"
    basename = variables["basename"]

    while True:
        # Listage des fichiers présents dans le dossier
        listing = os.listdir(pathname)
        paths = []
        for filename in listing:
            if filename.startswith(basename) and filename.endswith(".mat"):
                paths.append([int(os.stat(pathname + filename).st_mtime), pathname + filename])

        if len(paths) != 0:
            # Lecture et enregistrement des fichiers
            paths = np.sort(paths, axis=0)
            for k in range(paths.shape[0]):
                time.sleep(0.01)
                reader = scipy.io.loadmat(paths[k, 1])
                Fs = reader['tpd']['SampleFrequency'][0, 0].item()
                unit = reader['tpd']['Unit'][0, 0].item()
                tpd = reader['tpd']['Data'][0, 0].ravel()
                X.append(tpd)
                os.remove(paths[k, 1])
        else:
            os.rmdir(pathname)  # Suppression du dossier de la classe
            break

    return X
