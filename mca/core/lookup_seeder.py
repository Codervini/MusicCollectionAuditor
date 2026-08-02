from dotenv import dotenv_values
from pathlib import Path
from pprint import pprint
from mca.core.db_butler import insert_multiple_columns_data , fetch_id_by_value
# from schema.models.file_universe import Artists
from schema.lookup.file_universe_lookup import *
from mca.core.logger import set_logger
from mca_tools.utils import api_request_handler
import csv
from babel.localedata import locale_identifiers
from babel.core import Locale, UnknownLocaleError


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

def seed_alias_types_lookup():
    alias_types = [
    ("Artist Name",       "An alternative name the artist performs or is known under"),
    ("Legal Name",        "The official birth or legal name, e.g. Stefani Germanotta → Lady Gaga"),
    ("Search Hint",       "A misspelling or common variation to aid search, e.g. Led Zepplin"),
    ("Stage Name",        "A performance name adopted for public use, distinct from legal name"),
    ("Nickname",          "An informal name given by fans, peers or media, e.g. The Boss, The King"),
    ("Alter Ego",         "A distinct persona adopted for a specific creative project, e.g. Ziggy Stardust"),
    ("Abbreviation",      "A shortened form of the artist name, e.g. JT for Justin Timberlake"),
    ("Transliteration",   "A phonetic rendering into another script, e.g. Чайковский → Tchaikovsky"),
    ("Translation",       "A meaning-based rendering into another language"),
    ("Contractual Alias", "A name used to bypass label or contractual restrictions"),
    ("Collaboration Name","A name used specifically for a joint project or group effort"),
    ("Birth Name",        "The name given at birth, before any legal or stage name change"),
    ("Collective Name",   "A shared name used by a group or rotating set of artists as one identity"),
    ("Unspecified",       "Alias type not yet determined — assign a specific type after research"),
    ]
    for i in alias_types:
            insert_multiple_columns_data(AliasTypeLookup,{"name":i[0],"description":i[1]})
    logger.info("Alias Type Lookup Seeded")


def seed_locale_lookup():
    rtl_scripts = {"Arab", "Hebr", "Thaa", "Tfng", "Syrc", "Nkoo", "Adlm"}
    for locale_str in locale_identifiers():
        try:
            loc = Locale.parse(locale_str, sep="_")
            script  = str(loc.script)    if loc.script    else None
            region  = str(loc.territory) if loc.territory else None
            insert_multiple_columns_data(LocaleLookup,{
                "code":          locale_str,
                "language_code": str(loc.language),
                "region_code":   region,
                "script_code":   script,
                "display_name":  loc.get_display_name("en"),
                "is_rtl":        script in rtl_scripts if script else False,
            })
        except UnknownLocaleError:
            continue
    logger.info("Locale Lookup Seeded")

