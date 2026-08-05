import diskcache as dc

cache = dc.Cache(".cache/parsed")

def get(service: str, key: str) -> dict | None:
    return cache.get(f"{service}:{key}")

def set(service: str, key: str, data: dict) -> None:
    cache.set(f"{service}:{key}", data)

def invalidate(service: str, key: str) -> None:
    cache.delete(f"{service}:{key}")