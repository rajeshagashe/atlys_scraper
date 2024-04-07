import json
from database.redis.connect import redis_client

def compare_dicts(dict1: dict, dict2: dict) -> bool:
    if set(dict1.keys()) != set(dict2.keys()):
        return False
    
    for key in dict1:
        if dict1[key] != dict2[key]:
            return False
    
    return True

async def fetch_cache(key: str) -> str:
    data = redis_client.get(key)
    return json.loads(json.loads(data)) if data else {}

async def upsert_cache(key: str, data: dict[str, any]) -> None:
    serialized_data = json.dumps(data)
    redis_client.set(key, json.dumps(serialized_data))