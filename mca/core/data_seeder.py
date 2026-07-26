import requests
from dotenv import dotenv_values
from pathlib import Path
from pprint import pprint
from mca.core.db_butler import insert_multiple_columns_data , fetch_id_by_value , get_all_values_of_a_column_in_tb ,update_multiple_columns_data
from schema.models.file_universe import Artists
from schema.lookup.file_universe_lookup import *
from mca.core.logger import set_logger
from mca_tools.utils import api_request_handler, coerce_to_date
import csv
from datetime import date
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
            name =i.get("name","")
            dictt[name] = i.get("mbid","")
        return dictt

def discover_similar_artists_lastfm(artist,mbid = "",limit:int = 50):
    api = f"http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist=cher&api_key={lastfm_api_key}&format=json&limit={limit}&artist={artist}&mbid={mbid}"
    respone = requests.get(api)
    logger.debug("Artist dsa: %s", artist)
    logger.debug("API dsa response: %s", respone)
    data = {}
    if respone.status_code == 200:
        res = respone.json()
        logger.debug("Response dsa data: %s", res)
        with open(file=Path("data","log",f"sussy artist seed {date.today()}.csv"), mode="a") as f:
            writer = csv.writer(f)
            for i in res["similarartists"]["artist"]:
                if i.get("name").find(" & ") == -1: 
                    data[i.get("name")] = [i.get("mbid", ""),i.get("match","")]
                else:
                    writer.writerow([i.get("name"),i.get("mbid", ""),i.get("match","")])
        return data
    


def seed_artist_name_and_mbid(artist_limit, similar_artist_limit):
    artist_list1 = discover_artists_lastfm(limit=artist_limit)
    with open(Path("data","crucialdata",f"artists_tb {date.today()}.csv"),"a") as f:
        writer = csv.writer(f)
        for name,mbid in artist_list1.items():
            writer.writerow([name,mbid])    #Save to CSV
            insert_multiple_columns_data(Artists,{"name":name,"mbid":mbid})
            artist_list_2 = discover_similar_artists_lastfm(name,mbid,similar_artist_limit)
            for name,v in artist_list_2.items():
                writer.writerow([name,v[0]]) #Save to CSV
                insert_multiple_columns_data(Artists,{"name":name,"mbid":v[0]})
            
def seed_artist_props_musicbrainz():
    mbids = get_all_values_of_a_column_in_tb(Artists,"mbid")
    header = {"User-Agent": f"{CONFIG_CONSTANTS["APP_NAME"]}/{CONFIG_CONSTANTS["VERSION"]} ( {CONFIG_CONSTANTS["CONTACT_EMAIL"]} )"}
    try: 
        with open(Path("data","crucialdata",f"artists_props_tb {date.today()}.csv"),"a") as f:
            writer = csv.writer(f)
            for i in mbids:
                api = f"https://musicbrainz.org/ws/2/artist/{i}?fmt=json&inc=aliases"
                data = api_request_handler(api, header)
                # pprint(data)
                if data != None:
                    columns_data =  {"isni": (data["isnis"][0] if len(data["isnis"]) > 0 else ""),
                                        "sort_name":data.get("sort-name", ""),
                                        "born_or_formed": coerce_to_date(data["life-span"]["begin"]),
                                        "died_or_disbanded": coerce_to_date(data["life-span"].get("end", None)),
                                        "gender_id": fetch_id_by_value(GenderLookup,"name", data.get("gender", "Unknown")),
                                        "country_id": fetch_id_by_value(CountryLookup, "alpha2", data.get("country", "Unknown")),
                                        "disambiguation": data.get("disambiguation", ""),
                                        "raw_mb_response": data}
                    writer.writerow(columns_data.items())
                    update_multiple_columns_data(Artists,"mbid",i,columns_data)
                else:
                    logger.warning("No results from MB for %s",i)
        logger.info("%d artist properties inserted succesfully",len(mbids))
    except Exception as e:
        logger.critical("Something went wrong!: %d",e)



seed_artist_props_musicbrainz()
# pprint(discover_artists_lastfm(969))
