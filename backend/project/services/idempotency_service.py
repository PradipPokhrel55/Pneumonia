import json
import os

import redis


r = redis.Redis.from_url(os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0"))

def save_response(key,response):
    r.set(key, json.dumps(response))

def get_cached_response(key):
    data = r.get(key)
    return json.loads(data) if data else None