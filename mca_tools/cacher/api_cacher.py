from requests_cache import CachedSession
from pathlib import Path
from mca.core.logger import set_logger
from datetime import timedelta

logger = set_logger(__name__)
services = {"musicbrainz", "lastfm", "discogs", "spotify","restcountries"}

CACHE_DIR = Path(".cache/api")

def get_session(service: str, expiry_in_days: int = 69) -> CachedSession:
    if service not in services:
        logger.error("Invalid service selected")
        raise ValueError(f"Invalid service: {service}")
    
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Cached Session for {service} created")
    return CachedSession(
        backend="sqlite",
        cache_name=str(CACHE_DIR / service),
        expire_after=timedelta(days=expiry_in_days),
        ignored_parameters=['api_key', 'client_id', 'client_secret'],
        stale_if_error=True
    )