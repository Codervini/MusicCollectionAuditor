from uuid_extensions import uuid7, uuid7str
import requests
from mca.core.logger import set_logger
logger = set_logger(__name__)


def generate_uuidv7():
    return uuid7()

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