import asyncio
import hashlib
import json
import logging
import mimetypes
import os
import tempfile

from aiohttp import streams, web

from . import config
from .replication import queue_operation, get_nodes, get_queue_for_node
from .utils.filenames import generate_filename, get_hash_from_name
from .utils.streams import chunks

logger = logging.getLogger(__name__)


@asyncio.coroutine
def get_file(request: web.Request):
    filename = request.match_info.get('name').strip()
    filepath = os.path.join(config.args.storage, filename)
    _, ext = os.path.splitext(filepath)
    etag = hashlib.sha1(filename.encode('utf-8')).hexdigest()

    if not os.path.exists(filepath):
        raise web.HTTPNotFound()

    if 'If-None-Match' in request.headers:
        raise web.HTTPNotModified(headers={
            'ETag': etag
        })

    stat = os.stat(filepath)

    if request.method == 'HEAD':
        resp = web.Response()
    else:
        resp = web.StreamResponse()

    resp.headers['Content-Type'] = mimetypes.types_map.get(ext, 'application/octet-stream')
    resp.headers['ETag'] = etag
    resp.headers['Cache-Control'] = 'max-age=31536000'
    resp.headers['X-Content-SHA1'] = get_hash_from_name(filename)
    resp.content_length = stat.st_size
    resp.last_modified = stat.st_mtime

    if request.method == 'HEAD':
        return resp

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
        try:
            while True:
                chunk = yield from request._payload.read(1024)
                if chunk is streams.EOF_MARKER:
                    break
                print(repr(chunk), type(chunk))
                if isinstance(chunk, asyncio.Future):
                    print("FUTURE: %r!" % chunk)
                    chunk = yield from asyncio.wait_for(chunk, timeout=60)
                    print("FUTURE RETURNED: %r" % chunk)
                if chunk:
                    checksum.update(chunk)
                    tmpfile.write(chunk)
                else:
                    print("CHUNK IS: %s" % chunk)
        except asyncio.TimeoutError:
            raise web.HTTPRequestTimeout()

        calculated_hash = checksum.hexdigest()
        if 'X-Content-SHA1' in request.headers:
            client_hash = request.headers['X-Content-SHA1'].lower()
            if calculated_hash != client_hash:
                logger.warn('SHA1 hash mismatch: %s != %s' % (calculated_hash, client_hash))
                raise web.HTTPBadRequest(text='SHA1 hash does not match')

        filename = generate_filename(request.match_info.get('name').strip(), calculated_hash)
        filepath = os.path.join(config.args.storage, filename)

        if not os.path.exists(filepath):
            directory, _ = os.path.split(filepath)
            os.makedirs(directory, exist_ok=True)

            tmpfile.seek(0)
            with open(filepath, 'wb') as f:
                for chunk in chunks(tmpfile):
                    f.write(chunk)

            logger.debug('Created file {}, scheduling replication.'.format(filename))
            queue_operation('PUT', filename)
            return web.Response(status=201, headers={
                'Location': '/' + filename
            })
        else:
            logger.debug('File {} already existed.'.format(filename))
            return web.Response(status=302, headers={
                'Location': '/' + filename
            })


@asyncio.coroutine
def delete_file(request: web.Request):
    filename = request.match_info.get('name').strip()
    filepath = os.path.join(config.args.storage, filename)

    if not os.path.exists(filepath):
        logger.debug('File {} does not exist, cannot delete it.'.format(filename))
        raise web.HTTPNotFound()

    os.remove(filepath)
    # TODO: Clean up now-empty dictionaries

    logger.debug('Deletedfile {}, scheduling replication.'.format(filename))
    queue_operation('DELETE', filename)
    return web.Response()


@asyncio.coroutine
def status(request: web.Request):
    stat = {
        'queues': {
            n: {
                'length': len(get_queue_for_node(n))
            } for n in get_nodes()
            }
    }
    return web.Response(text=json.dumps(stat), headers={
        'Content-Type': 'application/json'
    })
