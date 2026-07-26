from dotenv import dotenv_values
from pathlib import Path
from pprint import pprint
from mca.core.db_butler import insert_multiple_columns_data , fetch_id_by_value
# from schema.models.file_universe import Artists
from schema.lookup.file_universe_lookup import *
from mca.core.logger import set_logger
from mca_tools.utils import api_request_handler
import csv
CONFIG_CONSTANTS = dotenv_values(Path("config",".env"))
logger = set_logger(__name__)
lastfm_api_key = CONFIG_CONSTANTS["LASTFM_API_KEY"]



def seed_country_lookup_restcountries():
    # 254 Countries
    offset = [0,100,200]
    limit = [100,100,54]
    for i in range(0, len(offset)):
        api = f"https://api.restcountries.com/countries/v5?limit={limit[i]}&offset={offset[i]}&response_fields=names,codes,region,subregion,continents&response_fields_omit=names.translations"
        data = api_request_handler(api,{'Authorization': f'Bearer {CONFIG_CONSTANTS["REST_COUNTRIES_API_KEY"]}'})
        for i in range(0,data["data"]["meta"]["count"]):
            columns_data =  {"name":data["data"]["objects"][i]["names"]["common"],
                            "official_name": data["data"]["objects"][i]["names"]["official"],
                            "alpha2":data["data"]["objects"][i]["codes"]["alpha_2"],
                            "alpha3": data["data"]["objects"][i]["codes"]["alpha_3"],
                            "numeric_code":data["data"]["objects"][i]["codes"]["ccn3"],
                            "continent":", ".join(data["data"]["objects"][i]["continents"])
                            }
            insert_multiple_columns_data(CountryLookup,columns_data)