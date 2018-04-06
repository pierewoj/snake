import requests
import json
import random
import hashlib
import redis
import uuid
import os

redis_host = os.environ['REDIS_HOSTNAME']
player_tokens_hash = 'player_tokens'

r = redis.StrictRedis(host=redis_host, port=6379, db=0)

print('please provide player name')
player_name = input()
print('generating token')
token = str(uuid.uuid4())
hashed_token = hashlib.sha256(token.encode('utf-8')).hexdigest()
print('uplodating token')
r.hset(player_tokens_hash, player_name, hashed_token)
print('successfully uploaded token for player='+player_name)
print('token for ' + player_name
print(token)
print('')