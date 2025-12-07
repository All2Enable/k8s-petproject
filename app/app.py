import os
from flask import Flask
import redis

app = Flask(__name__)

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = 6379

try:
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
except Exception as e:
    print(f"Error connecting to Redis: {e}")

@app.route('/')
def hello():
    try:
        count = r.incr('hits')
        return f"Hello from Kubernetes! I have been seen {count} times.\n Hostname: {os.uname()[1]}\n"
    except redis.exceptions.ConnectionError:
        return f"Hello! (Redis is not available)\n Hostname: {os.uname()[1]}\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)