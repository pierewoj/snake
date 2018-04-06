import requests
import json
import random
import hashlib
import redis
import uuid
import os
import fileinput

redis_host = os.environ['REDIS_HOSTNAME']
player_tokens_hash = 'player_tokens'

r = redis.StrictRedis(host=redis_host, port=6379, db=0)

player_name = raw_input('please provide player name')
print('generating token')
token = str(uuid.uuid4())
hashed_token = hashlib.sha256(token.encode('utf-8')).hexdigest()
print('uplodating token')
r.hset(player_tokens_hash, player_name, hashed_token)
print('successfully uploaded token for player='+player_name)
print('token for ' + player_name)
print(token)
print('')