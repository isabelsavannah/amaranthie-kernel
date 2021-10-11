from amaranthie.random_util import random_id
from amaranthie import logging_util

config = {
  "id": random_id(),

  "peers": {
    "listen_port": 2000,
    "heartbeat_interval_seconds": 30,
    "connect_interval_seconds": 10,
  },

  "state": {
    "path": "state",
    "encoding": "utf-8",
  },
}

logging_util.set_id(config["id"])
