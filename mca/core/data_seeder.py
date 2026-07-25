import requests
from dotenv import dotenv_values
from pathlib import Path
from pprint import pprint
from mca.core.db_butler import insert_multiple_columns_data
from schema.models.file_universe import Artists
from schema.lookup.file_universe_lookup import *
from mca.core.logger import set_logger
import csv
CONFIG_CONSTANTS = dotenv_values(Path("config",".env"))
logger = set_logger(__name__)
lastfm_api_key = CONFIG_CONSTANTS["LASTFM_API_KEY"]



def discover_artists_lastfm(limit:int = 50):
    response = requests.get(f"http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&api_key={lastfm_api_key}&format=json&limit={limit}")
    logger.debug("API dal response: %s", response)
    dictt = {}
    if response.status_code == 200:
        data = response.json()
        logger.debug("Response dal data: %s", data)
        for i in data["artists"]["artist"]:
            # pprint(f"{i.get("name",None)} + {i.get("mbid",None)}")
            name =i.get("name","")
            dictt[name] = i.get("mbid","")
        return dictt

def discover_similar_artists_lastfm(artist,mbid = "",limit:int = 50):
    api = f"http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist=cher&api_key={lastfm_api_key}&format=json&limit={limit}&artist={artist}&mbid={mbid}"
    respone = requests.get(api)
    # pprint(respone)
    logger.debug("Artist dsa: %s", artist)
    logger.debug("API dsa response: %s", respone)
    data = {}
    if respone.status_code == 200:
        res = respone.json()
        # pprint(res)
        logger.debug("Response dsa data: %s", res)
        with open(file=Path("data","log","sussy.csv"), mode="a") as f:
            writer = csv.writer(f)
            for i in res["similarartists"]["artist"]:
                if i.get("name").find(" & ") == -1: 
                    data[i.get("name")] = [i.get("mbid", ""),i.get("match","")]
                else:
                    writer.writerow([i.get("name"),i.get("mbid", ""),i.get("match","")])

        return data
    


def feed_artists(limit):
    artist_list1 = discover_artists_lastfm(limit=969)
    # pprint(artist_list1)
    for name,mbid in artist_list1.items():
        insert_multiple_columns_data(Artists,{"name":name,"mbid":mbid})
        artist_list_2 = discover_similar_artists_lastfm(name,mbid,limit)
        for name,v in artist_list_2.items():
            insert_multiple_columns_data(Artists,{"name":name,"mbid":v[0]})
            
def api_request_handler(api,header = None):
    match header:
        case None:
            response = requests.get(api)
        case header:
            response = requests.get(api,headers=header)

    logger.debug("API response: %s", response)
    if response.status_code == 200:
        data = response.json()
        logger.debug("Response data: %s", data)
        # pprint(data)
        return data
    
def mb_artist_props_feeder(mbid):
    api = "https://musicbrainz.org/ws/2/artist/5b6ebfe0-f72b-4902-bba9-74c8af0f1af0?fmt=json&inc=aliases"
    data = api_request_handler(api)
    columns_data =  {"isni":data.get("isnis"[0], ""),   "sort_name":data.get("sort-name", ""),
                        "born_or_formed": data.get("life-span", "")["begin"], "died_or_disbanded": data.get("life-span", "")["end"],
                        "gender_id": data.get("gender", "")}
    insert_multiple_columns_data(Artists,columns_data)

def feed_country_lookup_restcountries():
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

# feed_artists(50)
# mb_artist_feeder("5b6ebfe0-f72b-4902-bba9-74c8af0f1af0")
# pprint(discover_artists_lastfm(969))
#feed_country_lookup_restcountries()