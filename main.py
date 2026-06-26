from datetime import timedelta, datetime
import calendar
import plot_grandeur
import station
import logging
import plot_meteoFrance
from plot_meteoFrance import MeteoFranceDataType

def prompt_for_graphic() -> bool:
    print("Souhaitez vous générer les graphiques associées au stations individuel pour le calcul des périodes de retour ? (N/o)")
    input_graphic = input(" -> ")
    res_graphic = input_graphic.lower() in ["o","oui","y","yes"]
    if res_graphic:
        logging.info("Les graphiques individuels seront générés.")
    else:
        logging.info("Les graphiques individuels ne seront pas générés.")
    return res_graphic

def generer_hubeau_graph(res_generation_carte:str):
    # Selection de la date de la carte à générer.
    date_today = datetime.datetime.now()
    date_mois_precedent = date_today - timedelta(date_today.day)
    date_annee_mois = date_mois_precedent.strftime("%Y-%m")
    print("Choisissez la date que vous voulez générer : ")
    print(f"Format AAAA-MM, (mois précédent : {date_annee_mois} par défaut)")
    input_user_mois = input(" -> ")
    if input_user_mois != "" and len(input_user_mois) == 7:
        try:
            date = datetime.datetime.strptime(input_user_mois, "%Y-%m")
            date_annee_mois = input_user_mois
        except ValueError:
            logging.exception(f"Format de date rentrée invalide, date par défaut sélectionnée. -> {date_annee_mois}")

    date_res = datetime.datetime.strptime(date_annee_mois, "%Y-%m")
    print(f"Mois sélectionné : {date_res}")

    # Selection du réseau SANDRE à utiliser
    reseaux_sandre = "BSH001"
    print("Choisissez un réseau SANDRE : BSH001 (par défaut)")
    print("Rentrez 'custom' pour utiliser la liste custom.")
    input_reseaux_sandre = input(" -> ")
    if input_reseaux_sandre != "":
        reseaux_sandre = input_reseaux_sandre
    print(f"Réseau Sandre sélectionné : {reseaux_sandre}")

    is_graphic_genere = False
    if res_generation_carte in ["2", "3"]:
        is_graphic_genere = prompt_for_graphic()

    logging.info("Génération en cours...")
    # On génère les stations ouverte lors de date_annee_mois
    plot_grandeur.create_geojson_from_stations(reseaux_sandre, date_annee_mois)
    # On génère les sites correspondant au réseaux_sandre
    plot_grandeur.create_geojson_from_sites(reseaux_sandre)
    # On génère les stations du réseaux sandre, même celle qui ne sont pas ouverte
    plot_grandeur.create_geojson_from_stations(reseaux_sandre, None)
    # On génère toutes les stations et tous les sites que l'on a.
    plot_grandeur.create_geojson_from_stations(None, None)
    plot_grandeur.create_geojson_from_sites(None)

    if res_generation_carte == "1":
        plot_grandeur.create_geojson_from_hydraulicite(date_annee_mois, reseaux_sandre)
    elif res_generation_carte == "2":
        plot_grandeur.create_geojson_from_periode_de_retour(date_annee_mois, reseaux_sandre, is_graphic_genere)
    elif res_generation_carte == "3":
        plot_grandeur.create_geojson_from_hydraulicite(date_annee_mois, reseaux_sandre)
        plot_grandeur.create_geojson_from_periode_de_retour(date_annee_mois, reseaux_sandre, is_graphic_genere)

def generer_meteo_carte(res_generation_carte:str):
    print("Vous souhaitez générer des carte à partir de données météo.")
    print()
    print("Quel échelle temporelle souhaitez vous ?")
    print("(1) MENSUELLE")
    print("(2) QUOTIDIENNE (défaut)")
    res_prompt = input(" -> ")
    choix_res = "2"
    if res_prompt in ["1", "2"]:
        choix_res = res_prompt

    is_mens_generated = False
    is_quot_generated = False
    if choix_res == "1":
        is_mens_generated = True
    if choix_res == "2":
        is_quot_generated = True

    print()
    print("Quel type de données voulez vous ?")
    print("(1) Données sans pré-calcul")
    print("(2) SIM2 (défaut)")
    res_prompt = input(" -> ")
    choix_res = "2"
    if res_prompt in ["1", "2"]:
        choix_res = res_prompt

    is_sim2_generated = False
    is_classic_generated = False
    if choix_res == "1":
        is_classic_generated = True
    if choix_res == "2":
        is_sim2_generated = True

    format_date = "AAAAMMJJ" if is_quot_generated else "AAAAMM"
    formater_date = "%Y%m%d" if is_quot_generated else "%Y%m"

    print(f"Quelles date de début souhaitez vous ? ({format_date})")
    res_prompt = input(" -> ")
    date_start = datetime.strptime(res_prompt, formater_date)
    print(f"Date de départ : {date_start}")

    print(f"Quelles date de fin souhaitez vous (inclus dans l'intervalle) ? ({format_date})")
    res_prompt = input(" -> ")
    date_end = datetime.strptime(res_prompt, formater_date)
    print(f"Date de fin : {date_end}")


    print("Souhaitez vous aggréger les données dans cet intervalle ? O/n")
    print("Si vous n'aggrégez pas les données, des graphiques jour par jour seront générés en plus.")
    res_prompt = input(" -> ")
    is_data_aggregated = True
    if "n" in res_prompt.lower():
        is_data_aggregated = False

    if is_quot_generated:
        if is_classic_generated:
            print(f"Génération des données classiques quotidiennes de {date_start} à {date_end}")
            plot_meteoFrance.export_all_format_geojson_range(MeteoFranceDataType.QUOT, date_start, date_end, is_data_aggregated)
        if is_sim2_generated:
            print(f"Génération des données SIM2 quotidiennes de {date_start} à {date_end}")
            plot_meteoFrance.export_all_format_geojson_range(MeteoFranceDataType.SIM2_QUOT, date_start, date_end, is_data_aggregated)
    if is_mens_generated:
        if is_classic_generated:
            print(f"Génération des données classique mensuelles de {date_start} à {date_end}")
            plot_meteoFrance.export_all_format_geojson_range(MeteoFranceDataType.MENS, date_start, date_end, is_data_aggregated)
        if is_sim2_generated:
            print(f"Génération des données SIM2 mensuelles de {date_start} à {date_end}")
            plot_meteoFrance.export_all_format_geojson_range(MeteoFranceDataType.SIM2_MENS, date_start, date_end, is_data_aggregated)


if __name__ == "__main__":
    print("Bienvenue dans le client de génération de cartes, que souhaitez vous faire ?")

    # Selection de la carte à générer
    print("1 : Générer une carte d'hydraulicité")
    print("2 : Générer une carte de vcn3/période de retour")
    print("3 : Générer les deux (lent au premier lancement)")
    print("4 : Générer des extraits MétéoFrance (défaut)")
    input_carte_a_generer = input(" -> ")
    res_generation_carte = "4"
    if input_carte_a_generer in ["1", "2", "3", "4"]:
        res_generation_carte = input_carte_a_generer
    print(f"Choix de génération de carte : {res_generation_carte}")

    if res_generation_carte in ["1", "2", "3"]:
        generer_hubeau_graph(res_generation_carte)
    else:
        generer_meteo_carte(res_generation_carte)

    logging.info("\nGénération terminée.")
