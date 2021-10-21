import asyncio
from aiohttp import web
from amaranthie.graph.schema import schema
from amaranthie.activity import Activity
from strawberry.aiohttp.views import GraphQLView
import logging
log = logging.getLogger(__name__)

class GraphServer:
    async def start(self):
        self.app = web.Application()
        self.app.router.add_route("*", "/graphql", GraphQLView(schema=schema))
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

    async def run(self):
        await web.TCPSite(self.runner).start()
