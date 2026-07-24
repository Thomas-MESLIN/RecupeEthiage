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
import src.plotting.plot_onde as plot_onde
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
        "1": "BSH001 - par défaut",
        "2": "custom - utiliser la liste personnalisée"
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
            "- pour le calcul des périodes de retour?"
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
        "2": "QUOTIDIENNE - par défaut"
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
        "1": "Données brutes - sans pré-calcul",
        "2": "SIM2 - par défaut - données interpolées sur grille 8x8km"
    }
    choix_donnees = demander_avec_choix(
        "Quel type de données souhaitez-vous ?",
        options_donnees,
        "2"
    )
    est_classique = (choix_donnees == "1")
    est_sim2 = (choix_donnees == "2")
    
    # 3. Sélection de l'échelle géographique
    options_geo = {
        "1": "NATIONAL",
        "2": "BASSIN - par défaut",
        "3": "REGION_ADMINISTRATIVE",
        "4": "DEPARTEMENT_ADMINISTRATIF",
        "5": "REGION_BASSIN",
        "6": "DEPARTEMENT_BASSIN",
        "7": "ECOREGION_HYDROLOGIQUE"
    }
    choix_geo = demander_avec_choix(
        "Quel échelle géographique souhaitez-vous ?",
        options_geo,
        "2"
    )
    
    # Mapper le choix à l'énumération
    geographic_scale_map = {
        "1": GeographicScaleClip.NATIONAL,
        "2": GeographicScaleClip.BASSIN,
        "3": GeographicScaleClip.REGION_ADMINISTRATIVE,
        "4": GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF,
        "5": GeographicScaleClip.REGION_BASSIN,
        "6": GeographicScaleClip.DEPARTEMENT_BASSIN,
        "7": GeographicScaleClip.ECOREGION_HYDROLOGIQUE
    }
    geographic_scale = geographic_scale_map[choix_geo]
    logger.info(f"Échelle géographique sélectionnée : {geographic_scale}")
    
    # 4. Sélection des dates
    format_date = "AAAA-MM" if est_mensuel else "AAAA-MM-JJ"
    
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
        f"Quelle date de fin souhaitez-vous - inclus ?",
        format_date,
        fin_defaut
    )
    
    # 5. Agrégation des données
    aggreger_donnees = demander_ou_non(
        "Souhaitez-vous agréger les données dans cet intervalle ? "
        "- Si Non, des graphiques jour par jour seront générés en plus",
        valeur_par_defaut=True
    )
    
    # 6. Mise à jour des données
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
    
    # 7. Déterminer le type de données Météo France
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
        geographic_scale,
        type_donnees,
        date_debut,
        date_fin,
        aggreger_donnees,
        mettre_a_jour_index,
        mettre_a_jour_donnees
    )
    
    logger.info("Génération Météo France terminée !")


# ============================================================================
# FONCTIONS POUR LA GENERATION DES CARTES ONDE
# ============================================================================

def generer_carte_onde():
    """
    Génère une carte à partir des données ONDE.
    """
    logger.info("="*60)
    logger.info("GENERATION DE CARTE ONDE")
    logger.info("="*60)
    
    # 1. Sélection du type de campagne
    options_campagne = {
        "1": "Campagnes USUELLES uniquement",
        "2": "Toutes les campagnes - USUELLE + COMPLEMENTAIRE - par défaut",
    }
    choix_campagne = demander_avec_choix(
        "Quel type de campagne ONDE souhaitez-vous ?",
        options_campagne,
        "2"
    )
    
    campagne_type = OndeCampagneType.USUELLE if choix_campagne == "1" else OndeCampagneType.ALL_CAMPAGNE
    logger.info(f"Type de campagne sélectionné : {campagne_type}")
    
    # 2. Sélection de l'échelle géographique
    options_geo = {
        "1": "NATIONAL",
        "2": "BASSIN - par défaut",
        "3": "REGION_ADMINISTRATIVE",
        "4": "DEPARTEMENT_ADMINISTRATIF",
        "5": "REGION_BASSIN",
        "6": "DEPARTEMENT_BASSIN",
        "7": "ECOREGION_HYDROLOGIQUE"
    }
    choix_geo = demander_avec_choix(
        "Quel échelle géographique souhaitez-vous ?",
        options_geo,
        "2"
    )
    
    # Mapper le choix à l'énumération
    geographic_scale_map = {
        "1": GeographicScaleClip.NATIONAL,
        "2": GeographicScaleClip.BASSIN,
        "3": GeographicScaleClip.REGION_ADMINISTRATIVE,
        "4": GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF,
        "5": GeographicScaleClip.REGION_BASSIN,
        "6": GeographicScaleClip.DEPARTEMENT_BASSIN,
        "7": GeographicScaleClip.ECOREGION_HYDROLOGIQUE
    }
    geographic_scale = geographic_scale_map[choix_geo]
    logger.info(f"Échelle géographique sélectionnée : {geographic_scale}")
    
    # 3. Sélection du code de zone géographique
    # Afficher les codes utiles mentionnés dans le README
    logger.info("\nCodes géographiques utiles - Bassin :")
    logger.info("  01 : Artois-Picardie")
    logger.info("  02 : Meuse")
    logger.info("  03 : Moselle")
    logger.info("  04 : Rhin")
    logger.info("  05 : Loire-Bretagne")
    logger.info("  06 : Rhône-Méditerranée - choix par défaut")
    logger.info("  07 : Adour-Garonne")
    logger.info("  08 : Garonne")
    logger.info("  09 : Charente")
    logger.info("  10 : Seine-Normandie")
    logger.info("\nPour les régions et départements, voir les fichiers dans output/meteoFrance/downloaded_data/delimitation_qgis/")
    
    zone_code = input("Entrez le code de la zone géographique - ex: '06' pour bassin Rhône-Méditerranée : ")
    if not zone_code:
        zone_code = "06"  # Valeur par défaut
    logger.info(f"Code de zone sélectionné : {zone_code}")
    
    # 4. Sélection de la date
    aujourdhui = datetime.now()
    debut_mois_precedent = aujourdhui - timedelta(days=aujourdhui.day)
    
    date_selectionnee = demander_date(
        "Choisissez le mois pour lequel générer les données ONDE",
        "AAAA-MM",
        debut_mois_precedent
    )
    
    logger.info(f"Mois sélectionné : {date_selectionnee.strftime('%Y-%m')}")
    logger.info("Génération en cours...")
    
    # Générer les données ONDE
    plot_onde.plot_everything(
        campagne_type,
        date_selectionnee,
        geographic_scale,
        zone_code
    )
    
    logger.info("Génération ONDE terminée !")


