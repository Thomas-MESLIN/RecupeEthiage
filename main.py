import datetime
from datetime import timedelta
import calendar
import plot_grandeur
import station
import logging

def prompt_for_graphic() -> bool:
    print("Souhaitez vous générer les graphiques associées au stations individuel pour le calcul des périodes de retour ? (N/o)")
    input_graphic = input(" -> ")
    res_graphic = input_graphic.lower() in ["o","oui","y","yes"]
    if res_graphic:
        logging.info("Les graphiques individuels seront générés.")
    else:
        logging.info("Les graphiques individuels ne seront pas générés.")
    return res_graphic

if __name__ == "__main__":
    print("Bienvenue dans le client de génération de cartes, que souhaitez vous faire ?")

    # Selection de la carte à générer
    print("1 : Générer une carte d'hydraulicité")
    print("2 : Générer une carte de vcn3/période de retour")
    print("3 : Générer les deux (défaut)")
    input_carte_a_generer = input(" -> ")
    res_generation_carte = "3"
    if input_carte_a_generer in ["1", "2"]:
        res_generation_carte = input_carte_a_generer
    print(f"Choix de génération de carte : {res_generation_carte}")

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

    logging.info("Génération en cours...")
    if res_generation_carte == "1":
        plot_grandeur.create_geojson_from_hydraulicite(date_annee_mois, reseaux_sandre)
    elif res_generation_carte == "2":
        is_graphic_genere = prompt_for_graphic()
        plot_grandeur.create_geojson_from_periode_de_retour(date_annee_mois, reseaux_sandre, is_graphic_genere)
    elif res_generation_carte == "3":
        is_graphic_genere = prompt_for_graphic()
        plot_grandeur.create_geojson_from_hydraulicite(date_annee_mois, reseaux_sandre)
        plot_grandeur.create_geojson_from_periode_de_retour(date_annee_mois, reseaux_sandre, is_graphic_genere)

    logging.info("\nGénération terminée.")
