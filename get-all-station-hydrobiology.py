from cl_hubeau import hydrobiology
from pathlib import Path

# dossier vers lequel mettre les résultats
dest_folder = Path("output")

df = hydrobiology.get_all_stations()

df.to_csv(dest_folder / 'stations.csv')

