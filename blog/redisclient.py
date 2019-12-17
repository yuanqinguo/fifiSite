import redis
import config

redis_client = None

def get_redis():
    global redis_client
    if redis_client == None:
        redis_client = redis.Redis(host=config.REDIS_HOST, password=config.REDIS_PASSWD, port=config.REDIS_PORT, db=0)

    return redis_client
