# Snake
This repo contains source for online multiplayer snake game. Each snake in game can be controlled via HTTP API calls. State of the game can be viewed by using static website: https://4eynt6qa83.execute-api.eu-central-1.amazonaws.com/prod/

## Architecture
This game is hosted on AWS using:
* Lambda
* API Gateway
* ElastiCache (Redis)
* S3

## API 
The API of this game is quite simple and contains only 3 operations:
- GET /game - returns current state of the game (positions of snakes, round rumber)
- POST /decision - allows setting the direction of snake
- GET /board - returns board state to be displayed by the static website

## Running the game
To run the game runner, you need to set up an EC2 instance with access to redis (can be ElastiCache) and then (substitute hostname before pasting):
```
export REDIS_HOSTNAME=SOMEREDISHOSTNAME.DOMAIN.COM
sudo yum install git
git clone https://github.com/pierewoj/snake.git
cd snake/runner
./setup_runner.sh
python runner.py
```
