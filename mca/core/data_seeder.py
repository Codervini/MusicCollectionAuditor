import requests
from dotenv import dotenv_values
from pathlib import Path
from pprint import pprint
from mca.core.db_butler import ( insert_multiple_columns_data , fetch_id_by_value , get_all_values_of_a_column_in_tb ,
                                update_multiple_columns_data, get_all_values_of_multiple_column_in_tb) 
from schema.models.file_universe import *
from schema.lookup.file_universe_lookup import *
from mca.core.logger import set_logger
from mca_tools.utils import api_request_handler, coerce_to_date
import csv
from datetime import date
import time
import json
import ast
from mca_tools.cacher.api_cacher import *
import mca_tools.cacher.parsed_cacher as pc
from mca_tools.seeder_audit.audit_flusher import *
from mca_tools.seeder_audit.audit_writer import *
from mca_tools.seeder_audit.orphan_scanner import *
import inspect
CONFIG_CONSTANTS = dotenv_values(Path("config",".env"))
mb_header = {"User-Agent": f"{CONFIG_CONSTANTS["APP_NAME"]}/{CONFIG_CONSTANTS["VERSION"]} ( {CONFIG_CONSTANTS["CONTACT_EMAIL"]} )"}
logger = set_logger(__name__)
lastfm_api_key = CONFIG_CONSTANTS["LASTFM_API_KEY"]
lastfm_session = get_session("lastfm",60)
musicbrainz_session = get_session("musicbrainz",60)

def discover_artists_lastfm(artist_discovery_limit:int = 50) -> dict:
    artist_and_mbid = {}
    api = f"http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&api_key={lastfm_api_key}&format=json&limit={artist_discovery_limit}"
    data = api_request_handler(api,lastfm_session)
    for i in data["artists"]["artist"]:
        name = i.get("name","")
        artist_and_mbid[name] = i.get("mbid","")
    logger.info(f"Discovered {len(data)} artists")
    return artist_and_mbid

def discover_similar_artists_lastfm(artist,mbid = "",limit:int = 50):
    api = f"http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist=cher&api_key={lastfm_api_key}&format=json&limit={limit}&artist={artist}&mbid={mbid}"
    response = api_request_handler(api,lastfm_session)
    data = {}
    with open(file=Path("data","log",f"sussy similar artist seed {date.today()}.csv"), mode="a") as f:
        writer = csv.writer(f)
        for i in response["similarartists"]["artist"]:
            if i.get("name").find(" & ") == -1: 
                data[i.get("name")] = [i.get("mbid", ""),i.get("match","")]
            else:
                writer.writerow([i.get("name"),i.get("mbid", ""),i.get("match","")])
    logger.info(f"Discovered {len(data)} similar artists for {artist}")    
    return data
    


# def seed_artist_name_and_mbid(artist_limit, similar_artist_limit):
#     artist_list1 = discover_artists_lastfm(limit=artist_limit)
#     with open(Path("data","crucialdata",f"artists_tb {date.today()}.csv"),"a") as f:
#         writer = csv.writer(f)
#         for name,mbid in artist_list1.items():
#             writer.writerow([name,mbid])    #Save to CSV
#             insert_multiple_columns_data(Artists,{"name":name,"mbid":mbid})
#             artist_list_2 = discover_similar_artists_lastfm(name,mbid,similar_artist_limit)
#             for name,v in artist_list_2.items():
#                 writer.writerow([name,v[0]]) #Save to CSV
#                 insert_multiple_columns_data(Artists,{"name":name,"mbid":v[0]})
            
