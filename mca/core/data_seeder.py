import requests
from dotenv import dotenv_values
from pathlib import Path
from pprint import pprint
from mca.core.db_butler import insert_multiple_columns_data
from schema.models.file_universe import Artists
from schema.lookup.file_universe_lookup import *
from mca.core.logger import set_logger
CONFIG_CONSTANTS = dotenv_values(Path("config",".env"))
logger = set_logger(__name__)
lastfm_api_key = CONFIG_CONSTANTS["LASTFM_API_KEY"]

def discover_artists_lastfm(limit:int = 50):
    response = requests.get(f"http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&api_key={lastfm_api_key}&format=json&limit={limit}")
    logger.debug("API response: %s", response)
    dictt = {}
    if response.status_code == 200:
        data = response.json()
        logger.debug("Response data: %s", data)
        for i in data["artists"]["artist"]:
            # pprint(f"{i.get("name",None)} + {i.get("mbid",None)}")
            name =i.get("name",None)
            dictt[name] = i.get("mbid",None)
        return dictt

def discover_similar_artists_lastfm(artist,mbid = None,limit:int = 50):
    api = f"http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist=cher&api_key={lastfm_api_key}&format=json&limit={limit}&artist={artist}&mbid={mbid}"
    respone = requests.get(api)
    pprint(respone)
    logger.debug("API response: %s", respone)
    data = {}
    if respone.status_code == 200:
        res = respone.json()
        pprint(res)
        logger.debug("Response data: %s", res)
        for i in res["similarartists"]["artist"]:
            data[i.get("name")] = [i.get("mbid", None),i.get("match",None)]
        return data
    


def feed_artists(limit):
    artist_list1 = discover_artists_lastfm(limit=969)
    # pprint(artist_list1)
    for name,mbid in artist_list1.items():
        insert_multiple_columns_data(Artists,{"name":name,"mbid":mbid},["mbid"])
        artist_list_2 = discover_similar_artists_lastfm(name,mbid,limit)
        for name,v in artist_list_2.items():
            insert_multiple_columns_data(Artists,{"name":name,"mbid":v[0]},["mbid"])
            
        

        
feed_artists(50)

pprint(discover_artists_lastfm(969))