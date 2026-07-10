"""
Script principal pour générer des cartes et données hydrologiques/météorologiques.

Ce script propose deux modes d'utilisation :
1. Mode interactif : Lancez le script sans arguments pour être guidé pas à pas
2. Mode CLI (ligne de commande) : Utilisez des arguments pour automatiser les tâches

Fonctionnalités disponibles :
- Génération de cartes d'hydraulicité
- Génération de cartes de VCN3/périodes de retour
- Export de données Météo France (brutes ou SIM2, mensuelles ou quotidiennes)
- Export de données ONDE (campagnes habituelles ou toutes campagnes)
"""

import argparse
from datetime import timedelta, datetime
import calendar

# Import des modules locaux
import src.plotting.plot_grandeur as plot_grandeur
import src.plotting.plot_meteoFrance as plot_meteoFrance
import src.plotting.plot_onde as plot_onde
from src.model.enums import OndeCampagneType, GeographicScaleClip, MeteoFranceDataType
from pynsee.utils import clear_all_cache
from src.config.logging_config import setup_logger

# Configuration du logger (système de journalisation)
logger = setup_logger(name="main")


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

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
    logger.info(f"{message} (format: {format_exemple}, défaut: {valeur_par_defaut.strftime(format_exemple)})")
    reponse = input(" -> ")
    
    if not reponse:
        logger.info(f"Date par défaut utilisée : {valeur_par_defaut}")
        return valeur_par_defaut
    
    try:
        if len(reponse) == 7:  # Format AAAA-MM
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


# ============================================================================
# FONCTIONS POUR LA GENERATION DES CARTES HUBEAU (Hydraulicité et VCN3)
# ============================================================================

def generer_carte_hubeau(type_carte: str):
    """
    Génère une carte à partir des données Hubeau (stations hydrologiques).
    
    Args:
        type_carte: "hydraulicite", "vcn3", ou "les_deux"
    """
    logger.info("="*60)
    logger.info("GENERATION DE CARTE HUBEAU")
    logger.info("="*60)
    
    # 1. Sélection de la date
    aujourdhui = datetime.now()
    debut_mois_precedent = aujourdhui - timedelta(days=aujourdhui.day)
    
    date_selectionnee = demander_date(
        "Choisissez le mois pour lequel générer les données",
        "AAAA-MM",
        debut_mois_precedent
    )
    date_annee_mois = date_selectionnee.strftime("%Y-%m")
    logger.info(f"Mois sélectionné : {date_annee_mois}")
    
    # 2. Sélection du réseau SANDRE
    options_reseau = {
        "1": "BSH001 (par défaut)",
        "2": "custom (utiliser la liste personnalisée)"
    }
    choix_reseau = demander_avec_choix(
        "Choisissez un réseau SANDRE",
        options_reseau,
        "1"
    )
    reseau_sandre = "BSH001" if choix_reseau == "1" else "custom"
    logger.info(f"Réseau Sandre sélectionné : {reseau_sandre}")
    
    # 3. Génération des graphiques individuels (seulement pour VCN3)
    generer_graphiques = False
    if type_carte in ["vcn3", "les_deux"]:
        generer_graphiques = demander_ou_non(
            "Souhaitez-vous générer les graphiques individuels pour chaque station "
            "(pour le calcul des périodes de retour)?"
        )
    
    logger.info("Génération en cours...")
    
    # Générer les fichiers GeoJSON de base (communs à toutes les cartes)
    logger.info("  - Génération des stations ouvertes pour le mois sélectionné...")
    plot_grandeur.create_geojson_from_stations(reseau_sandre, date_annee_mois)
    
    logger.info("  - Génération des sites correspondant au réseau sélectionné...")
    plot_grandeur.create_geojson_from_sites(reseau_sandre)
    
    logger.info("  - Génération de toutes les stations du réseau (même fermées)...")
    plot_grandeur.create_geojson_from_stations(reseau_sandre, None)
    
    logger.info("  - Génération de toutes les stations et sites disponibles...")
    plot_grandeur.create_geojson_from_stations(None, None)
    plot_grandeur.create_geojson_from_sites(None)
    
    # Générer la carte demandée
    if type_carte in ["hydraulicite", "les_deux"]:
        logger.info("  - Génération de la carte d'hydraulicité...")
        plot_grandeur.create_geojson_from_hydraulicite(date_annee_mois, reseau_sandre)
    
    if type_carte in ["vcn3", "les_deux"]:
        logger.info("  - Génération de la carte de périodes de retour (VCN3)...")
        plot_grandeur.create_geojson_from_periode_de_retour(
            date_annee_mois, reseau_sandre, generer_graphiques
        )
    
    logger.info("Génération Hubeau terminée !")


