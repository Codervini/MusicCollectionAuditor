from uuid_extensions import uuid7, uuid7str
import requests
from mca.core.logger import set_logger
from datetime import date
logger = set_logger(__name__)


def generate_uuidv7():
    return uuid7()

def api_request_handler(api, session, header=None):
    match header:
        case None:
            response = session.get(api)
        case _:
            response = session.get(api, headers=header)

    logger.debug("API response: %s", response)
    if response.status_code == 200:
        data = response.json()
        logger.debug("Response data: %s", data)
        return data

    
def coerce_to_date(value: str | None) -> date | None:
    if not value:
        return None
    value = value.strip()
    try:
        if len(value) == 10:  # full date "2019-06-15"
            return date.fromisoformat(value)
        else:  # anything else — year only, year-month, whatever
            return date(int(value[:4]), 1, 1)
    except (ValueError, TypeError):
        return None