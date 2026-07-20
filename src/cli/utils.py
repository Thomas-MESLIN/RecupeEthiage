"""
Fonctions utilitaires pour l'interface utilisateur (CLI et interactif).
"""

from datetime import timedelta, datetime
import calendar

# Import du logger
from src.config.logging_config import setup_logger

# Configuration du logger
logger = setup_logger(name="cli_utils")


def demander_ou_non(question: str, valeur_par_defaut=True) -> bool:
    """
    Pose une question oui/non à l'utilisateur et retourne la réponse.
    
    Args:
        question: La question à poser
        valeur_par_defaut: True si la réponse par défaut est Oui, False si Non
    
    Returns:
        True si l'utilisateur répond Oui, False si Non
    """
    reponse_oui = ["o", "oui", "y", "yes"]
    reponse_non = ["n", "non"]
    
    logger.info(f"{question} (O/n) " if valeur_par_defaut else f"{question} (n/O)")
    reponse_utilisateur = input(" -> ").lower()
    
    if reponse_utilisateur in reponse_oui:
        logger.info("Réponse : Oui")
        return True
    elif reponse_utilisateur in reponse_non:
        logger.info("Réponse : Non")
        return False
    else:
        # Si l'utilisateur appuie juste sur Entrée, on prend la valeur par défaut
        logger.info(f"Réponse par défaut : {'Oui' if valeur_par_defaut else 'Non'}")
        return valeur_par_defaut


def demander_avec_choix(question: str, options: dict, valeur_par_defaut=None) -> str:
    """
    Pose une question avec des options numérotées à l'utilisateur.
    
    Args:
        question: La question à poser
        options: Dictionnaire {"1": "Option 1", "2": "Option 2", ...}
        valeur_par_defaut: La clé de l'option par défaut
    
    Returns:
        La clé de l'option choisie
    """
    logger.info(question)
    for numero, description in options.items():
        logger.info(f"({numero}) {description}")
    
    reponse = input(" -> ")
    
    if reponse in options:
        return reponse
    elif valeur_par_defaut:
        logger.info(f"Option par défaut sélectionnée : {valeur_par_defaut}")
        return valeur_par_defaut
    else:
        # Si aucune valeur par défaut, on prend la première option
        return list(options.keys())[0]


def demander_date(message: str, format_exemple: str, valeur_par_defaut: datetime) -> datetime:
    """
    Demande une date à l'utilisateur avec validation.
    
    Args:
        message: Le message à afficher
        format_exemple: Exemple de format (ex: "AAAA-MM")
        valeur_par_defaut: La date à utiliser si l'utilisateur ne saisit rien
    
    Returns:
        L'objet datetime correspondant
    """
    logger.info(f"{message} (format: {format_exemple}, dfaut: {valeur_par_defaut.strftime("%Y%m%d" if len(format_exemple) == 8 else "%Y%m")})")
    reponse = input(" -> ")
    
    if not reponse:
        logger.info(f"Date par défaut utilisée : {valeur_par_defaut}")
        return valeur_par_defaut
    
    try:
        # Essayer d'abord les formats sans tirets
        if len(reponse) == 6:  # Format AAAAMM
            return datetime.strptime(reponse, "%Y%m")
        elif len(reponse) == 8:  # Format AAAAMMJJ
            return datetime.strptime(reponse, "%Y%m%d")
        # Puis les formats avec tirets (pour la rétrocompatibilité)
        elif len(reponse) == 7:  # Format AAAA-MM
            return datetime.strptime(reponse, "%Y-%m")
        elif len(reponse) == 10:  # Format AAAA-MM-JJ
            return datetime.strptime(reponse, "%Y-%m-%d")
        else:
            logger.warning(f"Format non reconnu, utilisation de la date par défaut")
            return valeur_par_defaut
    except ValueError:
        logger.warning(f"Date invalide, utilisation de la date par défaut")
        return valeur_par_defaut


def formater_date_vers_datetime(date_str: str, est_debut=True) -> datetime | None:
    """
    Convertit une chaîne de caractères en objet datetime.
    
    Args:
        date_str: La date sous forme de chaîne (AAAA-MM ou AAAA-MM-JJ)
        est_debut: Si True, retourne le 1er jour du mois pour AAAA-MM
    
    Returns:
        Objet datetime ou None si le format est invalide
    """
    if len(date_str) == 7:  # Format AAAA-MM
        date = datetime.strptime(date_str, "%Y-%m")
        if est_debut:
            return date.replace(day=1)
        else:
            # Dernier jour du mois
            dernier_jour = calendar.monthrange(date.year, date.month)[1]
            return date.replace(day=dernier_jour)
    elif len(date_str) == 10:  # Format AAAA-MM-JJ
        return datetime.strptime(date_str, "%Y-%m-%d")
    return None