# ============================================================================
# FONCTIONS POUR LA GENERATION DES CARTES METEO FRANCE
# ============================================================================

def generer_carte_meteo():
    """
    Génère une carte à partir des données Météo France.
    """
    logger.info("="*60)
    logger.info("GENERATION DE CARTE METEO FRANCE")
    logger.info("="*60)
    
    # 1. Sélection de l'échelle temporelle
    options_echelle = {
        "1": "MENSUELLE",
        "2": "QUOTIDIENNE (par défaut)"
    }
    choix_echelle = demander_avec_choix(
        "Quel échelle temporelle souhaitez-vous ?",
        options_echelle,
        "2"
    )
    est_mensuel = (choix_echelle == "1")
    est_quotidien = (choix_echelle == "2")
    
    # 2. Sélection du type de données
    options_donnees = {
        "1": "Données brutes (sans pré-calcul)",
        "2": "SIM2 (par défaut - données interpolées sur grille 8x8km)"
    }
    choix_donnees = demander_avec_choix(
        "Quel type de données souhaitez-vous ?",
        options_donnees,
        "2"
    )
    est_classique = (choix_donnees == "1")
    est_sim2 = (choix_donnees == "2")
    
    # 3. Sélection des dates
    format_date = "AAAAMM" if est_mensuel else "AAAAMMJJ"
    
    aujourdhui = datetime.now()
    # Date de début par défaut : premier jour du mois précédent
    debut_defaut = (aujourdhui.replace(day=1) - timedelta(days=1)).replace(day=1)
    date_debut = demander_date(
        f"Quelle date de début souhaitez-vous ?",
        format_date,
        debut_defaut
    )
    
    # Date de fin par défaut : dernier jour du mois précédent
    fin_defaut = debut_defaut.replace(day=calendar.monthrange(debut_defaut.year, debut_defaut.month)[1])
    date_fin = demander_date(
        f"Quelle date de fin souhaitez-vous (inclus) ?",
        format_date,
        fin_defaut
    )
    
    # 4. Aggregation des données
    aggreger_donnees = demander_ou_non(
        "Souhaitez-vous agréger les données dans cet intervalle ? "
        "(Si Non, des graphiques jour par jour seront générés en plus)",
        valeur_par_defaut=True
    )
    
    # 5. Mise à jour des données
    mettre_a_jour_donnees = demander_ou_non(
        "Souhaitez-vous mettre à jour les données téléchargées ?",
        valeur_par_defaut=True
    )
    
    mettre_a_jour_index = False
    if mettre_a_jour_donnees:
        mettre_a_jour_index = demander_ou_non(
            "Souhaitez-vous aussi mettre à jour l'index des données ?",
            valeur_par_defaut=True
        )
    
    # 6. Déterminer le type de données Météo France
    if est_quotidien:
        if est_classique:
            type_donnees = MeteoFranceDataType.QUOT
            logger.info("Génération des données classiques quotidiennes")
        if est_sim2:
            type_donnees = MeteoFranceDataType.SIM2_QUOT
            logger.info("Génération des données SIM2 quotidiennes")
    else:  # mensuel
        if est_classique:
            type_donnees = MeteoFranceDataType.MENS
            logger.info("Génération des données classiques mensuelles")
        if est_sim2:
            type_donnees = MeteoFranceDataType.SIM2_MENS
            logger.info("Génération des données SIM2 mensuelles")
    
    logger.info(f"Période : du {date_debut} au {date_fin}")
    logger.info("Génération en cours...")
    
    # Générer les fichiers GeoJSON
    plot_meteoFrance.export_all_format_geojson_range(
        GeographicScaleClip.DEPARTEMENT_BASSIN,
        type_donnees,
        date_debut,
        date_fin,
        aggreger_donnees,
        mettre_a_jour_index,
        mettre_a_jour_donnees
    )
    
    logger.info("Génération Météo France terminée !")


