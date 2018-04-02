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
    
    return {
        "statusCode": 200,
        "body": json.dumps(result),
    }