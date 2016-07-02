import asyncio
import logging

import aiohttp
import aiohttp.server

logger = logging.getLogger(__name__)


class ProxyRequestHandler(aiohttp.server.ServerHttpProtocol):
    """
    Inspired by https://github.com/jmehnle/aiohttpproxy
    Copyright Julian Mehnle, Apache License 2.0
    """

    def __init__(self):
        super(ProxyRequestHandler, self).__init__()
        self.logger = logger

    @asyncio.coroutine
    def handle_request(self, message, payload):
        url = message.path

        logger.info('{0} {1}'.format(message.method, url))

        if message.method in ('POST', 'PUT', 'PATCH'):
            data = yield from payload.read()
        else:
            data = None

        message, data = self.intercept_request(message, data)
        if not message:
            return

        response = yield from aiohttp.request(message.method, url, headers=message.headers,
                                              data=data)
        response_content = yield from response.content.read()

        response, response_content = self.intercept_response(response, response_content)
        yield from self.response_to_proxy_response(response, response_content)

    def response_to_proxy_response(self, response, response_content):
        proxy_response = aiohttp.Response(self.writer, response.status, http_version=response.version)

        # Copy response headers, except for Content-Encoding header,
        # since unfortunately aiohttp transparently decodes content.
        proxy_response_headers = [(name, value)
                                  for name, value
                                  in response.headers.items() if name not in ('CONTENT-ENCODING',)]
        proxy_response.add_headers(*proxy_response_headers)
        proxy_response.send_headers()

        proxy_response.write(response_content)
        yield from proxy_response.write_eof()

    def intercept_request(self, message, data):
        return message, data

    def intercept_response(self, response, content):
        return response, content


def run(port, cls=None):
    cls = cls or ProxyRequestHandler
    loop = asyncio.get_event_loop()

    logging.basicConfig(
        format='[proxy] {asctime} {levelname} {name}: {message}',
        style='{',
        level=logging.DEBUG
    )

    server_future = loop.create_server(lambda: cls(), '', port)
    server = loop.run_until_complete(server_future)
    logger.info('Accepting HTTP proxy requests on {0}:{1} ...'.format(*server.sockets[0].getsockname()))

    loop.run_forever()


if __name__ == '__main__':
    run(8080)
