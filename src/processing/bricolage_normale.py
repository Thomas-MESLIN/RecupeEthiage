from src.model.enums import GeographicScaleClip,MeteoFranceDataType
from pathlib import Path
from datetime import datetime
import pandas as pd
import src.plotting.plot_meteoFrance as plot_meteoFrance

date_debut = datetime(2026, 6, 1)
date_fin = datetime(2026, 6, 28)

all_df = []
for annee in range(1990,2021):
    date_debut_extrait_historique = date_debut.replace(year=annee)
    date_fin_extrait_historique = date_fin.replace(year=annee)

    df_panda = plot_meteoFrance.df_range_processed(MeteoFranceDataType.SIM2_QUOT, date_debut_extrait_historique, date_fin_extrait_historique, True)
    df_panda["DATE"] = df_panda["DATE_min"]
    df_panda["DATE_DATETIME"] = df_panda["DATE_DATETIME_min"]
    all_df.append(df_panda)

df_concatenated = pd.concat(all_df, ignore_index=True)

df_groupped_by = df_concatenated.groupby(by=["LAMBX","LAMBY"])
df_aggregated = df_groupped_by.agg({
    "DATE":"first",
    "DATE_DATETIME":"first",
    "DATE_DATETIME_min":"min",
    "DATE_DATETIME_max":"max",
    "PE":"mean",
})
df_aggregated.reset_index(inplace=True)
# df_aggregated = meteoFrance_aggregation_donnee.aggregate_range(MeteoFranceDataType.SIM2_QUOT,df_concatenated,GroupByMethod.BY_POSITION)

chemin_mois_actuel = Path(f"output/QGIS/meteoFrance/QUOT-SIM2-aggregated-{date_debut.strftime('%Y%m%d')}-{date_fin.strftime('%Y%m%d')}/bassin/QUOT-SIM2-aggregated-{date_debut.strftime('%Y%m%d')}-{date_fin.strftime('%Y%m%d')}-B06.csv")
if not chemin_mois_actuel.exists():
    plot_meteoFrance.export_all_format_geojson_range(GeographicScaleClip.BASSIN, MeteoFranceDataType.SIM2_QUOT, date_debut, date_fin, True)
df_donnee_actuelle = plot_meteoFrance.df_range_processed(MeteoFranceDataType.SIM2_QUOT, date_debut, date_fin, True)
# df_donnee_actuelle = plot_meteoFrance.export_to_every_geographic_element(MeteoFranceDataType.SIM2_QUOT, GeographicScaleClip.BASSIN,df_donnee_actuelle,is_data_aggregated=True)

df_ref = df_aggregated.set_index(["LAMBX", "LAMBY"])
df_actuel = df_donnee_actuelle.set_index(["LAMBX", "LAMBY"])

# On adapte pour pouvoir faire un rapport sur 28 jours et pas 30.
df_actuel["PE_rapport_normale"] = (df_actuel["PE"]) / df_ref["PE"].abs().clip(lower=0.1)
df_actuel.reset_index(inplace=True)
df_lambert2 = plot_meteoFrance.to_lambert2_geodataframe(MeteoFranceDataType.SIM2_QUOT, df_actuel)

chemin_plot_normale = Path(f"output/QGIS/meteoFrance/QUOT-SIM2-NORMALES-{date_debut.strftime('%Y%m%d')}-{date_fin.strftime('%Y%m%d')}/bassin/QUOT-SIM2-NORMALES-{date_debut.strftime('%Y%m%d')}-{date_fin.strftime('%Y%m%d')}.geojson")
chemin_plot_normale.parent.mkdir(exist_ok=True, parents=True)
plot_meteoFrance.plot_geojson_from_lambert2(chemin_plot_normale,df_lambert2)
