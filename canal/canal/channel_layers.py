"""
Settings for the channel layers. Read connection information from
environment so the service can run inside Docker/CI where Redis runs
in a separate container.
"""
import os

# Allow overriding Redis host/port via environment
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}
