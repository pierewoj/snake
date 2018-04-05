# Snake

## How to run
To run the game runner, you need to set up an EC2 instance with access to redis (can be ElastiCache) and then (substitute hostname before pasting):
```
export REDIS_HOSTNAME=SOMEREDISHOSTNAME.DOMAIN.COM
sudo yum install git
git clone https://github.com/pierewoj/snake.git
cd snake/runner
./setup_runner.sh
python runner.py
```
