from cl_hubeau import hydrometry
from pathlib import Path
import os

# Permet d'accéder à internet via le réseau interne de la DREAL
os.environ['http_proxy'] = 'http://pfrie-std.proxy.e2.rie.gouv.fr:8080'
os.environ['HTTP_PROXY'] = 'http://pfrie-std.proxy.e2.rie.gouv.fr:8080'
os.environ['https_proxy'] = 'http://pfrie-std.proxy.e2.rie.gouv.fr:8080'
os.environ['HTTPS_PROXY'] = 'http://pfrie-std.proxy.e2.rie.gouv.fr:8080'

# dossier vers lequel mettre les résultats
dest_folder = Path("output/hubeau/downloaded_data")
#fields=["resultat_obs_elab", "code_site", "date_obs_elab"]
#fields=[]
df = hydrometry.get_all_stations()
df.to_csv(dest_folder/ 'stations' / 'stations.csv')
station_geojson = df.to_json(default=str)
with open(dest_folder/ 'stations' / 'stations.geojson', 'w') as file:
    file.write(station_geojson)

df = hydrometry.get_all_sites()
df.to_csv(dest_folder / 'sites' / 'sites.csv')
sites_geojson = df.to_json(default=str)
with open(dest_folder / 'sites' / 'sites.geojson', 'w') as file:
    file.write(sites_geojson)

# Bounding box grossière du bassin versant Auvergne-Rhône-Alpes
bounding_box_grossiere = [2.307129,42.749916,7.734375,47.279318]
# Petite bounding box autour de Lyon pour tester
bounding_box_lyon = [4.130859,45.431642,5.559082,46.136066]
# bbox=bounding_box_lyon,

# Format de date AAAA-MM-JJ
date_debut_observation = "2026-01-01"
date_fin_observation = "2026-01-31"

#dg = hydrometry.get_observations(date_debut_obs_elab=date_debut_observation,date_fin_obs_elab=date_fin_observation)

# Quelle que soit la bounding box choisie, le programme va quand même query absolument toutes les sources de données...
# Ce qui résulte en une extraction durant 2h...

#dg.to_csv(dest_folder / 'observations-janvier-france.csv')
