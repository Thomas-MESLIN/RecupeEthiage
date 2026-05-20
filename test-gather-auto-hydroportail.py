from time import sleep

import requests
import pandas as pd
from pathlib import Path

# ==========================================
# PARAMÈTRES
# ==========================================

def download_hydro(sandre_code:str,start_date:str):
    """
    Télécharge l'exctration hydroportail correspondant au mois et à l'année de la start_date et en utilisant le code sandre dans la requête hydroportail.
    :param sandre_code: Code sandre filtré par la requete hydroportail
    :param start_date: Mois et année au format "AAAA-MM-01T00:00:00Z"
    """
    rdds = sandre_code
    start_at = start_date
    output_folder = Path("output/exports_hydroportail")
    if rdds != "":
        output_file = output_folder / f"{start_at[:7]}-{rdds}-only-validated-qmm.csv"
    else:
        output_file = output_folder / f"{start_at[:7]}-only-validated-qmm.csv"

    telechargement_requis = True
    if output_file.exists():
        telechargement_requis = False

    if not telechargement_requis:
        print(f"Déjà téléchargé : {output_file}")
        return
    # ==========================================
    # URL API
    # ==========================================

    url = "https://hydro.eaufrance.fr/api/carte/donnees"

    params = {
        "data": "qmm",
        "startAt": start_at,
        "status": "validated",
        "rdds[]": rdds,
        "includeClosedEntities": "false",
    }

    # ==========================================
    # HEADERS NAVIGATEUR
    # ==========================================

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Referer": (
            "https://hydro.eaufrance.fr/carte-donnees/carte/toutes-eaux"
        ),
        "Origin": "https://hydro.eaufrance.fr",
    }

    # ==========================================
    # SESSION
    # ==========================================

    session = requests.Session()

    # IMPORTANT :
    # ouvrir d'abord la page web pour obtenir les cookies
    session.get(
        "https://hydro.eaufrance.fr/carte-donnees/carte/toutes-eaux",
        headers=headers,
    )

    # ensuite appeler l'API
    response = session.get(
        url,
        params=params,
        headers=headers,
    )
    sleep(1)

    print(response.status_code)
    print(response.url)

    response.raise_for_status()

    # ==========================================
    # JSON
    # ==========================================

    data = response.json()

    features = data["features"]

    rows = []

    for feature in features:

        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})

        coordinates = geometry.get("coordinates", [None, None])

        row = {
            **properties,
            "longitude": coordinates[0],
            "latitude": coordinates[1],
            "geometry_type": geometry.get("type"),
        }

        rows.append(row)

    df = pd.DataFrame(rows)
    #df = df[df["entityType"] == "site"]

    # ==========================================
    # EXPORT
    # ==========================================

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    print(df.head())
    print(f"\nCSV sauvegardé : {output_file}")

for annee in range(1999,2021):
    for mois in range(1,13):
        mois_str = str(mois)
        if mois < 10:
            mois = "0" + str(mois)

        annee_mois = f"{annee}-{mois}-01T00:00:00Z"

        code_sandre = "BSH101"
        download_hydro(code_sandre,annee_mois)
        code_sandre = "BSH001"
        download_hydro(code_sandre, annee_mois)
        # On télécharge toutes les stations de France
        code_sandre = ""
        download_hydro(code_sandre, annee_mois)
        print(f"Tous les fichiers de {annee}-{mois} ont été téléchargés")
