subscriptins = {}
from asy import create_task_watch_error

def subscribe(prefix, callback):
    subscriptions.setdefault(prefix, []).append(callback)

def deliver(prefix, content):
    target = RichId(prefix)
    for i in range(1, len(prefix)):
        target_prefix = RichId(target.id_words[0:i])
        if target_prefix not in subscriptions:
            continue
        for callback in subscriptions[target_prefix]:
            create_task_watch_error(run(callback, content))

async def run(callback, content):
    callback(content)
