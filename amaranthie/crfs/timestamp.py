import time
from amaranthie import config

def now():
    return [time.time(), config.get(config.my_id)]
