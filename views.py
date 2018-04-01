from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from itertools import cycle
from django.conf import settings
import json
import redis
import hashlib

live_game_key = 'live_game'
player_tokens_hash = 'player_tokens'
redis_db = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=0)
colors = ['black', 'red', 'yellow', 'blue', 'orange']
# Create your views here.
def index(request):
    context = { }
    return render(request, 'index.html', context)

def board(request):
    existing_game_serialized =  redis_db.get(live_game_key)
    if existing_game_serialized == None:
        return JsonResponse({'exists':False})  
    game = json.loads(existing_game_serialized)
    width = game['board_width']
    height = game['board_height']
    
    #building players
    colors_pool = cycle(colors)
    players = {}
    for snake in game['snakes']:
        color = next(colors_pool)
        player_id = snake['player_id']
        players[player_id] = {
            'id' : player_id,
            'color' : color
        }

    #building square colors
    square_colors=['white' for i in range(width*height)]
    for snake in game['snakes']:
        if snake['is_alive'] == False:
            continue
        player_id = snake['player_id']
        for field in snake['fields']:
            x = field['x']
            y = field['y']
            pos = width * (height - 1 - y) + x
            square_colors[pos] = players[player_id]['color']

    result = {}
    result['width'] = width
    result['height'] = height
    result['players'] = list(players.values())
    result['square_colors'] = square_colors
    result['round'] = game['round']
    result['max_rounds'] = game['max_rounds']
    
    result['leaderboard'] = [{
        'player_id' : player.decode("utf-8"), 
        'score' : score
        } for (player,score) in redis_db.zrange('scores',0,-1,withscores=True)[::-1]]

    return JsonResponse(result)

def game(request):
    existing_game_serialized =  redis_db.get(live_game_key)
    if existing_game_serialized == None:
        return HttpResponseNotFound('There are no active games. Please retry.')
    game = json.loads(existing_game_serialized)
    return JsonResponse(game)

def decision(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('/decision only supports POST HTTP method')

    payload = json.loads(request.body)
    player_id = payload.get('player_id')
    player_token = payload.get('player_token')
    game_id = payload.get('game_id')
    decision = payload.get('decision')

    if player_id == None:
        return HttpResponseBadRequest('player_id not set')
    if player_token == None:
        return HttpResponseBadRequest('player_token not set')
    if game_id == None:
        return HttpResponseBadRequest('game_id not set')
    if decision == None:
        return HttpResponseBadRequest('decision is not set')
    if decision not in ['N', 'E', 'W', 'S']:
        return HttpResponseBadRequest('decision must be one of {N, E, W, S}')
    
    real_token_hash = redis_db.hget(player_tokens_hash, player_id)
    if real_token_hash == None:
        return HttpResponse('Token for given player was not found. Please check player_id.', status=401)
    
    real_token_hash = real_token_hash.decode("utf-8")
    hashed_token = hashlib.sha256(player_token.encode('utf-8')).hexdigest()

    if hashed_token != real_token_hash:
        return HttpResponse('Invalid token provided', status=401)

    redis_db.set(game_id+'#'+player_id, decision,ex=30)

    result = {}
    result['status'] = 'saved'
    return JsonResponse(result)