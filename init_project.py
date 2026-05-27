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
]

for folder in result_folder:
    folder.mkdir(exist_ok=True)
