from pynsee.localdata import get_geo_list, get_descending_area
from src.utils.utils_proxy import set_up_working_proxy
from functools import cache
import pandas as pd

@cache
def get_regions_df() -> pd.DataFrame:
    set_up_working_proxy()
    return get_geo_list("regions").set_index("CODE")

@cache
def get_departements_from_regions_df(code_region:str) -> pd.DataFrame:
    set_up_working_proxy()
    return get_descending_area(area="region", code=code_region, type="departement").set_index("code")

@cache
def get_departements_from_regions(code_region:str) -> list[str]:
    return get_departements_from_regions_df(code_region).index.to_list()

@cache
def get_region_name(code_region:str) -> str|None:
    if code_region in get_regions_df().index:
        return get_regions_df().loc[code_region]["TITLE"]
    else:
        return None

@cache
def get_departement_name(code_region:str, code_departement:str) -> str|None:
    if code_departement in get_departements_from_regions_df(code_region).index:
        return get_departements_from_regions_df(code_region).loc[code_departement]["intitule"]
    else:
        return None

if __name__ == "__main__":
    print(get_departements_from_regions("84"))
    print(get_departement_name("84","01"))
    print(get_region_name("84"))
