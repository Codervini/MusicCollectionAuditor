import os
import subprocess
from pathlib import Path
import shutil
from dotenv import dotenv_values
import sys
import logging
import csv
from mutagen.flac import FLAC
from pprint import pprint
import musicbrainzngs as mb
from musicbrainzngs.musicbrainz import ResponseError
from urllib.error import HTTPError, URLError
import json
from db_manager.tools.meta_processor_db_handler import Song, db_init , drop_all_table_cascade

class MetaProcessor():
    def __init__(self):
        self.CONFIG_CONSTANTS = dotenv_values(".env")
        self.manual_review_queue = []
        # self.flac_path = {"root": "", "flac_paths":[]}
        mb.set_useragent(app=self.CONFIG_CONSTANTS["APP_NAME"], version=self.CONFIG_CONSTANTS["VERSION"], contact=self.CONFIG_CONSTANTS["CONTACT_EMAIL"])
        mb.set_rate_limit(1.0,1)

    def _fetch(self,mb_fetch_func,*args):
        try:
            pprint(mb_fetch_func(*args))
        except ResponseError as e:
            print("MusicBrainz API error:", e)
            return False
            #Has artist?
        except HTTPError as e:
            print("HTTP error:", e)
            return False
        except URLError as e:
            print("Network error:", e)
            return False
        except Exception as e:
            print("Unexpected error:", e)
            return False
        else:
            return True
        
    def _db_file_ingestion_handler(self):
        pass


    def _resolve_path(self,path: list):
        '''Returns the absoute path in the current system as a string.'''
        return str(Path(*path).absolute().resolve())

    def run_picard(self, dirs: list[str]):
        '''Launches MusicBrainz Picard with the provided directories.

        Resolves the given directory paths to absolute paths and attempts to
        locate a valid Picard executable before launching the application.

        Possible Picard sources the method can detect:
        - Executable available in the system PATH (Independent of OS)
        - macOS application bundle installation
        - Windows default installation path
        - Linux Flatpak package
        - Linux Snap package
        - Custom executable path specified in `.env` (`Picard_PATH`)

        Args:
            dirs (list[str]): List of directories containing audio files that should
            be opened in Picard.

        Returns:
            str | None: Path used to launch Picard, or None if Picard could not
            be located.
        '''
        if len(dirs) < 2:
            dirs = [str(Path(dirs).expanduser().resolve())]
        else:
            dirs = [str(Path(d).expanduser().resolve()) for d in dirs]

        picard_path = None

        if shutil.which("picard"):
            picard_path = shutil.which("picard")
            subprocess.run([picard_path] + dirs)
            return str(picard_path)
        elif sys.platform == "darwin":
            picard_path = Path("/Applications/MusicBrainz Picard.app/Contents/MacOS/picard")
            if picard_path.exists():
                subprocess.run([str(picard_path)] + dirs)
                return str(picard_path)
            else:
                logging.critical("Picard not found on Mac. If installed, provide path to picard.")
                return None

        elif sys.platform == "win32":
            picard_path = Path(r"C:\Program Files\MusicBrainz Picard\picard.exe")
            if picard_path.exists():
                subprocess.run([str(picard_path)] + dirs)
                return str(picard_path)
            else:
                logging.critical("Picard not found on Windows. If installed, provide path to picard.")
                return None

        elif sys.platform.startswith("linux"):
            if shutil.which("flatpak"):
                picard_path = shutil.which("flatpak")
                subprocess.run(["flatpak", "run", "org.musicbrainz.Picard"] + dirs)
                return str(picard_path)
            elif shutil.which("snap"):
                picard_path = shutil.which("snap")
                subprocess.run(["snap", "run", "picard"] + dirs)
                return str(picard_path)
            else:
                logging.critical("Picard not found on Linux. If installed, provide path to picard.")
                return None
        elif self.CONFIG_CONSTANTS.get("Picard_PATH"):
            picard_path = self.CONFIG_CONSTANTS["Picard_PATH"]
            subprocess.run([str(picard_path)] + dirs)
            return str(picard_path)
        else:
            logging.critical("Picard not found. If installed, provide path in env.")
            return None

    def path_finder(self, csv_file: str = None, csv_columns : list = None, root_dir : str = None, file : str = None):
        """
        Finds all FLAC file paths and determines their common root directory.

        Parameters
        ----------
        csv_file : str, optional
            Path to a CSV file containing song file paths.

        csv_columns : list[int], optional
            Column indices in the CSV that together form the full file path.

        root_dir : str, optional
            Root directory to recursively search for `.flac` files.

        file : str, optional
            Path to a single FLAC file.

        Returns
        -------
        dict
            {
                "root_path": str   # Common root directory containing the FLAC files
                "flac_paths": list[str]  # List of resolved FLAC file paths
            }

        Behavior
        --------
        - If `csv_file` is provided, file paths are built from the specified `csv_columns`
        and the common root directory is calculated.
        - If `root_dir` is provided, all `.flac` files are recursively discovered.
        - If `file` is provided, the file path is returned with its parent directory as root_path.
        """
        all_flac_path_info = {"root_path": "", "flac_paths":[]}
        if csv_file and csv_columns: #CSV
            with open(self._resolve_path([csv_file]),"r") as f:
                reader = csv.reader(f)
                next(reader,None)
                for i in reader:
                    path = []
                    try:
                        for column in csv_columns:
                            path.append(i[column])
                    except IndexError:
                        print("Invalid path")
                        continue
                    resolved_path = self._resolve_path(path)
                    all_flac_path_info["flac_paths"].append(resolved_path)
            if all_flac_path_info["flac_paths"]:
                all_flac_path_info['root_path'] = os.path.commonpath(all_flac_path_info["flac_paths"])
            else:
                print("No song path available, check CSV file for the cause.")
            return all_flac_path_info
        elif root_dir: #Given Root directory
            all_flac_path_info['root_path'] = self._resolve_path(root_dir)
            all_flac_path_info["flac_paths"] = [str(f) for f in Path(all_flac_path_info['root_path']).rglob("*.flac") if f.is_file()]
            return all_flac_path_info
        elif file: #Given a file
            all_flac_path_info['root_path'] = str(Path(self._resolve_path(file)).parent)
            all_flac_path_info["flac_paths"] = [self._resolve_path(file)]
            return all_flac_path_info

    def read_metadata(self, dirs: list[str]):
        # List of song metadata dict's  [{"FilePath":{"Vorbis":{}, "Technical":{}, "Picture":[{}]}}]
        """
            Read metadata from a list of FLAC audio files.

            For each file path provided, the function extracts three categories
            of metadata using the mutagen FLAC parser:

            1. Vorbis comments (standard FLAC tags such as artist, album, title, etc.)
            2. Stream information (technical audio properties like sample rate,
            bitrate, channels, and duration)
            3. Embedded picture metadata (cover artwork properties)

            Parameters
            ----------
            dirs : list[str]
                A list of file paths pointing to FLAC audio files.

            Returns
            -------
            list[dict]
                A list where each element represents one audio file and contains:

                {
                    "FilePath": str,          # Path to the FLAC file
                    "Vorbis": dict,           # Vorbis tag metadata
                    "Streaminfo": dict,       # Technical stream properties
                    "Pictures": list[dict]    # Embedded artwork metadata
                }

            Notes
            -----
            Only metadata blocks are read. The audio stream itself is not decoded,
            making the function efficient for scanning large music libraries.
        """
        all_audio_metatdata  = []
        for file in dirs:
            audio = {file: {"Vorbis":{}, "Streaminfo": {}, "Pictures": []}} #Dict of all metadata of a song:  {Vorbis{}, Technical{}, Picture[{}]}
            song = FLAC(file)
            audio[file]["Vorbis"] = song.tags.as_dict() if song.tags else {}
            audio[file]["Streaminfo"] = vars(song.info)
            audio[file]["Pictures"] = [
                                    {
                                        "type": pic.type,
                                        "mime": pic.mime,
                                        "description": pic.desc,
                                        "width": pic.width,
                                        "height": pic.height,
                                        "depth": pic.depth,
                                        "colors": pic.colors,
                                        "size_bytes": len(pic.data)
                                    }
                                    for pic in song.pictures
                                ]
            all_audio_metatdata.append(audio)
        return all_audio_metatdata

    def fetch_info_by_track_id(self,track_id : str):
        return self._fetch(mb.get_recording_by_id,track_id)

    def fetch_info_by_album_id(self,release_id : str):
        return self._fetch(mb.get_release_by_id,release_id)
    
    def metaFixer_redundant(self):

        while True:

            choice = int(input('''Select the type of the source of music
        1) Enter the absoulte path
        2) Fetch path from Song List CSV
        3) Recursively find the dir's from an absolute path
        9) To exit
        Your choice: ''').strip())

            song_dir_path = []

            if choice == 9:
                break
            elif choice not in [1,2,3]:
                print("Wrong Choice")

            match choice:
                case 1:
                    song_dir_path.append(str(Path(input("Enter path: ").strip()).expanduser().resolve()))
                case 2:
                    with open(Path("data", "output","All Songs list.csv"), "r") as f:
                        reader = csv.reader(f,skipinitialspace=True)
                        next(reader)

                        for i in reader:
                            if i[0] not in song_dir_path:
                                song_dir_path.append(i[0])

                        print(f"Found {len(song_dir_path)} directories")

                        self.PicardRunner(song_dir_path)


                case 3:
                    pass

    def metaFixer(self, song_metadata: dict):
        musicbrainz_ids_lookup = ('musicbrainz_albumartistid',
                            'musicbrainz_albumid',
                            'musicbrainz_artistid',
                            'musicbrainz_releasegroupid',
                            'musicbrainz_releasetrackid',
                            'musicbrainz_trackid')
                                                                                                                                    # {'FilePath': "",          'Pictures': [{}],         'Streaminfo': {},        'Vorbis': {"key": ['value']}}
        # print(json.dumps(song_metadata, indent=4))  # {"FilePath":{"Vorbis":{}, "Technical":{}, "Picture":[{}] }} 

        #------------READ FILE
        file = list(song_metadata.keys())[0]
        song_metadata = song_metadata[file]
        song_musicbrainz_ids = { id_name : value[0] for id_name, value in song_metadata["Vorbis"].items() if id_name in musicbrainz_ids_lookup and value}
        song_vorbis = {k : ", ".join(v) for k,v in song_metadata["Vorbis"].items() if k not in musicbrainz_ids_lookup and v}
        # pprint(song_vorbis)

        #---------Has MBID? 
        track_mbid_valid = None
        album_mbid_valid = None
        if 'musicbrainz_trackid'in song_musicbrainz_ids:
            track_mbid_valid = self.fetch_info_by_track_id(song_musicbrainz_ids.get("musicbrainz_trackid"))
        if 'musicbrainz_albumid'in song_musicbrainz_ids:
            album_mbid_valid=self.fetch_info_by_album_id(song_musicbrainz_ids.get("musicbrainz_albumid"))

        # drop_all_table_cascade()
        # db_init()

        song = Song(file,
            source_title = song_vorbis.get("title", None),
            source_artist= song_vorbis.get("artist", None),
            source_album_mbid= song_musicbrainz_ids.get("musicbrainz_albumid",None),
            source_track_mbid= song_musicbrainz_ids.get("musicbrainz_trackid", None),
            track_mbid_valid = track_mbid_valid,
            album_mbid_valid= album_mbid_valid)


        

mp = MetaProcessor()
all_paths_info = mp.path_finder(csv_file="data/output/All Songs list.csv", csv_columns=[0,1])
metadata_info = mp.read_metadata(all_paths_info["flac_paths"])[70]
# pprint(paths)
# print(MetaProcessor().read_metadata(paths)[2]["FilePath"])
# pprint(metadata_info,width=200, sort_dicts=False, compact=False)
# print(json.dumps(metadata_info, indent=4))
mp.metaFixer(metadata_info)