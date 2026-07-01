import redis.asyncio as redis
from decouple import config


""" pushing redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

