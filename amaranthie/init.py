import asyncio
from amaranthie.graph.server import GraphServer
from amaranthie.udp_server import UdpServer 
from amaranthie.activity import Activity
from amaranthie.crfs.domain import Domain

class Init(Activity):

    async def start(self):
        run_set = [UdpServer(), GraphServer()]
        await asyncio.gather(*[s.start_tagged() for s in run_set])
        await asyncio.gather(*[s.run_tagged() for s in run_set])

    async def run(self):
        Domain.get("internet").execute()

    def run_forever(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start_tagged())
        loop.run_until_complete(self.run_tagged())
        loop.run_forever()

exists = None
def singleton():
    global exists
    if not exists:
        exists = Init()
    return exists