# ============================================================================
# FONCTIONS PRINCIPALES
# ============================================================================

def mode_interactif():
    """
    Lance le script en mode interactif.
    Guide l'utilisateur pas à pas pour générer les cartes souhaitées.
    """
    logger.info("="*60)
    logger.info("BIENVENUE DANS L'OUTIL DE GENERATION DE CARTES")
    logger.info("="*60)
    logger.info("Ce script permet de générer différentes cartes à partir de données")
    logger.info("hydrologiques (Hubeau) et météorologiques (Météo France).")
    logger.info("Vous pouvez aussi utiliser le mode CLI avec des arguments.")
    logger.info("Voir --help pour plus d'informations.\n")
    
    # Sélection du type de carte à générer
    options_principales = {
        "1": "Générer une carte d'HYDRAULICITE (niveaux d'eau)",
        "2": "Générer une carte de VCN3/Périodes de retour (étiage)",
        "3": "Générer LES DEUX cartes Hubeau (plus long au premier lancement)",
        "4": "Générer des extraits METEO FRANCE (par défaut)"
    }
    
    choix = demander_avec_choix(
        "Que souhaitez-vous générer ?",
        options_principales,
        "4"
    )
    
    if choix in ["1", "2", "3"]:
        type_map = {"1": "hydraulicite", "2": "vcn3", "3": "les_deux"}
        generer_carte_hubeau(type_map[choix])
    else:
        generer_carte_meteo()


def mode_cli(args):
    """
    Exécute le script en mode CLI avec les arguments fournis.
    
    Args:
        args: Les arguments parsés par argparse
    """
    aujourdhui = datetime.now()
    
    # Initialisation des variables
    start_date = None
    end_date = None
    
    # Date de début
    if args.start_date:
        start_date = formater_date_vers_datetime(args.start_date, est_debut=True)
    
    if start_date is None:
        start_date = (aujourdhui.replace(day=1) - timedelta(days=1)).replace(day=1)
        logger.info(f"Date de début par défaut : {start_date}")
    
    # Date de fin
    if args.end_date:
        end_date = formater_date_vers_datetime(args.end_date, est_debut=False)
    
    if end_date is None:
        end_date = start_date.replace(day=calendar.monthrange(start_date.year, start_date.month)[1])
        logger.info(f"Date de fin par défaut : {end_date}")
    
    # Réseau Sandre par défaut
    reseau_sandre = args.reseau_sandre if args.reseau_sandre else "BSH001"
    
    # Appel de la fonction principale
    main(
        type_carte=args.type,
        start_date=start_date,
        end_date=end_date,
        reseau_sandre=reseau_sandre,
        has_vcn3_graphic=args.vcn3_graphic,
        has_meteo_aggregate=args.meteo_aggregate,
        has_meteo_index_update=not args.meteo_no_index_update,
        is_data_update_allowed=not args.meteo_no_update,
        geographic_scale=args.geographic_scale,
        code_zone=args.onde_zone_code if args.onde_zone_code else "01"
    )


