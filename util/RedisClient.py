import json
from aioredis import Redis


class RedisClient(Redis):
    async def hset_json(self, name, key, value):
        return await self.hset(name, key, json.dumps(value))

    async def hget_json(self, name, key):
        obj = await self.hget(name, key)
        return json.loads(obj) if obj is not None else obj

    async def hgetall_json(self, name):
        obj = await self.hgetall(name)
        return {
            k.decode("utf-8")
            if isinstance(k, bytes)
            else k: json.loads(v)
            if v is not None
            else v
            for k, v in obj.items()
        }

    async def set_key(self, name, value, expire: int = None) -> bool:
        return await self.set(name, value, ex=expire)

    async def get_key(self, name):
        result = await self.get(name)
        return result.decode("utf-8") if isinstance(result, bytes) else result
