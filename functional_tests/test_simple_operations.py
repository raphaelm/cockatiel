import hashlib

import requests

from .utils import running_cockatiel


def test_put_file_correctly():
    with running_cockatiel() as port:
        content = 'Hello, this is a testfile'.encode('utf-8')
        checksum = hashlib.sha1(content).hexdigest()
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']
        assert path == '/foo/bar_%s.txt' % checksum

        resp = requests.get(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=port),
            content
        )
        assert resp.content == content
        assert resp.headers['Content-Type'] == 'text/plain'


def test_remove_file_correctly():
    with running_cockatiel() as port:
        content = 'Hello, this is a testfile'.encode('utf-8')
        checksum = hashlib.sha1(content).hexdigest()
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']
        assert path == '/foo/bar_%s.txt' % checksum

        resp = requests.delete(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=port),
        )
        assert resp.status_code == 200

        resp = requests.get(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=port),
            content
        )
        assert resp.status_code == 404
