from requests_cache import CachedSession
from pathlib import Path
from mca.core.logger import set_logger
from dotenv import dotenv_values
from datetime import timedelta

logger = set_logger(__name__)


CACHE_DIR = Path(".cache/api")

def get_session(service: str, ttl_days: int = 7) -> CachedSession:
    services = ["musicbrainz", "last.fm"]
    if service not in services:
        print("Invalid service")
        logger.error("Invalid service selected")
        return
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Cached Session returned")
    return CachedSession(
        cache_name=str(CACHE_DIR / service),
        expire_after=timedelta(days=ttl_days),
        ignored_parameters=['api_key', 'client_id', 'client_secret'],
        stale_if_error=True,
    )