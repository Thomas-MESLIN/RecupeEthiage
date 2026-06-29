import argparse
from datetime import timedelta, datetime
import calendar
import plot_grandeur
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
    date_today = datetime.now()
    date_mois_precedent = date_today - timedelta(date_today.day)
    date_annee_mois = date_mois_precedent.strftime("%Y-%m")
    date_res = date_mois_precedent
    print("Choisissez la date que vous voulez générer : ")
    print(f"Format AAAA-MM, (mois précédent : {date_annee_mois} par défaut)")
    input_user_mois = input(" -> ")
    if input_user_mois != "" and len(input_user_mois) == 7:
        try:
            parsed_date = datetime.strptime(input_user_mois, "%Y-%m")
            date_annee_mois = input_user_mois
            date_res = parsed_date
        except ValueError:
            logging.exception(f"Format de date rentrée invalide, date par défaut sélectionnée. -> {date_annee_mois}")

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

    print("Souhaitez vous mettre à jour les données téléchargés ? N/y")
    res = input(" -> ")
    has_data_updated = 'y' in res.lower()

    if has_data_updated:
        print("Souhaitez vous mettre à jour l'index des données ? N/y")
        res = input(" -> ")
        has_index_updated = 'y' in res.lower()
    else:
        has_index_updated = False

    data_freq = MeteoFranceDataType.QUOT
    if is_quot_generated:
        if is_classic_generated:
            print(f"Génération des données classiques quotidiennes de {date_start} à {date_end}")
            data_freq = MeteoFranceDataType.QUOT
        if is_sim2_generated:
            print(f"Génération des données SIM2 quotidiennes de {date_start} à {date_end}")
            data_freq = MeteoFranceDataType.SIM2_QUOT
    if is_mens_generated:
        if is_classic_generated:
            print(f"Génération des données classique mensuelles de {date_start} à {date_end}")
            data_freq = MeteoFranceDataType.MENS
        if is_sim2_generated:
            print(f"Génération des données SIM2 mensuelles de {date_start} à {date_end}")
            data_freq = MeteoFranceDataType.SIM2_MENS

    plot_meteoFrance.export_all_format_geojson_range(data_freq, date_start, date_end, is_data_aggregated, has_index_updated, has_data_updated)


def interactif_start():
    print("Bienvenue dans le client de génération de cartes interactif, que souhaitez vous faire ?")
    print("(Il est aussi possible de lancer le script en mode CLI (-h))")

    # Selection de la carte à générer
    print("1 : Générer une carte d'hydraulicité")
    print("2 : Générer une carte de vcn3/période de retour")
    print("3 : Générer les deux (lent au premier lancement)")
    print("4 : Générer des extraits MétéoFrance (défaut)")
    input_carte_a_generer = input(" -> ")
    res_generation_carte_choice = "4"
    if input_carte_a_generer in ["1", "2", "3", "4"]:
        res_generation_carte_choice = input_carte_a_generer
    print(f"Choix de génération de carte : {res_generation_carte_choice}")

    if res_generation_carte_choice in ["1", "2", "3"]:
        generer_hubeau_graph(res_generation_carte_choice)
    else:
        generer_meteo_carte(res_generation_carte_choice)

def main(
    type_carte: str,
    start_date: datetime,
    end_date: datetime,
    reseau_sandre: str,
    has_vcn3_graphic: bool = False,
    has_meteo_aggregate: bool = False,
    has_meteo_index_update: bool = True,
    has_meteo_update: bool = True,
):
    """
    Génère les geojson à partir des arguments d'entrée du CLI.
    :param type_carte:
    :param start_date:
    :param end_date:
    :param reseau_sandre:
    :param has_vcn3_graphic:
    :param has_meteo_aggregate:
    :param has_meteo_index_update:
    :param has_meteo_update: Autorise le script meteo à mettre ses données à jour.
    :return:
    """
    if not has_meteo_update:
        has_meteo_index_update = False

    match type_carte:
        case "hydraulicite":
            plot_grandeur.create_geojson_from_hydraulicite(start_date.strftime("%Y-%m"), reseau_sandre)
        case "vcn3":
            plot_grandeur.create_geojson_from_periode_de_retour(start_date.strftime("%Y-%m"), reseau_sandre, has_vcn3_graphic)
        case "meteo_brut_MENS":
            plot_meteoFrance.export_all_format_geojson_range(MeteoFranceDataType.MENS, start_date, end_date, has_meteo_aggregate, has_index_update=has_meteo_index_update, has_update=has_meteo_update)
        case "meteo_sim2_MENS":
            plot_meteoFrance.export_all_format_geojson_range(MeteoFranceDataType.SIM2_MENS, start_date, end_date, has_meteo_aggregate, has_index_update=has_meteo_index_update, has_update=has_meteo_update)
        case "meteo_brut_QUOT":
            plot_meteoFrance.export_all_format_geojson_range(MeteoFranceDataType.QUOT, start_date, end_date, has_meteo_aggregate, has_index_update=has_meteo_index_update, has_update=has_meteo_update)
        case "meteo_sim2_QUOT":
            plot_meteoFrance.export_all_format_geojson_range(MeteoFranceDataType.SIM2_QUOT, start_date, end_date, has_meteo_aggregate, has_index_update=has_meteo_index_update, has_update=has_meteo_update)
        case _:
            raise NotImplementedError

