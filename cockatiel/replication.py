import asyncio
import logging
import os
import string
from urllib.parse import urljoin

import aiohttp

from . import config, version
from .queue import FSQueue

running = True
logger = logging.getLogger(__name__)
MIN_INTERVAL = 0.5
MAX_INTERVAL = 60
DEFAULTHEADERS = {
    'User-Agent': 'cockatiel/' + version
}

# We use this as a singleton. It is populated from the server module.
dellog = None


class ReplicationFailed(IOError):
    pass


def get_queue_for_node(node_url):
    prefix = "".join(c for c in node_url if c in string.ascii_letters or c in string.digits)
    return FSQueue(basedir=config.args.queue, subdir=prefix)


def get_nodes():
    nodes = config.args.node
    return nodes or []


def get_all_queues():
    return [get_queue_for_node(n) for n in get_nodes()]


def queue_operation(operation, filename):
    for queue in get_all_queues():
        queue.put({
            'operation': operation,
            'filename': filename
        })


@asyncio.coroutine
def perform_operation(session, node, obj):
    logger.debug('[-> {node}] Propagating operation {obj!r}'.format(
        node=node, obj=obj
    ))
    if obj['operation'] == 'PUT':
        filepath = os.path.join(config.args.storage, obj['filename'])
        if not os.path.exists(filepath):
            logger.debug('[-> {node}] File has been deleted in the meantime.'.format(
                node=node,
            ))
            return
        with open(filepath, 'rb') as f:
            resp = yield from session.put(urljoin(node, obj['filename']), data=f, headers=DEFAULTHEADERS)
    elif obj['operation'] == 'DELETE':
        resp = yield from session.delete(urljoin(node, obj['filename']), headers=DEFAULTHEADERS)
    else:
        raise ValueError('Unknown operation mode {}'.format(obj['operation']))

    if resp.status >= 400:
        if resp.status == 404 and obj['operation'] == 'DELETE':
            # Deleting a file that does not exist is fine.
            return
        if resp.status == 409 and obj['operation'] == 'PUT':
            # Putting a file to a node that has it already deleted is file. The
            # deletion operation will reach us eventually, we'll just wait here.
            return
        body = yield from resp.text()
        yield from resp.close()
        raise ReplicationFailed('Received status code {} with body {}'.format(
            resp.status, body
        ))


@asyncio.coroutine
def queue_getter(queue):
    qitem = queue.get(delete=False)
    if qitem is not None:
        return qitem
    else:
        yield from asyncio.sleep(0.5)


@asyncio.coroutine
def replication_worker(node: str):
    if not running:
        return

    queue = get_queue_for_node(node)
    interval = MIN_INTERVAL

    logger.debug('[-> {node}] Starting...'.format(
        node=node,
    ))

    with aiohttp.ClientSession() as session:
        try:
            while True:
                qitem = yield from queue_getter(queue)
                if qitem:
                    itemid, obj = qitem
                else:
                    continue
                try:
                    yield from perform_operation(session, node, obj)
                    interval = MIN_INTERVAL
                    logger.debug('[-> {node}] Operation replicated successfully'.format(node=node))
                except (IOError, aiohttp.errors.ClientError):
                    logger.exception('[-> {node}] Error during replication'.format(node=node))
                    yield from asyncio.sleep(interval)
                    # Slow down repetitions
                    interval = max(interval * 2, MAX_INTERVAL)
                else:
                    queue.delete(itemid)
        except asyncio.CancelledError:
            logger.debug('[-> {node}] Cancelled.'.format(
                node=node,
            ))
    logger.debug('[-> {node}] Goodbye.'.format(
        node=node,
    ))