# ============================================================================
# FONCTION POUR GENERER LES STATIONS ET SITES
# ============================================================================

def generer_stations_sites():
    """
    Génère les fichiers de stations et sites.
    """
    logger.info("="*60)
    logger.info("GENERATION DES STATIONS ET SITES")
    logger.info("="*60)
    
    # 1. Sélection du réseau SANDRE
    options_reseau = {
        "1": "BSH001 - par défaut",
        "2": "custom - utiliser la liste personnalisée"
    }
    choix_reseau = demander_avec_choix(
        "Choisissez un réseau SANDRE",
        options_reseau,
        "1"
    )
    reseau_sandre = "BSH001" if choix_reseau == "1" else "custom"
    logger.info(f"Réseau Sandre sélectionné : {reseau_sandre}")
    
    # 2. Sélection de la date (optionnelle pour les stations)
    aujourdhui = datetime.now()
    debut_mois_precedent = aujourdhui - timedelta(days=aujourdhui.day)
    
    date_selectionnee = demander_date(
        "Choisissez le mois pour filtrer les stations - optionnel - laissez vide pour toutes les stations",
        "AAAA-MM",
        debut_mois_precedent
    )
    date_annee_mois = date_selectionnee.strftime("%Y-%m")
    
    logger.info("Génération en cours...")
    
    # Générer les fichiers
    logger.info("  - Génération des stations ouvertes pour le mois sélectionné...")
    plot_grandeur.create_geojson_from_stations(reseau_sandre, date_annee_mois)
    
    logger.info("  - Génération des sites correspondant au réseau sélectionné...")
    plot_grandeur.create_geojson_from_sites(reseau_sandre)
    
    logger.info("  - Génération de toutes les stations du réseau (même fermées)...")
    plot_grandeur.create_geojson_from_stations(reseau_sandre, None)
    
    logger.info("  - Génération de toutes les stations et sites disponibles...")
    plot_grandeur.create_geojson_from_stations(None, None)
    plot_grandeur.create_geojson_from_sites(None)
    
    logger.info("Génération des stations et sites terminée !")


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
    logger.info("hydrologiques (Hubeau), météorologiques (Météo France) et ONDE.")
    logger.info("Vous pouvez aussi utiliser le mode CLI avec des arguments.")
    logger.info("Voir --help pour plus d'informations.\n")
    
    # Sélection du type de carte à générer
    options_principales = {
        "1": "Générer une carte d'HYDRAULICITE - niveaux d'eau",
        "2": "Générer une carte de VCN3/Périodes de retour - étiage",
        "3": "Générer LES DEUX cartes Hubeau - plus long au premier lancement",
        "4": "Générer des extraits METEO FRANCE - option par défaut",
    "5": "Générer des extraits ONDE - écoulements des cours d'eau",
        "6": "Générer les stations et sites - liste de référence"
    }
    
    choix = demander_avec_choix(
        "Que souhaitez-vous générer ?",
        options_principales,
        "4"
    )
    
    if choix == "1":
        generer_carte_hubeau("hydraulicite")
    elif choix == "2":
        generer_carte_hubeau("vcn3")
    elif choix == "3":
        generer_carte_hubeau("les_deux")
    elif choix == "4":
        generer_carte_meteo()
    elif choix == "5":
        generer_carte_onde()
    elif choix == "6":
        generer_stations_sites()
