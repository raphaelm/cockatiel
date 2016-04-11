import asyncio
import logging
import os

from aiohttp import web
from cockatiel.dellog import DeletionLog

from . import config, replication, handlers, version

logger = logging.getLogger(__name__)


def create_app(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/_status', handlers.status)
    app.router.add_route('GET', '/{name:.+}', handlers.get_file)
    app.router.add_route('PUT', '/{name:.+}', handlers.put_file)
    app.router.add_route('DELETE', '/{name:.+}', handlers.delete_file)
    app.router.add_route('HEAD', '/{name:.+}', handlers.get_file)
    return app


@asyncio.coroutine
def on_response_prepare(request, response):
    response.headers['Server'] = 'cockatiel/' + version
    return response


def run(cmdargs=None, logprefix=''):
    if cmdargs:
        config.args = config.parser.parse_args(args=cmdargs)
    else:
        config.args = config.parser.parse_args()

    logging.basicConfig(
        format=logprefix + '{asctime} {levelname} {name}: {message}',
        style='{',
        level=logging.DEBUG if config.args.verbose else logging.WARNING
    )

    if not os.path.exists(config.args.queue):
        os.makedirs(config.args.queue)
    replication.dellog = DeletionLog(os.path.join(config.args.queue, 'deletion.log'))

    logger.info('Starting up...')
    loop = asyncio.get_event_loop()
    start_replication_workers(loop)
    app = create_app(loop)
    app.on_response_prepare.append(on_response_prepare)
    web.run_app(app, port=config.args.port, host=config.args.host, print=logger.info)
    logger.info('Starting to tear down workers...')
    stop_replication_workers(loop)
    logger.info('Goodbye.')


def start_replication_workers(loop):
    replication.running = True
    for node in replication.get_nodes():
        loop.create_task(replication.replication_worker(node))


def stop_replication_workers(loop):
    replication.running = False
