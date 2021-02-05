from matplotlib import pyplot as plt
import numpy as np
import time, timeit
import os, glob

def clear_folder(path):
    """
    Supression de tous les fichiers d'un répertoire.

    path : str
        Chemin absolue du répertoire.
    """
    files = glob.glob(path + '*')
    for f in files:
        os.remove(f)


def countdown(t):
    """
    Compte à rebours.

    t : int
        Temps en seconde
    """
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1
    print('Fire in the hole!!')



def mkdir(path):
    """
    Creation de repertoire.

    path : str
        Chemin du répertoire.
    """
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    else:
        False

def list_data_files(path):
    """
    Liste les fichiers d'un répertoire.

    path_to_files : str
        Chemin du répertoire.
    """
    (_, _, filenames) = next(os.walk(path))
    list_files = [ path + u for u in filenames ]
    list_files.sort()
    return list_files

def choose_a_folder(path):
    """
    Choisir un dossier.
    """
    # get the list of files in path and store in a list
    folder = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    
    # print out all the files with it's corresponding index
    for i in range(len(folder)):
        print( i, folder[i] )
    
    # prompt the user to select the file
    option = input('Choisir un dossier : ')
    
    # build out the full path of the file and open it
    return os.path.join(path, folder[int(option)])
