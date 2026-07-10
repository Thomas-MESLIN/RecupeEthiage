"""
Mode interactif pour générer des cartes et données hydrologiques/météorologiques.

Ce module contient les fonctions pour le mode interactif qui guide l'utilisateur
pas à pas pour générer les cartes souhaitées.
"""

from datetime import timedelta, datetime
import calendar

# Import des modules locaux
import src.plotting.plot_grandeur as plot_grandeur
import src.plotting.plot_meteoFrance as plot_meteoFrance
from src.model.enums import OndeCampagneType, GeographicScaleClip, MeteoFranceDataType
from src.config.logging_config import setup_logger
from src.cli.utils import demander_ou_non, demander_avec_choix, demander_date, formater_date_vers_datetime

# Configuration du logger
logger = setup_logger(name="main_interactive")


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
        valeur_par_defaut=False
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
