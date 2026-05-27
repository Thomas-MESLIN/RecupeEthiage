from cl_hubeau import hydrometry
from pathlib import Path
import os
from datetime import datetime
import calendar

#def download_hubeau_france(annee_mois : str, grandeur_souhaite : str):

# Permet d'accéder à internet via le réseau interne de la DREAL
os.environ['http_proxy'] = 'http://pfrie-std.proxy.e2.rie.gouv.fr:8080'
os.environ['HTTP_PROXY'] = 'http://pfrie-std.proxy.e2.rie.gouv.fr:8080'
os.environ['https_proxy'] = 'http://pfrie-std.proxy.e2.rie.gouv.fr:8080'
os.environ['HTTPS_PROXY'] = 'http://pfrie-std.proxy.e2.rie.gouv.fr:8080'

# dossier vers lequel mettre les résultats
dest_folder = Path("output/hubeau/downloaded_data/observations_elaboree")

# Bounding box grossière du bassin versant Auvergne-Rhône-Alpes
bounding_box_grossiere = [2.307129,42.749916,7.734375,47.279318]

date_actuelle = datetime.now().strftime("%Y-%m")

# Format de date AAAA-MM-JJ
annee_mois_souhaite = "-1"
while len(annee_mois_souhaite) != 7 and annee_mois_souhaite != "":
    annee_mois_souhaite = input(f"Quelle année et mois souhaitez vous télécharger ? (AAAA-MM) (par défaut le mois actuel -> {date_actuelle}): ")
    if len(annee_mois_souhaite) != 7 and annee_mois_souhaite != "":
        print(f"Attention au format ! exemple {date_actuelle}")

if len(annee_mois_souhaite) == 0:
    annee_mois_souhaite = date_actuelle


dernier_jour = calendar.monthrange(int(annee_mois_souhaite[0:4]), int(annee_mois_souhaite[5:]))[1]

date_debut_observation = f"{annee_mois_souhaite}-01"
date_fin_observation = f"{annee_mois_souhaite}-{dernier_jour}"

print(f"Période téléchargée : {date_debut_observation}->{date_fin_observation}")

# Données souhaitées parmi (HIXM, HIXnJ, QINM, QINnJ, QixM, QIXnJ, QmM ou QmnJ)
grandeur_hydro = ["QmM"]

# Format des données souhaité, pour n'avoir que les bons champs parmi
# code_site,code_station,date_obs_elab,resultat_obs_elab,date_prod,code_statut,libelle_statut,code_methode,libelle_methode,code_qualification,libelle_qualification,longitude,latitude,grandeur_hydro_elab
format_attendu = [
    "code_site",
    "code_station",
    "date_obs_elab",
    "resultat_obs_elab",
    "date_prod",
    "libelle_statut",
    "libelle_methode",
    "libelle_qualification",
]

dataframe_observation = hydrometry.get_observations(
    date_debut_obs_elab=date_debut_observation,
    date_fin_obs_elab=date_fin_observation,
    grandeur_hydro_elab=grandeur_hydro,
    fields=format_attendu,
)

dataframe_observation.to_csv(dest_folder / f'observations-QmM-france-{annee_mois_souhaite}.csv')
