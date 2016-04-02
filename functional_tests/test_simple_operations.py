import hashlib

import requests

from .utils import running_cockatiel


def test_put_file():
    with running_cockatiel() as port:
        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}/{name}.{ext}'.format(
                name=hashlib.sha256(content).hexdigest(), ext='txt',
                port=port),
            content
        )
        assert resp.status_code == 201
