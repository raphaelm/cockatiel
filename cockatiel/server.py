from aiohttp import web
from .handlers import get_file, delete_file, put_file
from .config import parser


def run(*cmdargs):
    args = parser.parse_args(args=cmdargs)
    web.run_app(app, port=args.port, host=args.host)


app = web.Application()
app.router.add_route('GET', '/{name}', get_file)
app.router.add_route('PUT', '/{name}', put_file)
app.router.add_route('DELETE', '/{name}', delete_file)
