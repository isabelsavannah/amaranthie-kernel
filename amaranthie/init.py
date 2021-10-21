import asyncio
from amaranthie.graph.server import GraphServer
from amaranthie.udp_server import UdpServer 

run_set = [
        UdpServer(),
        GraphServer(),
        ]

singleton = None

class Init:
    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.a_run())
        loop.run_forever()

    async def a_run(self):
        await asyncio.gather(*[s.start() for s in run_set])
        await asyncio.gather(*[s.run() for s in run_set])

singleton = Init()
