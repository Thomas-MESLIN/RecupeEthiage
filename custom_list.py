import utils
import pandas as pd

def clean_input_list():
    """
    Remove the duplicates entries from customs list, merge it with the custom site,
    rewrite it.

    :return: Rien
    """
    df_station = pd.read_csv("liste_station_custom.csv")
    df_site = pd.read_csv("liste_site_custom.csv")
