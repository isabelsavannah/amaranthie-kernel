from aiohttp import web
from schema import schema

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
app.add_routes([web.get('/', handle),
                web.get('/graphql', handle_graph)])

if __name__ == '__main__':
    web.run_app(app)
