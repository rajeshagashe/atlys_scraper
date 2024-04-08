import json
import httpx
import asyncio

from typing import Union
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

async def fetch_get_response(url: str, proxy: Union[str, None] = None, retry_options: dict[str, any] = {}) -> httpx.Response:
        status_code = 500
        retries = retry_options.get('count', 1)
        delay = retry_options.get('interval', 1)
        
        proxy_options = {"https://": proxy} if proxy else None

        # httpx does not provide ready-made retry options so doing a simple implementation
        async with httpx.AsyncClient(proxies=proxy_options) as client:
            while status_code in [i for i in range(500, 600)]:
                if retries < retry_options.get('count', 1): # not delaying for 1st attempt
                    await asyncio.sleep(delay)
                response = await client.get(url)
                status_code = response.status_code
                retries -= 1
                if retries == 0:
                    break

            return response