import requests
from dotenv import dotenv_values
from pathlib import Path
from pprint import pprint
from mca.core.db_butler import insert_multiple_columns_data , fetch_id_by_value , get_all_values_of_a_column_in_tb ,update_multiple_columns_data
from schema.models.file_universe import *
from schema.lookup.file_universe_lookup import *
from mca.core.logger import set_logger
from mca_tools.utils import api_request_handler, coerce_to_date
import csv
from datetime import date
import time
import json
import ast
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
            
def seed_artist_props_musicbrainz(cache = True):
    mbids = get_all_values_of_a_column_in_tb(Artists,"mbid","created_at")
    header = {"User-Agent": f"{CONFIG_CONSTANTS["APP_NAME"]}/{CONFIG_CONSTANTS["VERSION"]} ( {CONFIG_CONSTANTS["CONTACT_EMAIL"]} )"}
    cached_data = {}
    data_counter = 0
    if cache and Path("data","crucialdata",f"artists_props_tb.csv").exists():
        with open(Path("data","crucialdata",f"artists_props_tb.csv"),"r", newline='') as f:
            reader = csv.reader(f)
            rl = list(reader)
            cached_data = {item[0]:item[1:] for item in rl if item}
            # pprint(cached_data)
            # pprint(len(cached_data))
            # for i in rl: print(i[0])
        # time.sleep(5)
    with open(Path("data","crucialdata",f"artists_props_tb.csv"),"a") as f:
        writer = csv.writer(f)
        for i in mbids:
            print(data_counter, " Now: ", i)
            try:
                if cached_data and i in cached_data.keys():
                    columns_data =  {   "isni": cached_data[i][0],
                                        "sort_name":cached_data[i][1],
                                        "born_or_formed": cached_data[i][2],
                                        "died_or_disbanded": cached_data[i][3],
                                        "gender_id": cached_data[i][4],
                                        "country_id": cached_data[i][5],
                                        "disambiguation": cached_data[i][6],
                                        "raw_mb_response": cached_data[i][7]}
                    logger.debug("Updated from cache: %s",i)
                    print("Updated from cache: ",i)
                else: 
                    api = f"https://musicbrainz.org/ws/2/artist/{i}?fmt=json&inc=aliases"
                    data = api_request_handler(api, header)
                    if data != None:
                        life_span = data.get("life-span", {})
                        columns_data =  {   "mbid": i, "isni": (data["isnis"][0] if len(data["isnis"]) > 0 else ""),
                                            "sort_name":data.get("sort-name", ""),
                                            "born_or_formed": coerce_to_date(life_span.get("begin", None)),
                                            "died_or_disbanded": coerce_to_date(life_span.get("end", None)),
                                            "gender_id": fetch_id_by_value(GenderLookup,"name", data.get("gender", "Unknown")),
                                            "country_id": fetch_id_by_value(CountryLookup, "alpha2", data.get("country", "Unknown")),
                                            "disambiguation": data.get("disambiguation", ""),
                                            "raw_mb_response": data}
                        writer.writerow(columns_data.values())
                        columns_data.pop("mbid")
                        time.sleep(1)
                    else:
                        # writer.writerow([])
                        logger.warning("No results from MB for: %s",i)
                        print("No results from MB for: ",i)
                if columns_data:
                    update_multiple_columns_data(Artists,"mbid",i,columns_data)                
                columns_data = None
            except Exception as e:
                    logger.critical("Failed for mbid %s: %s", i, e, exc_info=True)
            data_counter += 1
    logger.info("%d artist properties inserted succesfully",len(mbids))
    
def seed_artist_aliases():
    ids = get_all_values_of_a_column_in_tb(Artists,"id","created_at")
    alias_count = 0
    artist_count = 0
    with open(Path("data","crucialdata",f"artists_props_tb.csv"),"r") as f:
        reader = csv.reader(f)
        id_aliases_data = {i[0]:ast.literal_eval(i[-1]).get("aliases",[]) for i in list(reader)}

    for artist, aliases in id_aliases_data.items():
        if len(aliases) > 0:
            for alias in aliases:
                data = {"artist_id":fetch_id_by_value(Artists,"mbid",artist),
                        "alias_type_id": fetch_id_by_value(AliasTypeLookup,"name",alias.get("type","Unspecified")),
                        "name":alias.get("name","Unknown"),
                        "sort_name":alias.get("sort-name","Unknown"),
                        "locale_id": fetch_id_by_value(LocaleLookup,"code",alias.get("locale",None)),
                        "is_primary": alias.get("primary",None)
                        }
                # pprint(alias)
                # pprint(data)
                insert_multiple_columns_data(ArtistAliases,data)
                alias_count+=1
                pprint(f"{alias_count}/{len(aliases)} of {artist} inserted")
            logger.info("%d %s aliases inserted succesfully",len(alias),artist)
            alias_count = 0
                # time.sleep(2)
        artist_count+=1
        pprint(f"{artist_count}/{len(id_aliases_data)} completed")
    logger.info("%d artist aliases inserted succesfully",len(id_aliases_data))

# seed_artist_aliases()
# seed_artist_props_musicbrainz()
# pprint(discover_artists_lastfm(969))
