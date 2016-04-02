from aiohttp import web

from . import config
from .handlers import get_file, delete_file, put_file


def run(cmdargs=None):
    if cmdargs:
        config.args = config.parser.parse_args(args=cmdargs)
    else:
        config.args = config.parser.parse_args()

    web.run_app(app, port=config.args.port, host=config.args.host)


app = web.Application()
app.router.add_route('GET', '/{name:.*}', get_file)
app.router.add_route('PUT', '/{name:.*}', put_file)
app.router.add_route('DELETE', '/{name:.*}', delete_file)
