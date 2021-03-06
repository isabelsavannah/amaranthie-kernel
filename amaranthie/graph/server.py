import asyncio
import sys
from aiohttp import web
from amaranthie import config
from amaranthie.activity import Activity
from amaranthie.graph.schema import schema
from strawberry.aiohttp.views import GraphQLView
import logging
log = logging.getLogger(__name__)

class GraphServer(Activity):
    async def start(self):
        log.warning("Hacky graphql port selection!")
        self.port = config.get(config.graphql_port) + int(sys.argv[1])
        self.app = web.Application()
        self.app.router.add_route("*", "/graphql", GraphQLView(schema=schema))
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

    async def run(self):
        log.info("Listening for graphql on port %d", self.port)
        await web.TCPSite(self.runner, '127.0.0.1', self.port).start()
