import os
import json
import redis

def lambda_handler(event, context):
    redis_hostname = os.environ['REDIS_HOSTNAME']
    live_game_key = 'live_game'
    rs = redis.StrictRedis(host=redis_hostname, port=6379, db=0)
    existing_game_serialized =  rs.get(live_game_key)
    if existing_game_serialized == None:
        return {
            "statusCode": 404,
        }
    game = json.loads(existing_game_serialized)
    return {
        "statusCode": 404,
        "body": game,
    }