from cl_hubeau import hydrometry
from pathlib import Path

# dossier vers lequel mettre les résultats
dest_folder = Path("output")
#fields=["resultat_obs_elab", "code_site", "date_obs_elab"]
#fields=[]
df = hydrometry.get_all_stations()
df.to_csv(dest_folder / 'stations.csv')

# Bounding box grossière du bassin versant Auvergne-Rhône-Alpes
bounding_box_grossiere = [2.307129,42.749916,7.734375,47.279318]
# Petite bounding box autour de Lyon pour tester
bounding_box_lyon = [4.130859,45.431642,5.559082,46.136066]
# bbox=bounding_box_lyon,

# Format de date AAAA-MM-JJ
date_debut_observation = "2026-01-01"
date_fin_observation = "2026-02-01"

dg = hydrometry.get_observations(date_debut_obs_elab=date_debut_observation,date_fin_obs_elab=date_fin_observation)

# Quelle que soit la bounding box choisie, le programme va quand même query absolument toutes les sources de données...
# Ce qui résulte en une extraction durant 2h...

dg.to_csv(dest_folder / 'observations-janvier-france.csv')