def main(
    type_carte: str,
    start_date: datetime,
    end_date: datetime,
    reseau_sandre: str,
    has_vcn3_graphic: bool = False,
    has_meteo_aggregate: bool = False,
    has_meteo_index_update: bool = True,
    is_data_update_allowed: bool = True,
    geographic_scale: GeographicScaleClip = GeographicScaleClip.BASSIN,
    code_zone: str = "01",
):
    """
    Fonction principale qui génère les GeoJSON en fonction des paramètres.
    
    Args:
        type_carte: Type de carte à générer
        start_date: Date de début
        end_date: Date de fin
        reseau_sandre: Réseau SANDRE à utiliser
        has_vcn3_graphic: Si True, génère les graphiques individuels pour VCN3
        has_meteo_aggregate: Si True, aggrège les données météo
        has_meteo_index_update: Si True, met à jour l'index météo
        is_data_update_allowed: Si True, autorise la mise à jour des données
        geographic_scale: Échelle géographique pour les données météo/onde
        code_zone: Code de la zone géographique pour ONDE
    """
    if not is_data_update_allowed:
        has_meteo_index_update = False
    
    # Exécution en fonction du type de carte
    if type_carte == "hydraulicite":
        logger.info("Génération de la carte d'hydraulicité...")
        plot_grandeur.create_geojson_from_hydraulicite(
            start_date.strftime("%Y-%m"),
            reseau_sandre
        )
    
    elif type_carte == "vcn3":
        logger.info("Génération de la carte VCN3/périodes de retour...")
        plot_grandeur.create_geojson_from_periode_de_retour(
            start_date.strftime("%Y-%m"),
            reseau_sandre,
            has_vcn3_graphic
        )
    
    elif type_carte == "meteo_brut_MENS":
        logger.info("Génération des données Météo France brutes mensuelles...")
        plot_meteoFrance.export_all_format_geojson_range(
            geographic_scale,
            MeteoFranceDataType.MENS,
            start_date,
            end_date,
            is_data_aggregated=has_meteo_aggregate,
            has_index_update=has_meteo_index_update,
            is_data_update_allowed=is_data_update_allowed
        )
    
    elif type_carte == "meteo_sim2_MENS":
        logger.info("Génération des données Météo France SIM2 mensuelles...")
        plot_meteoFrance.export_all_format_geojson_range(
            geographic_scale,
            MeteoFranceDataType.SIM2_MENS,
            start_date,
            end_date,
            is_data_aggregated=has_meteo_aggregate,
            has_index_update=has_meteo_index_update,
            is_data_update_allowed=is_data_update_allowed
        )
    
    elif type_carte == "meteo_brut_QUOT":
        logger.info("Génération des données Météo France brutes quotidiennes...")
        plot_meteoFrance.export_all_format_geojson_range(
            geographic_scale,
            MeteoFranceDataType.QUOT,
            start_date,
            end_date,
            is_data_aggregated=has_meteo_aggregate,
            has_index_update=has_meteo_index_update,
            is_data_update_allowed=is_data_update_allowed
        )
    
    elif type_carte == "meteo_sim2_QUOT":
        logger.info("Génération des données Météo France SIM2 quotidiennes...")
        plot_meteoFrance.export_all_format_geojson_range(
            geographic_scale,
            MeteoFranceDataType.SIM2_QUOT,
            start_date,
            end_date,
            is_data_aggregated=has_meteo_aggregate,
            has_index_update=has_meteo_index_update,
            is_data_update_allowed=is_data_update_allowed
        )
    
    elif type_carte == "onde_USUELLE":
        logger.info("Génération des données ONDE (campagnes usuelles)...")
        plot_onde.plot_everything(
            OndeCampagneType.USUELLE,
            start_date,
            geographic_scale,
            code_zone
        )
    
    elif type_carte == "onde_ALL":
        logger.info("Génération des données ONDE (toutes campagnes)...")
        plot_onde.plot_everything(
            OndeCampagneType.ALL_CAMPAGNE,
            start_date,
            geographic_scale,
            code_zone
        )
    
    elif type_carte == "stations-sites":
        logger.info("Génération des stations et sites...")
        # Générer les fichiers de base
        plot_grandeur.create_geojson_from_stations(reseau_sandre, start_date.strftime("%Y-%m"))
        plot_grandeur.create_geojson_from_sites(reseau_sandre)
        plot_grandeur.create_geojson_from_stations(reseau_sandre, None)
        plot_grandeur.create_geojson_from_stations(None, None)
        plot_grandeur.create_geojson_from_sites(None)
    
    else:
        raise NotImplementedError(f"Type de carte non implémenté : {type_carte}")


