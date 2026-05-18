from cl_hubeau import hydrometry
#from pathlib import Path

# dossier vers lequel mettre les résultats
#dest_folder = Path("output")
#fields=["resultat_obs_elab", "code_site", "date_obs_elab"]
#fields=[]
df = hydrometry.get_all_stations()
#df.to_csv(dest_folder / 'stations.csv')