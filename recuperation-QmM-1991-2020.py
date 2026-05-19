from cl_hubeau import hydrometry
from pathlib import Path
import os

# Voir la documentation Hub'eau
# https://hubeau.eaufrance.fr/page/api-hydrometrie#/hydrometrie/observationsElaborees%20csv
# Voir la documentation Hub'eau
# https://hubeau.eaufrance.fr/page/api-hydrometrie#/hydrometrie/observationsElaborees%20csv


# Passage par le proxy de la DREAL (permet d'accéder à internet depuis le réseau interne)
proxy_http = "http://proxy.monreseau.fr:8080"
proxy_https = "https://proxy.monreseau.fr:8080"

os.environ["HTTP_PROXY"] = proxy_http
os.environ["HTTPS_PROXY"] = proxy_https
os.environ["http_proxy"] = proxy_http
os.environ["https_proxy"] = proxy_https

# dossier vers lequel mettre les résultats
dest_folder = Path("output")

# Bounding box grossière du bassin versant Auvergne-Rhône-Alpes
bounding_box_grossiere = [2.307129,42.749916,7.734375,47.279318]

# Format de date AAAA-MM-JJ
date_debut_observation = "1991-01-01"
date_fin_observation = "2020-12-31"

# Données souhaitées parmi (HIXM, HIXnJ, QINM, QINnJ, QixM, QIXnJ, QmM ou QmnJ) → Voir https://hubeau.eaufrance.fr/page/api-hydrometrie#/hydrometrie/observationsElaborees%20csv
grandeur_hydro = ["QmM"]

# Format des données souhaité, pour n'avoir que les bon champs parmis
# code_site,code_station,date_obs_elab,resultat_obs_elab,date_prod,code_statut,libelle_statut,code_methode,libelle_methode,code_qualification,libelle_qualification,longitude,latitude,grandeur_hydro_elab
format_attendu = ["code_site","code_station","date_obs_elab","resultat_obs_elab","date_prod","libelle_statut","libelle_methode","libelle_qualification","longitude","latitude","grandeur_hydro_elab"]

dg = hydrometry.get_observations(
    date_debut_obs_elab=date_debut_observation,
    date_fin_obs_elab=date_fin_observation,
    grandeur_hydro_elab=grandeur_hydro,
    fields=format_attendu,
)


dg.to_csv(dest_folder / f'observations-QmM-france-{date_debut_observation}-{date_fin_observation}.csv')
