from amaranthie.activity import Activity
from amaranthie import local_pubsub
from amaranthie import config
import logging
import json
import asyncio
import sys

log = logging.getLogger(__name__)

class UdpServer(Activity):
    async def handle(self, string, addr):
        try:
            obj = json.loads(string.decode(config.get(config.udp_encoding)))
            topic = obj["topic"]
            content = obj["content"]
            obj["lazy_sender"] = addr
            await local_pubsub.pub(topic, content)
        except Exception as ex:
            logging.debug("Failed to parse udp message: %s", ex)

    class Protocol(asyncio.DatagramProtocol):
        def connection_made(self, transport):
            pass

        def datagram_received(self_inner, data, addr):
            self.handle(data, addr)

    async def run(self):
        log.warning("Hacky UDP port selection!")
        self.port = config.get(config.udp_port) + int(sys.argv[1])

        loop = asyncio.get_running_loop()

        self.transport, self.protocol = await loop.create_datagram_endpoint(
                lambda: self.Protocol(), local_addr=('0.0.0.0', self.port))
        log.info("Listening for UDP on port %d", self.port)
