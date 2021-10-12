import asyncio
from aiohttp import web
from amaranthie.graph.schema import schema
from strawberry.aiohttp.views import GraphQLView
import logging
log = logging.getLogger(__name__)

async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

async def handle_graph(request):
    request_data = request.query
    if 'query' in request_data:
        return web.Response(text=str(schema.execute(request_data['query'])))
    return web.Response(text="no query?")

app = web.Application()
app.add_routes([web.get('/', handle)])
app.router.add_route("*", "/graphql", GraphQLView(schema=schema))

def start():
    try:
        runner = web.AppRunner(app)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(runner.setup())
        loop.run_until_complete(web.TCPSite(runner).start())
    except:
        log.critical("Failed to start graphql server")
