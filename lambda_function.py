import os
import json
import redis

def lambda_handler(event, context):
    REDIS_HOSTNAME = os.environ['REDIS_HOSTNAME']
    rs = redis.StrictRedis(host=REDIS_HOSTNAME, port=6379, db=0)
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": { },
        "body": "hi "+rs.get(None)
    }