# def seed_artist_props_musicbrainz(cache = True):
#     mbids = get_all_values_of_a_column_in_tb(Artists,"mbid","created_at")
#     header = {"User-Agent": f"{CONFIG_CONSTANTS["APP_NAME"]}/{CONFIG_CONSTANTS["VERSION"]} ( {CONFIG_CONSTANTS["CONTACT_EMAIL"]} )"}
#     cached_data = {}
#     data_counter = 0
#     if cache and Path("data","crucialdata",f"artists_props_tb.csv").exists():
#         with open(Path("data","crucialdata",f"artists_props_tb.csv"),"r", newline='') as f:
#             reader = csv.reader(f)
#             rl = list(reader)
#             cached_data = {item[0]:item[1:] for item in rl if item}
#             # pprint(cached_data)
#             # pprint(len(cached_data))
#             # for i in rl: print(i[0])
#         # time.sleep(5)
#     with open(Path("data","crucialdata",f"artists_props_tb.csv"),"a") as f:
#         writer = csv.writer(f)
#         for i in mbids:
#             print(data_counter, " Now: ", i)
#             try:
#                 if cached_data and i in cached_data.keys():
#                     columns_data =  {   "isni": cached_data[i][0],
#                                         "sort_name":cached_data[i][1],
#                                         "born_or_formed": cached_data[i][2],
#                                         "died_or_disbanded": cached_data[i][3],
#                                         "gender_id": cached_data[i][4],
#                                         "country_id": cached_data[i][5],
#                                         "disambiguation": cached_data[i][6],
#                                         "raw_mb_response": cached_data[i][7]}
#                     logger.debug("Updated from cache: %s",i)
#                     print("Updated from cache: ",i)
#                 else: 
#                     api = f"https://musicbrainz.org/ws/2/artist/{i}?fmt=json&inc=aliases"
#                     data = api_request_handler(api, header)
#                     if data != None:
#                         life_span = data.get("life-span", {})
#                         columns_data =  {   "mbid": i, "isni": (data["isnis"][0] if len(data["isnis"]) > 0 else ""),
#                                             "sort_name":data.get("sort-name", ""),
#                                             "born_or_formed": coerce_to_date(life_span.get("begin", None)),
#                                             "died_or_disbanded": coerce_to_date(life_span.get("end", None)),
#                                             "gender_id": fetch_id_by_value(GenderLookup,"name", data.get("gender", "Unknown")),
#                                             "country_id": fetch_id_by_value(CountryLookup, "alpha2", data.get("country", "Unknown")),
#                                             "disambiguation": data.get("disambiguation", ""),
#                                             "raw_mb_response": data}
#                         writer.writerow(columns_data.values())
#                         columns_data.pop("mbid")
#                         time.sleep(1)
#                     else:
#                         # writer.writerow([])
#                         logger.warning("No results from MB for: %s",i)
#                         print("No results from MB for: ",i)
#                 if columns_data:
#                     update_multiple_columns_data(Artists,"mbid",i,columns_data)                
#                 columns_data = None
#             except Exception as e:
#                     logger.critical("Failed for mbid %s: %s", i, e, exc_info=True)
#             data_counter += 1
#     logger.info("%d artist properties inserted succesfully",len(mbids))
    
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

def seed_artists_link():
    ids = get_all_values_of_a_column_in_tb(Artists,"id","created_at")



