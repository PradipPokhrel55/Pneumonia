import redis
import json

r = redis.Redis()

def save_response(key,response):
    r.set(key, json.dumps(response))

def get_cached_response(key):
    data = r.get(key)
    return json.loads(data) if data else None