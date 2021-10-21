# all listening servers dump here, all local announcements dump here, it's async, it's a coordination point, local-peers is exempt
# interchange format is json-compatible-python-objects

import asyncio
from amaranthie.asy import create_task_watch_error

registrations = {}

def sub(topic, async_callback):
    if topic not in registrations:
        registrations[topic] = []
    registrations[topic].append(async_callback)

def sub_by_queue():
    # etc
    pass

async def pub(topic, message):
    if topic in registrations:
        [create_task_watch_error(subber(message)) for subber in registrations[topic]]
