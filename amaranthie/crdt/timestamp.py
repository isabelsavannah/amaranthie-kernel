import time
from amaranthie.config import config

def now():
    return [time.time(), config["id"]]
