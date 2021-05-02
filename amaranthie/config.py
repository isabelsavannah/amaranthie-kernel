from amaranthie.random import random_id

config = {
  "id": random_id(),

  "peers": {
    "listen_port": 2000,
    "heartbeat_interval_seconds": 30,
    "connect_interval_seconds": 10,
  },

  "state": {
    "path": "state",
  },
}
