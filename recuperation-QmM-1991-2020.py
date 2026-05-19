from cl_hubeau import hydrometry
from pathlib import Path
import os

# Passage par le proxy de la DREAL (permet d'accéder à internet depuis le réseau interne)
proxy_http = "http://proxy.monreseau.fr:8080"

os.environ["HTTP_PROXY"] = proxy_http
os.environ["HTTPS_PROXY"] = proxy_http
os.environ["http_proxy"] = proxy_http
os.environ["https_proxy"] = proxy_http

# dossier vers lequel mettre les résultats
dest_folder = Path("output")

# Bounding box grossière du bassin versant Auvergne-Rhône-Alpes
bounding_box_grossiere = [2.307129,42.749916,7.734375,47.279318]

# Format de date AAAA-MM-JJ
date_debut_observation = "1991-01-01"
date_fin_observation = "2020-12-31"

# Données souhaitées parmi (HIXM, HIXnJ, QINM, QINnJ, QixM, QIXnJ, QmM ou QmnJ) → Voir https://hubeau.eaufrance.fr/page/api-hydrometrie#/hydrometrie/observationsElaborees%20csv
grandeur_hydro = ["QmM"]

dg = hydrometry.get_observations(
    date_debut_obs_elab=date_debut_observation,
    date_fin_obs_elab=date_fin_observation,
    grandeur_hydro_elab=grandeur_hydro,
)


dg.to_csv(dest_folder / f'observations-QmM-france-{date_debut_observation}-{date_fin_observation}.csv')
