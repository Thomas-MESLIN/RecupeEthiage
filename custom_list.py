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
    df_station_no_duplicate = df_station.drop_duplicates()
    df_site_no_duplicate = df_site.drop_duplicates()

    # Load the huge station list.
    df_all_station = pd.DataFrame(pd.read_csv(utils.get_path_stations()))

    df_station_custom_full = df_station_no_duplicate.merge(df_all_station, on="code_station", how="left")
    df_all_code_site_from_station = df_station_custom_full["code_site"].drop_duplicates().dropna()

    df_all_sites = df_site_no_duplicate.merge(df_all_code_site_from_station, on="code_site", how="outer")
    # df_sites_custom_full = df_site_no_duplicate.merge(df_all_station, on="code_site", how="left")
    print(f"Nombre de nouveaux sites : abs({len(df_site_no_duplicate)} - {len(df_all_sites)}) = {abs(len(df_site_no_duplicate) - len(df_all_sites))}")
    print("pas mal")

    code_site_et_station = df_all_sites.merge(df_station_custom_full, on="code_site", how="outer")
    print(code_site_et_station)
    code_site_et_station_uniquement = code_site_et_station[["code_site","code_station"]].sort_values(by="code_site")
    print("Nettoyage terminé")

    print("Récupération stations manquante.")
    code_site_station_manquante = code_site_et_station_uniquement[pd.isna(code_site_et_station_uniquement["code_station"])]
    list_site_station_manquante = code_site_station_manquante["code_site"].drop_duplicates().dropna().to_list()
    print(list_site_station_manquante)
    df_resultat = find_perfect_station(list_site_station_manquante)

    code_site_et_station_total = pd.concat([df_resultat, code_site_et_station_uniquement], ignore_index=True)
    code_site_et_station_total.sort_values(by="code_site", inplace=True)
    code_site_et_station_total.dropna(subset=["code_station"], inplace=True)
    code_site_et_station_total.to_csv("liste_site_et_station_custom.csv", index=False)


def find_perfect_station(code_site_list:list[str]) -> pd.DataFrame:
    """
    Trouve le code station qui serait le plus probablement associé à ce code site.
    :param code_site_list: Une liste de code site où il faut trouver la station correspondante
    :return: Renvoie un dataframe qui associe a un code_site une station
    """
    df_all_site = pd.DataFrame(pd.read_csv(utils.get_path_sites()))
    df_all_station = pd.DataFrame(pd.read_csv(utils.get_path_stations()))
    df_all_station = df_all_station[df_all_station["en_service"]]
    nombre_site_inexistant = 0
    nombre_absent = 0
    nombre_unique = 0
    nombre_plusieurs = 0
    list_correspondance = []
    for code_site in code_site_list:
        if len(df_all_site[df_all_site["code_site"] == code_site]) == 0:
            print(f"Le site n'existe pas. - {code_site}")
            nombre_site_inexistant += 1
            continue
        df_stations_lie = df_all_station[df_all_station["code_site"] == code_site]
        if len(df_stations_lie) == 0:
            nombre_absent += 1
            print()
            print(f"Il n'y a aucune station associé. - {code_site}")
        elif len(df_stations_lie) == 1:
            nombre_unique +=1
            code_station = df_stations_lie["code_station"].iloc[0]
            row = {"code_site": code_site, "code_station": code_station}
            list_correspondance.append(row)
            # print("Il y a exactement une station associé.")
        else:
            nombre_plusieurs += 1
            print()
            print(f"Il y a plus d'une station associé. - {code_site}")
            print(df_stations_lie["code_station"])
            for code_station in df_stations_lie["code_station"]:
                row = {"code_site": code_site, "code_station": code_station}
                list_correspondance.append(row)

    print(f"\nNombre site inexistant {nombre_site_inexistant}, \n"
          f"Nombre pas de stations correspondante {nombre_absent}, \n"
          f"Nombre 1 station correspondant {nombre_unique}, \n"
          f"Nombre plusieurs stations correspondantes {nombre_plusieurs}\n")
    df_final = pd.DataFrame(data=list_correspondance)
    return df_final

if __name__ == "__main__":
    clean_input_list()