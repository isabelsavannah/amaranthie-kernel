import time
from amaranthie.config import config

def now():
    return [time.time(), config.get(config.my_id)]
