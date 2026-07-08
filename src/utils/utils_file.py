from pathlib import Path
from datetime import datetime, timedelta

# Vérification de l'ancienneté des données.
def is_path_valid_age(chemin:Path) -> bool:
    """
    Renvoie vrai si le fichier est assez récent (< 1 ans)
    :param chemin: Un chemin sous forme de Path pointant vers un fichier.
    :return: Vrai si le fichier est récent (< 1 ans), faux sinon.
    """
    if not chemin.exists():
        raise FileNotFoundError(chemin)
    one_year = timedelta(days=360) # 1 ans
    #one_year = timedelta(seconds=1)  # 101 seconde pour le test
    time_modification_fichier = chemin.stat().st_mtime
    date_modification_fichier = datetime.fromtimestamp(time_modification_fichier)
    date_actuelle = datetime.now()
    delta = date_actuelle - date_modification_fichier
    return delta < one_year

_cache_prompt = {}
def prompt_renew_old_data(chemin:Path) -> bool:
    """
    Demande à l'utilisateur s'il souhaite renouveler le fichier pointé vers Path.
    :param chemin: Un chemin sous forme de Path pointant vers un fichier à renouveller.
    :return: Vrai si l'utilisateur accepte de renouveller le fichier, faux sinon.
    """
    # Si on a répondu à renouveller tous précédemment, on renvoie True sans rien re-demander à l'utilisateur.
    if "renouveler_tout" in _cache_prompt:
        return True
    elif "renouveler_rien" in _cache_prompt:
        return False

    res_prompt = input(f"\nLe fichier : {chemin.name} est vieux de plus d'un an, souhaitez vous : \n"
                       f"Ne rien renouveler ? (0)\n"
                       f"renouveler uniquement ce fichier ? (1)\n"
                       f"renouveler tous les fichiers trop vieux ? (2)\n"
                       f"Entrez votre réponse (0,1 ou 2) -> ")

    if res_prompt == "1": # On renouvelle uniquement un fichier
        return True
    elif res_prompt == "2": # On renouvelle tous les fichiers trop vieux.
        _cache_prompt["renouveler_tout"] = True
        return True
    else: # On ne renouvelle aucun fichier
        _cache_prompt["renouveler_rien"] = False
        print("\nAucun fichier ne sera renouvelé.\n")
        return False

def is_file_need_download(chemin:Path):
    """
    Vérifie qu'un fichier doit être téléchargé.
    Demande à l'utilisateur de renouveler le fichier si celui-ci est trop vieux.
    :param chemin: Le fichier a potentiellement renouveler.
    :return: True si le fichier doit être téléchargé, False sinon.
    """
    if not chemin.exists():
        return True
    elif is_path_valid_age(chemin):
        return False # On a pas besoin de télécharger le fichier car il est assez récent
    elif prompt_renew_old_data(chemin):
        print(f"\nLe fichier {chemin.name} va être re-téléchargé. \n"
              "si le temps d'attente est trop long, vous pouvez annuler la commande avec ctrl+c.\n"
              "Il suffira de relancer le script et de refuser le prompt qui va s'afficher, \n"
              "l'ancien fichier sera alors utilisé.\n")
        return True
    else:
        return False

def is_res_updated_with_source(chemin_source_list:list[Path], chemin_resultat:Path) -> bool:
    """
    Compare la date de modification du fichier de résultat et du fichier source
    vérifie que le fichier de résultat est plus récent que celui d'entrée.
    Si c'est le fichier source qui est plus récent, alors le fichier résultat doit être mis à jour.
    Si la source n'existe pas, on renvoie False.
    :param chemin_source_list: Une liste de fichier qui sert à construire le résultat
    :param chemin_resultat: Le fichier résultat basé sur le fichier source.
    :return: Renvoie True si le fichier résultat est plus récent que le fichier source. False sinon.
    """
    if not chemin_resultat.exists():
        return False
    is_resultat_plus_recent_que_source = True
    for chemin_source in chemin_source_list:
        if not chemin_source.exists():
            return False
        date_modification_source = chemin_source.stat().st_mtime
        date_modification_resultat = chemin_resultat.stat().st_mtime
        if not date_modification_source < date_modification_resultat:
            is_resultat_plus_recent_que_source = False
            break
    return is_resultat_plus_recent_que_source
