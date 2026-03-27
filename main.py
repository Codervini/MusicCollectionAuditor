import csv
from pathlib import Path
from dotenv import dotenv_values
import logging
import datetime
import re
from app_tools.QualityChecker import QualityChecker

if not Path("data").exists():
    Path("data").mkdir()
if not Path("data","log").exists():
    Path("data","log").mkdir()
if not Path("data","output").exists():
    Path("data","output").mkdir()
if not Path("data","stage").exists():
    Path("data","stage").mkdir()
LOG_FILE=str(Path("data","log",f"{str(datetime.date.today())}.log"))

    

logging.basicConfig(level=logging.DEBUG, filename=LOG_FILE,filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")



if Path(".env").exists():
    CONFIG_CONSTANTS = dotenv_values(".env")
    logging.info("Environment variables initialised")
else:
    logging.info(".env file not found")



def main():
    # STAGING_DIR = input("Enter the absolute staging directory path: ")
    # OUTPUT_DIR = input("Enter the absolute ouput directory path: ")
    if CONFIG_CONSTANTS["FLAC_LOG_REPORT_FILE"]:
        FLAC_TEST_REPORT = CONFIG_CONSTANTS["FLAC_LOG_REPORT_FILE"]
    else:
        FLAC_TEST_REPORT = input("Enter the FLAC-authenticity CSV report absolute path: ")
    logging.info("Entered Main.")


    while True:
        # mode = input("""Enter "i" for interactive mode or "m" for manual mode "e" for exit: """).strip()
        mode = "i"
        if (mode == "i"):
            logging.info("Entered interactive mode.")
            QualityChecker(FLAC_TEST_REPORT,CONFIG_CONSTANTS)
            break
        elif mode == "m":
            pass
        elif mode == "e":
            print("Goodbye.")
            break
        else:
            print("Invalid option")



    


main()