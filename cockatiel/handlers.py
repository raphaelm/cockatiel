import asyncio

from aiohttp import web


@asyncio.coroutine
def get_file(request):
    # name = request.match_info.get('name')
    raise web.HTTPBadRequest()


@asyncio.coroutine
def put_file(request):
    raise web.HTTPBadRequest()


@asyncio.coroutine
def delete_file(request):
    raise web.HTTPBadRequest()
