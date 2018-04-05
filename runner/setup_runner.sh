sudo yum update
sudo yum install python gcc make
pip install --upgrade pip
pip install redis

# installing redis
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make