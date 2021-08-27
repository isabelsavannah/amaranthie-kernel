from aiohttp import web
from schema import schema
from strawberry.aiohttp.views import GraphQLView

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

if __name__ == '__main__':
    web.run_app(app)
