import random
import asyncio
import json
import logging
from amaranthie import config
from amaranthie.local_peers import local_peers

log = logging.getLogger(__name__)

async def lazy_broadcast(topic, content):
    for peer in local_peers():
        await lazy_send(peer, topic, content)

async def lazy_send(target_ref, topic, content, error_handler=lambda x: x):
    msg = {"topic": topic, "data": content}

    class Sender:
        def connection_made(self, transport):
            transport.sendto(json.dumps(msg).encode(config.get(config.udp_encoding)))

        def error_received(self, exc):
            log.debug("udp send to %s failed with %s", target_ref, exc)
            error_handler(exc)

    await asyncio.get_running_loop().create_datagram_endpoint(
            lambda: Sender(), remote_addr=(target_ref.host, target_ref.port))

def get_random_peer_ref():
    return random.choice(local_peers())
