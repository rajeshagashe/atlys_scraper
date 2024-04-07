import aioredis
import os

redis = None
async def connect_redis():
    global redis
    connection_string = os.environ.get('REDIS_CONN')
    redis = await aioredis.from_url(connection_string)
    return redis

async def disconnect_redis():
    if redis:
        redis.close()
        await redis.wait_closed()

connect_redis()
print(redis)