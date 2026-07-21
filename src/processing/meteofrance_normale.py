from src.model.enums import GeographicScaleClip,MeteoFranceDataType
from pathlib import Path
from datetime import datetime
import pandas as pd
import src.plotting.plot_meteoFrance as plot_meteoFrance
from src.config.paths import OUTPUT_DIR
from src.model.utils import meteofrance_data_type_to_str
from src.utils.utils import get_path_meteofrance_historic_mean
from src.utils.utils_file import is_path_valid_age

def get_unit_to_mean(data_freq: MeteoFranceDataType) -> list[str]:
    """
    Renvoie la liste des colonnes dont il faut faire la moyenne lors d'un calcul historique.
    """
    match data_freq:
        case MeteoFranceDataType.SIM2_QUOT:
            return ["PRENEI","PRELIQ","T","FF","Q","DLI","SSI","HU","EVAP","ETP","PE","SWI","SSWI_10J","DRAINC","RUNC","RESR_NEIGE","RESR_NEIGE6","HTEURNEIGE","HTEURNEIGE6","HTEURNEIGEX","SNOW_FRAC","ECOULEMENT","WG_RACINE","WGI_RACINE","TINF_H","TSUP_H"]
        case MeteoFranceDataType.SIM2_MENS:
            return ["PRENEI","PRELIQ","PRETOTM","T","EVAP","ETP","PE","SWI","SPI1","SPI3","SPI6","SPI12","SSWI1","SSWI3","SSWI6","SSWI12","DRAINC","RUNC","ECOULEMENT"]
        case MeteoFranceDataType.QUOT:
            return ["RR","TN","HTN","TX","HTX","TM","TNTXM","TNSOL","TN50","DG","FFM","FF2M","FXY","DXY","HXY","FXI","DXI","HXI","FXI2","DXI2","HXI2","FXI3S","DXI3S","HXI3S","DRR","STATUS_FXI3S","STATUS_DXI3S"]
        case MeteoFranceDataType.MENS:
            return ["RR","RR_ME","RRAB","TX","TX_ME"]

def get_historic_mean(data_freq:MeteoFranceDataType, date_debut:datetime, date_fin:datetime):
    """
    Récupère les données historiques d'une unité particulière.

    Les dates de début et dates de fin doivent appartenir à la même année.
    """
    if date_debut.year != date_fin.year:
        raise ValueError("La date de début et date de fin ne sont pas de la même année.")

    if date_debut.year > date_fin.year:
        raise ValueError("La date de fin est plus tôt que la date de début.")

    chemin_historic_aggregation = get_path_meteofrance_historic_mean(data_freq, date_debut, date_fin)
    # Si le calcul des données historiques a déjà été fait, on charge juste le fichier.
    if chemin_historic_aggregation.exists() and is_path_valid_age(chemin_historic_aggregation):
        return pd.read_csv(chemin_historic_aggregation)

    # On récupère tous les dataframes de chaque années sur la période date_début-date_fin
    all_df = []
    for annee in range(1990,2021):
        date_debut_extrait_historique = date_debut.replace(year=annee)
        date_fin_extrait_historique = date_fin.replace(year=annee)

        df_panda = plot_meteoFrance.df_range_processed(data_freq, date_debut_extrait_historique, date_fin_extrait_historique, True)
        df_panda["DATE"] = df_panda["DATE_min"]
        df_panda["DATE_DATETIME"] = df_panda["DATE_DATETIME_min"]
        all_df.append(df_panda)

    df_concatenated = pd.concat(all_df, ignore_index=True)

    df_groupped_by = df_concatenated.groupby(by=["LAMBX","LAMBY"])

    # On récupère toutes les colonnes dont on doit faire la moyenne
    list_unit_to_mean = get_unit_to_mean(data_freq)

    # On crée le dictionnaire qui sert à agréger le DataFrame.
    dico_aggregation = {
        "DATE":"first",
        "DATE_DATETIME":"first",
        "DATE_DATETIME_min":"min",
        "DATE_DATETIME_max":"max",
    }

    # On fait des moyennes avec les unités
    for unit in list_unit_to_mean:
        dico_aggregation[unit] = "mean"

    df_aggregated = df_groupped_by.agg(dico_aggregation)

    df_aggregated.reset_index(inplace=True)

    df_aggregated.to_csv(chemin_historic_aggregation, index=False)

    return df_aggregated

def get_rapport_normale(geographic_scale:GeographicScaleClip, data_freq:MeteoFranceDataType, date_debut:datetime, date_fin:datetime):

    df_donnee_moyenne_historique = get_historic_mean(data_freq, date_debut, date_fin)

    chemin_donnee = OUTPUT_DIR / "QGIS" / "meteoFrance" / f"{meteofrance_data_type_to_str(data_freq)}-aggregated-{date_debut.strftime("%Y%m%d")}-{date_fin.strftime("%Y%m%d")}" / geographic_scale / f"{meteofrance_data_type_to_str(data_freq)}-aggregated-{date_debut.strftime("%Y%m%d")}-{date_fin.strftime("%Y%m%d")}.csv"
    if not chemin_donnee.exists():
        plot_meteoFrance.export_all_format_geojson_range(geographic_scale, data_freq, date_debut, date_fin, True)
    df_donnee_actuelle = plot_meteoFrance.df_range_processed(data_freq, date_debut, date_fin, True)

    df_ref = df_donnee_moyenne_historique.set_index(["LAMBX", "LAMBY"])
    df_actuel = df_donnee_actuelle.set_index(["LAMBX", "LAMBY"])

    # On construit une liste en ajoutant rapport_normale à la fin
    list_unit_to_mean = get_unit_to_mean(data_freq)
    list_unit_normale = [ f"{unit}_rapport_normale" for unit in list_unit_to_mean ]

    # On fait un très très gros ratio
    df_actuel[list_unit_normale] = (df_actuel[list_unit_to_mean]) / df_ref[list_unit_to_mean].abs().clip(lower=0.01)
    df_actuel.reset_index(inplace=True)
    df_lambert2 = plot_meteoFrance.to_lambert2_geodataframe(data_freq, df_actuel)

    # On sauvegarde le résultat
    chemin_plot_normale = OUTPUT_DIR / "QGIS" / "meteoFrance" / f"{meteofrance_data_type_to_str(data_freq)}-aggregated-{date_debut.strftime("%Y%m%d")}-{date_fin.strftime("%Y%m%d")}" / geographic_scale / f"{meteofrance_data_type_to_str(data_freq)}-RAPPORT-NORMALE-{date_debut.strftime("%Y%m%d")}-{date_fin.strftime("%Y%m%d")}.geojson"
    chemin_plot_normale.parent.mkdir(exist_ok=True, parents=True)
    plot_meteoFrance.plot_geojson_from_lambert2(chemin_plot_normale,df_lambert2)


if __name__ == "__main__":
    date_debut = datetime(2026, 6, 1)
    date_fin = datetime(2026, 6, 31)

    get_historic_mean(MeteoFranceDataType.SIM2_QUOT, date_debut, date_fin)
