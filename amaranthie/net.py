import random
import asyncio
import json
from amaranthie.local_peers import local_peers

async def lazy_broadcast(topic, content):
    for peer in local_peers():
        await lazy_send(peer, topic, content)

async def lazy_send(target_ref, topic, content):
    msg = {"topic": topic, "data": content}

    class Sender:
        def connection_made(self, transport):
            import pdb
            pdb.set_trace()
            print(msg)
            transport.sendto(json.dumps(msg))

    await asyncio.get_running_loop().create_datagram_endpoint(
            lambda: Sender(), remote_addr=(target_ref.host, target_ref.port))

def get_random_peer_ref():
    return random.choice(local_peers())
