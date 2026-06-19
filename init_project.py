from pathlib import Path
# USAGE : The script sert à créer l'arborescence de dossier utilisé par les différents scritps

output_folder = Path("output")
output_folder.mkdir(exist_ok=True)

# Hubeau folder
hubeau_folder = output_folder / "hubeau"

# Hydroportail folder
hydroportail_folder = output_folder / "hydroportail"

# Hierarchie of each folder :
folder_to_create = [
    Path("cleaned_data"),
    Path("downloaded_data"),
    Path("downloaded_data/observations_elaboree"),
    Path("downloaded_data/sites"),
    Path("downloaded_data/stations"),
    Path("QmM_moyen"),
]

# Création de l'arborescence en dessous de chaque folder
for parent_folder in [hydroportail_folder,hubeau_folder]:
    parent_folder.mkdir(exist_ok=True)
    for folder in folder_to_create:
        res_folder = parent_folder / folder
        res_folder.mkdir(exist_ok=True)

result_folder = [
    Path("hydraulicite"),
    Path("QGIS"),
    Path("QGIS/stations"),
    Path("QGIS/sites"),
    Path("QGIS/VCN3_periode_de_retour"),
    Path("QGIS/hydraulicite"),
    Path("QGIS/sites"),
    Path("QGIS/meteoFrance"),
    Path("QGIS/meteoFrance/bassin"),
    Path("QGIS/meteoFrance/departement"),
    Path("QGIS/meteoFrance/region_administrative"),
    Path("VCN3"),
    Path("VCN3/stations"),
    Path("VCN3/plot_stations"),
    Path("VCN3/analyse_frequence_periode"),
    Path("VCN3/mensuel"),
    Path("VCN3/moyenne_historique"),
    Path("site_station_custom"),
    Path("meteoFrance"),
    Path("meteoFrance/departement_id_datagouv"),
    Path("meteoFrance/downloaded_data"),
    Path("meteoFrance/downloaded_data/mens_historique"),
    Path("meteoFrance/downloaded_data/mens_historique_archive"),
    Path("meteoFrance/downloaded_data/mens_sim2"),
    Path("meteoFrance/downloaded_data/mens_sim2_archive"),
    Path("meteoFrance/downloaded_data/quot_sim2"),
    Path("meteoFrance/downloaded_data/quot_sim2_archive"),
    Path("meteoFrance/downloaded_data/delimitation_qgis"),
    Path("meteoFrance/downloaded_data/delimitation_qgis_archive"),
]

for folder in result_folder:
    ("output" / folder).mkdir(exist_ok=True)