class SeedArtistsFamily:
    def __init__(self):
        self.artist_and_mbid = {}
        self._init_data()
        # self.id_tb_data = get_all_values_of_multiple_column_in_tb(Artists,["id","name","mbid"],"created_at")
        self.session = SESSION_MANAGER()

    def _init_data(self):
        self.id_tb_data = get_all_values_of_multiple_column_in_tb(Artists,["id","name","mbid"],"created_at")
    def _validate_artists_data_completion(self,id):
        data = get_all_values_of_multiple_column_in_tb(Artists,[ 'name', 'sort_name', 'type_id', 
                                                                'gender_id', 'mbid', 'isni', 'country_id', 'born_or_formed', 
                                                                'died_or_disbanded', 'disambiguation', 'raw_mb_response']
                                                                )
        for i in data:
            if not data[i]:
                return False
        return True 

    def seed_artists(self,artist_discovery_limit:int=50, similar_artist_discovery_limit:int=969):
        auditor = AuditWriter(self.session,seeder_name=inspect.currentframe().f_code.co_name)
        artist_and_mbid = discover_artists_lastfm(artist_discovery_limit)
        for name,mbid in artist_and_mbid.items():
            self.artist_and_mbid[mbid] = name
            pc.set("lastfm",mbid,{"name":name})
            inserted  = insert_multiple_columns_data(Artists,{"name":name,"mbid":mbid})
            if inserted:
                auditor.record(Artists.__tablename__,mbid,status="inserted")
            else:
                auditor.record(Artists.__tablename__,mbid,status="failed")

            similar_artists = discover_similar_artists_lastfm(name,mbid,similar_artist_discovery_limit)
            for name,v in similar_artists.items():
                print(name,"================",v)
                pc.set("lastfm",v[0],{"name":name})
                self.artist_and_mbid[v[0]] = name
                inserted  = insert_multiple_columns_data(Artists,{"name":name,"mbid":v[0]})
                if inserted:
                    auditor.record(Artists.__tablename__,v[0],status="inserted")
                else:
                    auditor.record(Artists.__tablename__,v[0],status="failed")
        auditor.finish()
    def seed_artist_props_musicbrainz(self):      
        auditor = AuditWriter(self.session,seeder_name=inspect.currentframe().f_code.co_name)
        data_counter = 0
        for id, name, mbid in self.id_tb_data:
            print(data_counter, " Now: ", mbid)
            try:
                parsed  = pc.get("musicbrainz",mbid)
                if parsed:
                    columns_data =  {   "isni": parsed["isni"],
                                        "sort_name":parsed["sort_name"],
                                        "type_id":parsed["type_id"],
                                        "born_or_formed": parsed["born_or_formed"],
                                        "died_or_disbanded": parsed["died_or_disbanded"],
                                        "gender_id": parsed["gender_id"],
                                        "country_id": parsed["country_id"],
                                        "disambiguation": parsed["disambiguation"],
                                        "raw_mb_response": parsed["raw_mb_response"]}
                    logger.debug("Fetched from cache: %s",mbid)
                    print("Fetched from cache: ",mbid)
                else: 
                    api = f"https://musicbrainz.org/ws/2/artist/{mbid}?fmt=json&inc=aliases+url-rels+tags+genres+annotation+ratings"
                    data = api_request_handler(api, musicbrainz_session, mb_header)
                    if data:
                        life_span = data.get("life-span", {})
                        columns_data =  {   "isni": (data["isnis"][0] if len(data["isnis"]) > 0 else ""),
                                            "sort_name":data.get("sort-name", ""),
                                            "type_id":fetch_id_by_value(ArtistTypeLookup,"alt_type_id",data.get("type-id")),
                                            "born_or_formed": coerce_to_date(life_span.get("begin", None)),
                                            "died_or_disbanded": coerce_to_date(life_span.get("end", None)),
                                            "gender_id": fetch_id_by_value(GenderLookup,"name", data.get("gender", "Unknown")),
                                            "country_id": fetch_id_by_value(CountryLookup, "alpha2", data.get("country", "Unknown")),
                                            "disambiguation": data.get("disambiguation", ""),
                                            "raw_mb_response": data
                                        }
                        pc.set("musicbrainz",mbid,columns_data)
                        time.sleep(1)
                    else:
                        logger.warning("No results from MB for: %s",mbid)
                        print("No results from MB for: ",mbid)
                if columns_data:
                    columns_data["data_complete"] = True
                    for i in columns_data:
                        if not columns_data[i]:
                            columns_data["data_complete"] = False
                            break
                    updated = update_multiple_columns_data(Artists,"mbid",mbid,columns_data) 
                    if updated:
                        auditor.record(Artists.__tablename__,str(id),status="inserted")
                    else:
                        auditor.record(Artists.__tablename__,str(id),status="failed")
                    logger.info(f"UPDATED Artist {name} : {mbid} props ")    
                               
                columns_data = None
            except Exception as e:
                    logger.error("Failed for mbid %s: %s", mbid, e, exc_info=True)
            data_counter += 1
        auditor.finish(True)
        logger.info("%d of %d artist properties seeded succesfully",data_counter,len(self.artist_and_mbid))

    def seed_artist_aliases(self):
        auditor = AuditWriter(self.session,seeder_name=inspect.currentframe().f_code.co_name)
        alias_count = 0
        artist_count = 0
        empty_count = 0
        success_count = 0
        for id, name, mbid in self.id_tb_data:
            parsed =  pc.get("musicbrainz",mbid)
            # pprint(parsed)
            # time.sleep(2)
            
            if parsed and len(parsed["raw_mb_response"]["aliases"]) > 0:
                aliases = parsed["raw_mb_response"]["aliases"]
                for alias in aliases:
                    data = {"artist_id":fetch_id_by_value(Artists,"mbid",mbid),
                            "alias_type_id": fetch_id_by_value(AliasTypeLookup,"name",(alias.get("type") or "Unspecified").capitalize()),
                            "name":alias.get("name","Unknown"),
                            "sort_name":alias.get("sort-name","Unknown"),
                            "locale_id": fetch_id_by_value(LocaleLookup,"code",alias.get("locale",None)),
                            "is_primary": alias.get("primary",None)
                            }
                    # pprint(alias)
                    # pprint(data)
                    inserted = insert_multiple_columns_data(ArtistAliases,data)
                    if inserted:
                        auditor.record(ArtistAliases.__tablename__,str(id),status="inserted")
                    else:
                        auditor.record(ArtistAliases.__tablename__,str(id),status="failed")
                    alias_count+=1
                    pprint(f"{alias_count}/{len(aliases)} of {name}:{id} inserted")
                    logger.info(f"{alias_count}/{len(aliases)} of {name}:{id} inserted")
                success_count +=1
                logger.info("%d aliases of %s:%s  inserted succesfully",len(aliases),name,id)
            else:
                empty_count+=1
                logger.warning(f"No aliases of {name}:{id} found")
            alias_count = 0
            artist_count+=1
        # pprint(f"{artist_count}/{len(self.id_tb_data)} completed")
        auditor.finish(True)
        logger.info("%d of %d artist's aliases inserted succesfully",success_count,artist_count)
        logger.info("%d of %d artist's aliases not found",empty_count,artist_count)
    def seed_artist_link(self):
        auditor = AuditWriter(self.session,seeder_name=inspect.currentframe().f_code.co_name)
        # self._init_data()
        for id, name, mbid in self.id_tb_data:
            parsed = pc.get("musicbrainz",mbid)
            if parsed:
                relations = parsed["raw_mb_response"]["relations"]
                links_count = 0
                for link in relations:
                    # pprint(link)
                    links_count+=1
                    if link.get("target-type",None) == "url" and link["url"].get("resource"):
                        data = {"artist_id": id,
                                "link_type_id": (fetch_id_by_value(LinkTypeLookup,"alt_type_id",link.get("type-id")) or fetch_id_by_value(LinkTypeLookup,"name",link.get("type","").title())),
                                "url": link["url"].get("resource"), 
                        }
                        # pprint(data)
                        if not data["link_type_id"]:
                            insert_multiple_columns_data(LinkTypeLookup,{"name":link.get("type","").title(),
                                                                         "base_url":"/".join(data["url"].split("/")[:3]+[""]),   
                                                                         "ingestion_source":inspect.currentframe().f_code.co_name})
                            data["link_type_id"] = fetch_id_by_value(LinkTypeLookup,"name",link.get("type","").title())
                            logger.warning(f"New URL name found '{link.get("type","").title()}' for {name}:{id} and inserting new lookup record!")
                        inserted = insert_multiple_columns_data(ArtistLinks,data)
                        print(f"{links_count}/{len(relations)} links of {name} processed")
                        if inserted:
                            auditor.record(ArtistLinks.__tablename__,str(id),status="inserted")
                        else:
                            auditor.record(ArtistLinks.__tablename__,str(id),status="failed")
                    else:
                        logger.warning(f"{link} is not a valid link object for {name}:{id}")
                else:
                    logger.info(f"Processed {len(relations)} url link objects for {name}:{id}")
            else:
                logger.warning(f"No link found for {name}:{id}")
        auditor.finish()