# ============================================================================
# CONFIGURATION CLI ET POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    # Nettoyer le cache de Pynsee
    clear_all_cache()
    
    # Configuration du parseur d'arguments
    parser = argparse.ArgumentParser(
        description="Exporter des données hydrologiques/météorologiques sous forme de cartes GeoJSON.",
        epilog="Pour plus d'informations : https://github.com/Thomas-MESLIN/RecupeEthiage"
    )
    
    # Argument principal : type de carte
    parser.add_argument(
        "--type",
        choices=[
            "hydraulicite",
            "vcn3",
            "meteo_brut_MENS",
            "meteo_sim2_MENS",
            "meteo_brut_QUOT",
            "meteo_sim2_QUOT",
            "stations-sites",
            "onde_USUELLE",
            "onde_ALL"
        ],
        help="""
        Type de données à générer :
        - hydraulicite : Carte d'hydraulicité (niveaux d'eau) pour un mois
        - vcn3 : Carte de VCN3 et périodes de retour (étiage) pour un mois
        - meteo_brut_MENS : Données Météo France brutes mensuelles
        - meteo_sim2_MENS : Données Météo France SIM2 mensuelles
        - meteo_brut_QUOT : Données Météo France brutes quotidiennes
        - meteo_sim2_QUOT : Données Météo France SIM2 quotidiennes
        - stations-sites : Liste des stations et sites
        - onde_USUELLE : Données ONDE (campagnes usuelles)
        - onde_ALL : Données ONDE (toutes campagnes)
        """
    )
    
    # Arguments de dates
    parser.add_argument(
        "--start_date",
        help="Date de début au format AAAA-MM-JJ ou AAAA-MM (défaut : premier jour du mois précédent)"
    )
    parser.add_argument(
        "--end_date",
        help="Date de fin au format AAAA-MM-JJ ou AAAA-MM (défaut : dernier jour du mois précédent)"
    )
    
    # Arguments spécifiques
    parser.add_argument(
        "--reseau_sandre",
        help="Réseau SANDRE à utiliser (défaut : BSH001). Utilisez 'custom' pour la liste personnalisée"
    )
    parser.add_argument(
        "--vcn3_graphic",
        action='store_true',
        help="[VCN3] Générer des graphiques individuels pour chaque station"
    )
    parser.add_argument(
        "--geographic_scale",
        choices=[
            GeographicScaleClip.NATIONAL,
            GeographicScaleClip.BASSIN,
            GeographicScaleClip.REGION_ADMINISTRATIVE,
            GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF,
            GeographicScaleClip.REGION_BASSIN,
            GeographicScaleClip.DEPARTEMENT_BASSIN
        ],
        help="[météo/onde] Échelle géographique (défaut : BASSIN)",
        default=GeographicScaleClip.BASSIN
    )
    parser.add_argument(
        "--onde_zone_code",
        help="[onde] Code de la zone géographique (ex : '06' pour bassin Rhône-Méditerranée)"
    )
    parser.add_argument(
        "--meteo_aggregate",
        action='store_true',
        help="[météo] Aggréger les données sur la période sélectionnée"
    )
    parser.add_argument(
        "--meteo_no_index_update",
        action='store_false',
        help="[météo] Ne pas mettre à jour l'index de correspondance des datasets"
    )
    parser.add_argument(
        "--meteo_no_update",
        action='store_false',
        help="[météo] Ne pas mettre à jour les données (désactive aussi mise à jour index)"
    )
    
    # Parsing des arguments
    args = parser.parse_args()
    
    # Initialisation des variables
    start_date = None
    end_date = None
    
    # Mode interactif si aucun type n'est spécifié
    if args.type is None:
        logger.info("Aucun type de carte spécifié.")
        logger.info("Lancement du mode interactif...\n")
        mode_interactif()
    else:
        # Mode CLI
        mode_cli(args)
    
    logger.info("="*60)
    logger.info("GENERATION TERMINEE AVEC SUCCES !")
    logger.info("="*60)
