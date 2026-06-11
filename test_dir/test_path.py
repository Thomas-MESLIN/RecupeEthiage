from pathlib import Path
import utils
import pandas as pd

chemin_station = utils.get_path_stations()
print(chemin_station)
df = pd.read_csv(chemin_station)
print(df)
chemin_vcn3_station = utils.get_path_vcn3_station("U023001001")
print(chemin_vcn3_station)

#chemin_relatif_station_to_vcn3 = chemin_station.relative_to(chemin_vcn3_station,walk_up=True)
#print(chemin_relatif_station_to_vcn3)

