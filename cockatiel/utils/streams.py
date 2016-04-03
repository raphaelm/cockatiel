import asyncio

from aiohttp.streams import EOF_MARKER


def chunks(stream, chunk_size=1024):
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        yield chunk


@asyncio.coroutine
def request_chunks(request, chunk_size=1024):
    while True:
        chunk = yield from request._payload.read(chunk_size)
        if chunk is EOF_MARKER:
            break
        yield chunk