class SeedWorksFamily():
    def __init__(self):
        self.session = SESSION_MANAGER()
        self.artist_tb_data = get_all_values_of_multiple_column_in_tb(Artists,["id","name","mbid"],"created_at")
        self.tb_data = get_all_values_of_multiple_column_in_tb(Works,["id","mbid","title","type_id","iswc","language_id"],"created_at") 
    def _get_work_data_from_mb(self,mbid,offset,limit=100):
        api = f"https://musicbrainz.org/ws/2/work?artist={mbid}&offset={offset}&limit={limit}&fmt=json"
        return api_request_handler(api, musicbrainz_session, mb_header)
    def seed_works_mb(self):
        auditor = AuditWriter(self.session,seeder_name=inspect.currentframe().f_code.co_name) 
        try:
            for id, name, mbid in self.artist_tb_data:
                if not mbid:
                    logger.warning(f"{name}:{id} has no mbid, skipping quering for works.")
                else:
                    works = []
                    work_count = 0
                    initial_data = self._get_work_data_from_mb(mbid,0)
                    works.extend([work for work in initial_data["works"]])
                    # time.sleep(1)
                    logger.info(f"Total {initial_data["work-count"]}  Works found for Name: {name} | MBID:{mbid}, procceding to query.")
                    for offset in range(100,initial_data["work-count"],100):
                        succesive_data = self._get_work_data_from_mb(mbid,offset)
                        works.extend([work for work in succesive_data["works"]])
                        # time.sleep(1)
                    else:
                        logger.debug(f"Queried succesive data for {name} | MBID:{mbid} with total count {initial_data["work-count"]}")
                    if initial_data["work-count"] == 0:
                        logger.info(f"0 Works data found for Name: {name} | MBID:{mbid} skipping processing.")
                        continue
                    logger.info(f"{initial_data["work-count"]} Works data for Name: {name} | MBID:{mbid} found, proceeding to process.")
                    for work in works:
                        work_count +=1
                        if work.get("title"):
                            data = {"title": work.get("title"),
    #                                "type_id": fetch_id_by_value(WorkTypeLookup,"alt_type_id", work.get("type-id")),
                                    "iswc":" ".join(work.get("iswcs")),
                                    "language_id": fetch_id_by_value(ISOLanguageLookup,"iso_639_3", work.get("language")),
                                    "mbid":work.get("id"),
    #                                "disambiguation":work.get("disambiguation",None),
                                    "raw_mb_response":initial_data                            
                            }
    #                        inserted = insert_multiple_columns_data(Works,data) 
                            if False:
                                auditor.record(Works.__tablename__,str(id),status="inserted")
                            else:
                                auditor.record(Works.__tablename__,str(id),status="failed")
                        else:
                            logger.warning(f"Invalid work {work_count}/{len(works)}, skipping")  
                    else:
                        logger.info(f"Processed {work_count}/{len(works)} works of {name}:{id}")
            else:
                logger.info(f"Works table is seeded succesfully for {len(self.artist_tb_data)} artists")
        except Exception as e:
            logger.critical(f"Exception occured for {name}:{id}: {e}",exc_info=True)
        auditor.finish()

    def seed_work_credits(self):
        auditor = AuditWriter(self.session,seeder_name=inspect.currentframe().f_code.co_name) 
        try:
            for work in self.tb_data:
                if not work[1]: # work["mbid"]
                    logger.warning(f"{work["title"]}:{work["id"]} has no mbid, skipping quering for work credits.")
                else:
                    work_credit_count = 0
                    api = f"https://musicbrainz.org/ws/2/work/{work['mbid']}?inc=artist-rels&fmt=json"
                    credits =  api_request_handler(api, musicbrainz_session, mb_header)
                    if credits:
                        for credit in credits["relations"]:
                            if not credit["artist"]["id"]:
                                logger.warning(f"{credit} has no Artist MBID, skipping")
                            else:
                                data = {"work_id":work["id"],
                                        "artist_id":fetch_id_by_value(Artists,"mbid",credit["artist"]["id"]),
    #                                    "role_id":fetch_id_by_value(ArtistRolesLookup,"alt_type_id",credits["type-id"]),
                                        "credit_source_id":(fetch_id_by_value(CreditSourceLookup,"name",credits["source-credit"]) or None),
                                        "credit_source_url": api,
                                        "credit_order": None,
                                        "note": None
                                    }
                    time.sleep(1)
        except:
            pass
        auditor.finish()




            
            


# SeedArtistsFamily().seed_artists(1000,9999)       
# SeedArtistsFamily().seed_artist_props_musicbrainz()  
# SeedArtistsFamily().seed_artist_aliases()     
# SeedArtistsFamily().seed_artist_link()     

SeedWorksFamily().seed_works_mb()
SeedWorksFamily().seed_work_credits()
# seed_artist_aliases()
# seed_artist_props_musicbrainz()
# pprint(discover_artists_lastfm(969))
