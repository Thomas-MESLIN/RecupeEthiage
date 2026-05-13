from cl_hubeau import hydrometry
from pathlib import Path

# dossier vers lequel mettre les résultats
dest_folder = Path("output")

df = hydrometry.get_all_stations(fields=["resultat_obs_elab", "code_site", "date_obs_elab"])
dg = hydrometry.get_observations()
df.to_csv(dest_folder / 'stations.csv')
dg.to_csv(dest_folder / 'observations.csv')

