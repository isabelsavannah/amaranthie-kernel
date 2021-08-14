subscriptins = {}

def subscribe(prefix, callback):
    subscriptions.setdefault(prefix, []).append(callback)

async def deliver(prefix, content):




