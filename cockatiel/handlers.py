import asyncio
import hashlib
import mimetypes
import os
import tempfile

from aiohttp import web

from . import config
from .replication import queue_operation
from .utils.filenames import generate_filename
from .utils.streams import async_chunks, chunks


@asyncio.coroutine
def get_file(request: web.Request):
    filename = request.match_info.get('name').strip()
    filepath = os.path.join(config.args.storage, filename)
    _, ext = os.path.splitext(filepath)

    if not os.path.exists(filepath):
        raise web.HTTPNotFound()

    stat = os.stat(filepath)

    resp = web.StreamResponse()
    resp.headers['Content-Type'] = mimetypes.types_map.get(ext, 'application/octet-stream')
    resp.content_length = stat.st_size
    resp.last_modified = stat.st_mtime

    yield from resp.prepare(request)
    with open(filepath, 'rb') as f:
        for chunk in chunks(f):
            resp.write(chunk)
            yield from resp.drain()

    yield from resp.write_eof()
    return resp


@asyncio.coroutine
def put_file(request: web.Request):
    checksum = hashlib.sha1()

    with tempfile.SpooledTemporaryFile(max_size=1024 * 1024) as tmpfile:
        for chunk in async_chunks(request.content):
            checksum.update(chunk)
            tmpfile.write(chunk)

        calculated_hash = checksum.hexdigest()
        filename = generate_filename(request.match_info.get('name').strip(), calculated_hash)
        filepath = os.path.join(config.args.storage, filename)

        if not os.path.exists(filepath):
            directory, _ = os.path.split(filepath)
            os.makedirs(directory, exist_ok=True)

            tmpfile.seek(0)
            with open(filepath, 'wb') as f:
                for chunk in chunks(tmpfile):
                    f.write(chunk)

            queue_operation('PUT', filename)
            return web.Response(status=201, headers={
                'Location': '/' + filename
            })
        else:
            return web.Response(status=302, headers={
                'Location': '/' + filename
            })


@asyncio.coroutine
def delete_file(request: web.Request):
    filename = request.match_info.get('name').strip()
    filepath = os.path.join(config.args.storage, filename)

    if not os.path.exists(filepath):
        raise web.HTTPNotFound()

    os.remove(filepath)
    # TODO: Clean up now-empty dictionaries

    queue_operation('DELETE', filename)
    return web.Response()
