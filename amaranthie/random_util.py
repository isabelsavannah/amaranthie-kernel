import random
import string

charset = string.ascii_lowercase + string.digits

def random_id():
    return "".join([random.choice(charset) for _ in range(0, 32)])

