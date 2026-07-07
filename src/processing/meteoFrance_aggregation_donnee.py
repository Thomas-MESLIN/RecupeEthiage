import src.io.download_meteoFrance as dm
from src.io.download_meteoFrance import MeteoFranceDataType
import pandas as pd
from datetime import datetime
from pathlib import Path
from enum import Enum


class GroupByMethod(Enum):
    BY_POSITION = 0
    BY_DATE = 1

def aggregate_range(data_freq:MeteoFranceDataType, df_to_aggregate:pd.DataFrame, aggregation_method : GroupByMethod):
    """
    Prend un df en argument, aggrège selon chaque paramètre, en fonction de si on à une somme ou une moyenne à faire
    :param aggregation_method: La manière dont les données sont aggrégé, cela peut-être fait par la position géographique ou par la DATE
    :param data_freq: Le type de donnée présent dans le Dataframe
    :param df_to_aggregate: Le Dataframe à aggréger
    :return: Un DataFrame, contenant les données aggrégé.
    """
    match data_freq:
        case MeteoFranceDataType.SIM2_QUOT:
            # Colonne inconnue pour aggréger : HTEURNEIGEX, TINF_H, TSUP_H
            group_by_position_columns = ["LAMBX", "LAMBY"]
            columns_to_sum = ["PRENEI","PRELIQ","DLI","SSI","EVAP", "ETP", "PE", "DRAINC", "RUNC", "ECOULEMENT"]
            columns_to_mean = ["T","FF","Q","HU", "SWI", "SSWI_10J", "RESR_NEIGE", "RESR_NEIGE6", "HTEURNEIGE", "HTEURNEIGE6", "SNOW_FRAC", "WG_RACINE","WGI_RACINE"]
        case MeteoFranceDataType.SIM2_MENS:
            group_by_position_columns = ["LAMBX", "LAMBY"]
            columns_to_sum = ["PRENEI", "PRELIQ", "PRETOTM", "EVAP", "ETP", "PE", "DRAINC", "RUNC", "ECOULEMENT"]
            columns_to_mean = ["T", "SWI","SPI1", "SPI3", "SPI6", "SPI12", "SSWI1", "SSWI3", "SSWI6", "SSWI12"]
        case MeteoFranceDataType.QUOT:
            # Colonne inconnue pour aggréger : TN, TX,
            group_by_position_columns = ["LAT", "LON"]
            columns_to_sum = ["RR"]
            columns_to_mean = ["INFRART", "UV", "TM", "TNTXM", "TAMPLI", "DG", "FFM", "FF2M", "DXY", "DXI", "DXI2", "DRR", "PMERM", "INST", "GLOT", "DIFT"
                               ,"DIRT", "SIGMA", "UN","UX", "UM","DHUMI40", "DHUMI80", "TSVM", "ETPMON", "ETPGRILLE", "ECOULEMENTM", "HNEIGEF"]
        case MeteoFranceDataType.MENS:
            # Colonne inconnue pour aggréger : TN, TX,
            group_by_position_columns = ["LAT", "LON"]
            columns_to_sum = ["RR", "RR_ME"]
            columns_to_mean = ["RRAB", "PMERM", "PMERMINAB", "TX", "TX_ME", "TXAB", "TXMIN", "TN", "TN_ME",
                               "TNAB", "TNMAX", "TAMPLIM", "TAMPLIAB", "TM", "TMM", "TMMIN", "TMMAX", "UNAB", "NBUN", "UXAB",
                               "UMM", "TSVM", "TSVM", "ETP", "FXIAB", "FXI3SAB", "FXYAB", "FFM", "INST", "GLOT", "DIFT", "DIRT",
                               "HNEIGEFTOT", "HNEIGEFAB", "NEIGETOTM", "NEIGETOTAB"]
        case _:
            raise NotImplementedError

    dico_operation = {}
    match aggregation_method:
        case GroupByMethod.BY_POSITION:
            df_grouped_by = df_to_aggregate.groupby(by=group_by_position_columns)
            match data_freq:
                case MeteoFranceDataType.SIM2_QUOT | MeteoFranceDataType.SIM2_MENS:
                    dico_operation["DATE"] = ["min", "max"]
                case MeteoFranceDataType.QUOT:
                    dico_operation["AAAAMMJJ"] = ["min", "max"]
                case MeteoFranceDataType.MENS:
                    dico_operation["AAAAMM"] = ["min", "max"]
            dico_operation["DATE_DATETIME"] = ["min", "max"]
        case GroupByMethod.BY_DATE:
            df_grouped_by = df_to_aggregate.groupby(by=["DATE_DATETIME"])

    for column in columns_to_sum:
        dico_operation[column] = ["sum"]
    for column in columns_to_mean:
        dico_operation[column] = ["mean"]


    df_grouped_by_aggregated = df_grouped_by.agg(dico_operation)

    # On enlève LAMBX et LAMBY des index pour qu'ils redeviennent des colonnes "normales".
    df_grouped_by_aggregated.reset_index(inplace=True)

    match aggregation_method:
        case GroupByMethod.BY_POSITION:
            df_grouped_by_aggregated.columns = [
                f"{col1}_{col2}" if "DATE" in col1 or "AAAAMM" in col1 else col1
                for col1, col2 in df_grouped_by_aggregated.columns
            ]
        case GroupByMethod.BY_DATE:
            df_grouped_by_aggregated.columns = [
                col1 for col1, _ in df_grouped_by_aggregated.columns
            ]

    return df_grouped_by_aggregated


if __name__ == "__main__":
    df_to_aggregate = dm.get_data_in_range(MeteoFranceDataType.SIM2_QUOT, datetime(2026,5,1),datetime(2026,5,7))
    df_aggregated = aggregate_range(MeteoFranceDataType.SIM2_QUOT, df_to_aggregate)
    df_to_aggregate.to_csv(Path("output/test/df_a_aggreger.csv"), index=False)
    df_aggregated.to_csv(Path("output/test/df_aggrege.csv"), index=False)