def seed_link_types_lookup():
    link_types = [

    # Official
    ("Official Homepage","https://","Artist's official website"),
    ("Official Store","https://","Official merch or music store"),

    # Social Networks
    ("Facebook","https://www.facebook.com/","Facebook page or profile"),
    ("Instagram","https://www.instagram.com/","Instagram profile"),
    ("Twitter","https://twitter.com/","Twitter/X profile"),
    ("TikTok","https://www.tiktok.com/@","TikTok profile"),
    ("Myspace","https://myspace.com/","Myspace page"),
    ("SoundCloud","https://soundcloud.com/","SoundCloud profile"),
    ("Snapchat","https://www.snapchat.com/add/","Snapchat profile"),
    ("Threads","https://www.threads.net/@","Threads profile"),
    ("Bluesky","https://bsky.app/profile/","Bluesky profile"),
    ("Mastodon","https://","Mastodon profile"),
    ("Tumblr","https://","Tumblr blog"),

    # Video
    ("YouTube","https://www.youtube.com/","Official YouTube channel"),
    ("YouTube Music","https://music.youtube.com/","YouTube Music channel"),
    ("Vimeo","https://vimeo.com/","Vimeo channel"),

    # Streaming
    ("Spotify","https://open.spotify.com/artist/","Spotify artist page"),
    ("Apple Music","https://music.apple.com/","Apple Music artist page"),
    ("Tidal","https://tidal.com/browse/artist/","Tidal artist page"),
    ("Deezer","https://www.deezer.com/en/artist/","Deezer artist page"),
    ("Amazon Music","https://music.amazon.com/artists/","Amazon Music artist page"),
    ("Pandora","https://www.pandora.com/artist/","Pandora artist page"),

    # Purchase / Download
    ("Bandcamp","https://","Bandcamp artist page"),
    ("CD Baby","https://store.cdbaby.com/Artist/","CD Baby artist page"),
    ("iTunes","https://music.apple.com/","iTunes artist page"),
    ("Purchase Download","https://","Page where music can be purchased for download"),
    ("Purchase Mail Order","https://","Page where music can be purchased by mail order"),
    ("Free Download","https://","Page where music can be downloaded for free"),
    ("Free Streaming","https://","Page where music can be streamed for free"),

    # Databases / Reference
    ("MusicBrainz","https://musicbrainz.org/artist/","MusicBrainz artist page"),
    ("Discogs","https://www.discogs.com/artist/","Discogs artist page"),
    ("Last.fm","https://www.last.fm/music/","Last.fm artist page"),
    ("AllMusic","https://www.allmusic.com/artist/","AllMusic artist page"),
    ("Wikidata","https://www.wikidata.org/wiki/","Wikidata entity page"),
    ("Wikipedia","https://en.wikipedia.org/wiki/","Wikipedia article"),
    ("IMDb","https://www.imdb.com/name/","IMDb page"),
    ("IMSLP","https://imslp.org/wiki/","IMSLP page for classical works"),
    ("SecondHandSongs","https://secondhandsongs.com/artist/","SecondHandSongs page"),
    ("Setlist.fm","https://www.setlist.fm/setlists/","Setlist.fm artist page"),
    ("Songkick","https://www.songkick.com/artists/","Songkick artist page"),
    ("Bandsintown","https://www.bandsintown.com/","Bandsintown artist page"),
    ("VGMdb","https://vgmdb.net/artist/","VGMdb page for video game/anime music artists"),
    ("VIAF","https://viaf.org/viaf/","Virtual International Authority File ID"),
    ("CPDL","https://www.cpdl.org/wiki/index.php/","Choral Public Domain Library page"),
    ("BookBrainz","https://bookbrainz.org/creator/","BookBrainz page"),

    # Content
    ("Lyrics Page","https://","Page containing lyrics for the artist"),
    ("Blog","https://","Artist blog"),
    ("Biography","https://","Online biography of the artist"),
    ("Discography Page","https://","Online discography of the artist's works"),
    ("Interview","https://","URL containing an interview with the artist"),
    ("Image","https://","A pictorial image of the artist"),
    ("Fan Page","https://","Fan-created website for the artist"),
    ("Online Community","https://","Online community or forum for the artist"),
    ("Art Gallery", "https://","Art gallery page e.g. DeviantArt, pixiv"),

    # Funding / Tickets
    ("Crowdfunding","https://","Crowdfunding page e.g. Kickstarter, Indiegogo"),
    ("Patronage","https://","Patronage/donation page e.g. Patreon, PayPal.me"),
    ("Ticketing","https://","Ticket purchase page for events"),

    # Fallback
    ("Other","https://","External link that does not fit any other category"),
]
    for i in link_types:
            insert_multiple_columns_data(LinkTypeLookup,{"name":i[0],"base_url":i[1],"description":i[2]})
    logger.info("Links Type Lookup Seeded")

seed_link_types_lookup()
# seed_artist_type_lookup()
# seed_alias_types_lookup()
# seed_locale_lookup()
# seed_gender_lookup()
# seed_country_lookup_restcountries()