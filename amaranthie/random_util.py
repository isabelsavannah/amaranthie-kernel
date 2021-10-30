import random
import string

charset = string.ascii_lowercase + string.digits

def random_id():
    return "".join([random.choice(charset) for _ in range(0, 32)])

def random_delay(max_delay):
    return random.randrange(max_delay/2, max_delay)

def shuffled(ls):
    return random.sample(ls, len(ls))
