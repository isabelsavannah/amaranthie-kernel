# all listening servers dump here, all local announcements dump here, it's async, it's a coordination point, local-peers is exempt
# interchange format is json-compatible-python-objects

import asyncio
from amaranthie.asy import create_task_watch_error
from amaranthie.rich_id import RichId

registrations = {}

def sub(topic, async_callback):
    topic = str(RichId(topic))
    if topic not in registrations:
        registrations[topic] = []
    registrations[topic].append(async_callback)

async def split_run(callback, msg):
    await callback(msg)

def pub(topic, message):
    if topic in registrations:
        [create_task_watch_error(split_run(subber, message)) for subber in registrations[topic]]