def try_format_date(date_to_format:str,is_last_day:bool) -> datetime|None:
    """
    Tente de reconnaitre le format d'une date et renvoie la date formatté.
    :param date_to_format: La date à formatter.
    :param is_last_day: Si à True, Renvoie le dernier jour du mois.
    :return: Une date formatté si l'opération a été réussi ou None si la date n'a pas été reconnue.
    """
    try:
        return datetime.strptime(date_to_format, "%Y-%m-%d")
    except ValueError:
        pass
    try:
        res = datetime.strptime(date_to_format, "%Y-%m")
        res.replace(day=1)
        if is_last_day:
            res.replace(day=calendar.monthrange(res.year, res.month)[1])
    except ValueError:
        pass

    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exporter des données hydrologiques/météorologiques.",
                                     epilog="N'hésitez pas à rapporter des bugs ou des suggestions sur la page github : https://github.com/Thomas-MESLIN/RecupeEthiage")
    parser.add_argument("--type", choices=["hydraulicite", "vcn3", "meteo_brut_MENS", "meteo_sim2_MENS", "meteo_brut_QUOT", "meteo_sim2_QUOT"])
    parser.add_argument("--start_date", help="Format: AAAA-MM-JJ|AAAA-MM (défaut le début du mois précédent)")
    parser.add_argument("--end_date", help="Format: AAAA-MM-JJ|AAAA-MM (borne incluse) (défaut - fin du mois précédent)")
    parser.add_argument("--reseau_sandre", help="Le réseau SANDRE que vous souhaitez utiliser (défaut BSH001), custom pour utiliser la liste de sites/stations custom")
    parser.add_argument("--vcn3_graphic", action='store_true', help="[VCN3] Si présent, des graphiques individuels seront générés pour chaque stations")
    parser.add_argument("--meteo_aggregate", action='store_true', help="[météo] Si présent, les données seront aggrégés sur la période sélectionnée")
    parser.add_argument("--meteo_no_index_update", action='store_false', help="[météo] Si présent, l'index de correspondance entre les fichiers enregistré des dataset et leur id_datagouv ne sera pas mis à jour.")
    parser.add_argument("--meteo_no_update", action='store_false',help="[météo] Si présent, aucune données ne sera mis à jour. Peut servir pour les données quotidiennes brut où il peut y avoir beaucoup de mis à jour.")

    args = parser.parse_args()

    start_date = try_format_date(args.start_date,is_last_day=False)
    # Si la date de début est vide, on remplace par le premier jour du mois précédent
    if start_date is None:
        start_date = (datetime.today().replace(day=1) - timedelta(days=1)).replace(day=1)
        logging.info(f"Utilisation de la start_date par défaut : {start_date}")

    end_date = try_format_date(args.end_date,is_last_day=True)
    # Si la date de fin est vide, on remplace par le dernier jour du mois précédent
    if end_date is None:
        end_date = datetime.today().replace(day=1) - timedelta(days=1)
        logging.info(f"Utilisation de la end_date par défaut : {end_date}")

    if args.type is None:
        logging.error("Le type de données souhaité n'est pas spécifié !")
        logging.info("Passage en mode interactif !")
    else:
        main(args.type,
             start_date,
             end_date,
             args.reseau_sandre,
             args.vcn3_graphic,
             args.meteo_aggregate,
             args.meteo_no_index_update,
             args.meteo_no_update,
        )

    logging.info("\nGénération terminée.")
