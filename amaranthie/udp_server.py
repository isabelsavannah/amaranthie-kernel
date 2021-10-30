from amaranthie.activity import Activity
from amaranthie.local_peers import LocalPeerRef
from amaranthie import local_pubsub
from amaranthie import config
import logging
import json
import asyncio
import sys

log = logging.getLogger(__name__)

class UdpServer(Activity):
    class Protocol(asyncio.DatagramProtocol):
        def connection_made(self, transport):
            pass

        def datagram_received(self, data, addr):
            try:
                obj = json.loads(data.decode(config.get(config.udp_encoding)))
                topic = obj["topic"]
                content = obj["data"]
                host, peer = addr
                obj["lazy_sender"] = LocalPeerRef('0.0.0.0', peer-1000)
                local_pubsub.pub(topic, obj)
            except Exception as ex:
                log.debug("Failed to parse udp message: %s", ex)
                raise ex

    async def run(self):
        log.warning("Hacky UDP port selection!")
        self.port = config.get(config.udp_port) + int(sys.argv[1])

        loop = asyncio.get_running_loop()

        self.transport, self.protocol = await loop.create_datagram_endpoint(
                lambda: self.Protocol(), local_addr=('0.0.0.0', self.port))
        log.info("Listening for UDP on port %d", self.port)
