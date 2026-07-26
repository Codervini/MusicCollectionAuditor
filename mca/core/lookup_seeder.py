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

def seed_gender_lookup():
    genders = [
    ("Male",                "Identifies as male"),
    ("Female",              "Identifies as female"),
    ("Trans Male",          "Identifies as trans male"),
    ("Trans Female",        "Identifies as trans female"),
    ("Non-binary",          "Identifies outside the male/female binary"),
    ("Genderqueer",         "Identifies as genderqueer or gender non-conforming"),
    ("Genderfluid",         "Gender identity that shifts over time"),
    ("Agender",             "Identifies as having no gender"),
    ("Bigender",            "Identifies as two genders"),
    ("Androgyne",           "Identifies as androgynous or between genders"),
    ("Two-Spirit",          "Indigenous North American third-gender identity"),
    ("Intersex",            "Born with variations in sex characteristics"),
    ("Boy Group",           "All-male musical group"),
    ("Girl Group",          "All-female musical group"),
    ("Mixed Group",         "Mixed-gender musical group"),
    ("Trans Male Group",    "Group identifying as trans male"),
    ("Trans Female Group",  "Group identifying as trans female"),
    ("Mixed Trans Group",   "Group with mixed trans gender identities"),
    ("Not Applicable",      "Entity for which gender is not applicable"),
    ("Unknown",             "Gender not known or not recorded"),
    ("Prefer Not to Say",   "Gender withheld by choice"),
    ]
    for i in genders:
        insert_multiple_columns_data(GenderLookup,{"name":i[0],"description":i[1]})
    logger.debug("Gender Lookup Seeded")

def seed_artist_type_lookup():
    artist_types = [
    ("Person",      "A single individual artist"),
    ("Group",       "A band, ensemble, or musical group"),
    ("Choir",       "A vocal ensemble or chorus"),
    ("Orchestra",   "A large classical or symphonic ensemble"),
    ("Character",   "A fictional or animated character"),
    ("Other",       "An artist type that does not fit standard categories"),
    ("Unknown",     "Artist type not known or not recorded"),
    ]
    for i in artist_types:
        insert_multiple_columns_data(ArtistTypeLookup,{"name":i[0],"description":i[1]})
    logger.debug("Artist Type Lookup Seeded")


seed_artist_type_lookup()
seed_gender_lookup()
seed_country_lookup_restcountries()