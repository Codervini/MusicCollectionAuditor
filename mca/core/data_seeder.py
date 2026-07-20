import requests
from dotenv import dotenv_values
from pathlib import Path
from pprint import pprint
CONFIG_CONSTANTS = dotenv_values(Path("config",".env"))

lastfm_api_key = CONFIG_CONSTANTS["LASTFM_API_KEY"]

def discover_artists_lastfm(limit:int = 50):
    response = requests.get(f"http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&api_key={lastfm_api_key}&format=json&limit={limit}")
    dictt = {}
    if response.status_code == 200:
        data = response.json()
        for i in data["artists"]["artist"]:
            # pprint(f"{i.get("name",None)} + {i.get("mbid",None)}")
            dictt[i.get("name",None)] = i.get("mbid",None)
    return dictt

def discover_similar_artists_lastfm(artist,mbid = None,limit:int = 50):
    api = f"http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist=cher&api_key={lastfm_api_key}&format=json&limit={limit}&artist={artist}&mbid={mbid}"
    respone = requests.get(api)
    data = {}
    if respone.status_code == 200:
        res = respone.json()
        for i in res["similarartists"]["artist"]:
            data[i.get("name")] = [i.get("mbid", None),i.get("match",None)]
    return data



pprint(discover_artists_lastfm(969))