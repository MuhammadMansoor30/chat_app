import redis.asyncio as redis

redis_client = redis.from_url("redis://127.0.0.1:6379")

async def user_connected(user_id, channel_name):
    key = f"user_connections:{user_id}"

    async with redis_client.pipeline(transaction=True) as pipe:
        pipe.sadd(key, channel_name)
        pipe.sadd("online_users", user_id)
        pipe.scard(key)
        pipe.expire(key, 60)
        pipe.expire("online_users", 60)

        results = await pipe.execute()
        
    return results[1] == 1

async def user_disconneted(user_id, channel_name):
    key = f"user_connections:{user_id}"

    await redis_client.srem(key, channel_name)
    remaining = await redis_client.scard(key)

    if remaining == 0:
        await redis_client.delete(key)
        await redis_client.srem("online_users", user_id)

        return False

    return True

async def total_online_users():
    return await redis_client.scard("online_users")