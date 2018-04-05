import os
import json
import redis
import hashlib

def bad_request_response(reason):
    return {
        'statusCode' : 400,
        'message' : reason
    }

player_tokens_hash = 'player_tokens'

def lambda_handler(event, context):
    player_id = event.get('player_id')
    player_token = event.get('player_token')
    game_id = event.get('game_id')
    decision = event.get('decision')
    redis_hostname = os.environ['REDIS_HOSTNAME']
    rs = redis.StrictRedis(host=redis_hostname, port=6379, db=0)

    if player_id == None:
        return bad_request_response('player_id not set')
    if player_token == None:
        return bad_request_response('player_token not set')
    if game_id == None:
        return bad_request_response('game_id not set')
    if decision == None:
        return bad_request_response('decision is not set')
    if decision not in ['N', 'E', 'W', 'S']:
        return bad_request_response('decision must be one of {N, E, W, S}')
    
    real_token_hash = rs.hget(player_tokens_hash, player_id)
    if real_token_hash == None:
        return bad_request_response('Token for given player was not found. Please check player_id.')
    
    real_token_hash = real_token_hash.decode("utf-8")
    hashed_token = hashlib.sha256(player_token.encode('utf-8')).hexdigest()

    if hashed_token != real_token_hash:
        return bad_request_response('Invalid token provided')

    rs.set(game_id+'#'+player_id, decision,ex=30)

    return {
        'statusCode' : 200,
        'message' : 'saved'
    }
