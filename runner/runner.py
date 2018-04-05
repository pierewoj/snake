from __future__ import print_function # Python 2/3 compatibility
import redis
import json
import uuid
import os
from time import sleep
import sys

redis_host =  os.environ['REDIS_HOSTNAME']
r = redis.StrictRedis(host=redis_host, port=6379, db=0)
live_game_key = 'live_game'
max_rounds = 120
score_retention_coef = 0.98

def create_snake(player_id, col):
    snake = {}
    snake['player_id'] = player_id
    snake['fields'] = list(reversed([{'x':col, 'y':i} for i in range(0,14)]))
    snake['direction'] = 'N'
    snake['is_alive'] = True
    snake['round_died'] = -1
    return snake

def create_game():
    game = {}
    game['id'] = str(uuid.uuid4())
    game['status'] = 'LIVE'
    game['board_width'] = 20
    game['board_height'] = 20
    game['round'] = 0
    game['max_rounds'] = max_rounds
    game['snakes'] = [
        create_snake('player1',0), 
        create_snake('player2',2),
        create_snake('player3',4),
        create_snake('player4',6),]
    return game

def get_game():
    existing_game_serialized = r.get(live_game_key)
    if existing_game_serialized != None:
        return json.loads(existing_game_serialized)
    print('no LIVE games found, creating')
    game = create_game()
    save_game(game)
    return game

# make sure number is in [0,bound)
def bound_number(number,bound):
    if number >= bound:
        return number - bound
    if number < 0:
        return number + bound
    return number

def build_neighbor_field(game, field, direction):
    direction_map = {
        'N' : (0,1),
        'E' : (1,0),
        'W' : (-1,0),
        'S' : (0,1),
        }
    vector = direction_map[direction]

    new_x = bound_number(field['x'] + vector[0], game['board_width'])
    new_y = bound_number(field['y'] + vector[1], game['board_height'])
    return {
        'x' : new_x,
        'y' : new_y
    }

def update_directions(game):
    game_id = game['id']
    for snake in game['snakes']:
        player_id = snake['player_id']
        dec = r.get(game_id+'#'+player_id)
        if dec == None:
            continue
        dec = dec.decode("utf-8") 
        if dec not in ['N', 'E', 'W', 'S']:
            continue
        fields = snake['fields']
        next_field = build_neighbor_field(game, fields[0], dec)
        if next_field == fields[1]:
            continue
        snake['direction'] = dec

def field_to_str(field):
    return str(field['x']) + '#' + str(field['y'])

def process_game(game):
    taken_fields={}
    for snake in game['snakes']:
        if snake['is_alive'] == False:
            continue
        for field in snake['fields']:
            player_id = snake['player_id']
            if taken_fields.get(field_to_str(field)) == None:
                taken_fields[field_to_str(field)] = [player_id]
            else:
                taken_fields[field_to_str(field)].append('player_id')

    for snake in game['snakes']:
        if snake['is_alive'] == False:
            continue
        head = snake['fields'][0]
        if len(taken_fields[field_to_str(head)]) > 1:
            snake['is_alive'] = False
            snake['round_died'] = game['round']

    for snake in game['snakes']:
        if snake['is_alive'] == False:
            continue
        fields = snake['fields']
        new_field = build_neighbor_field(game, fields[0], snake['direction'])
        snake['fields'] = [new_field] + fields[0:-1]
    
    game['round'] = game['round'] + 1

def save_game(game):
    r.set(live_game_key, json.dumps(game))

def update_scores(game):
    scores_key = 'scores'
    for (player,score) in r.zrange(scores_key,0,-1,withscores=True):
        r.zadd(scores_key, score*score_retention_coef, player)
    for snake in game['snakes']:
        player=snake['player_id']
        score = r.zscore(scores_key,player)
        if score == None:
            score = 0
        added_score = 0
        if snake['round_died'] == -1:
            added_score = game['max_rounds']
        else:
            added_score = snake['round_died']
        new_score = score + (1-score_retention_coef) * added_score
        r.zadd(scores_key,new_score,player)

while True:
    print('getting game')
    game = get_game()
    print(game)
    update_directions(game)
    process_game(game)
    save_game(game)
    if sum(snake['is_alive'] for snake in game['snakes']) < 2 or game['round'] >= game['max_rounds']:
        update_scores(game)
        r.delete(live_game_key)
    sleep(1)