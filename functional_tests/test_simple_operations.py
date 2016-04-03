import hashlib

import requests

from .utils import running_cockatiel


def test_put_file_correctly():
    with running_cockatiel() as proc:
        content = 'Hello, this is a testfile'.encode('utf-8')
        checksum = hashlib.sha1(content).hexdigest()
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=proc.port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']
        assert path == '/foo/bar_%s.txt' % checksum

        resp = requests.get(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=proc.port),
            content
        )
        assert resp.status_code == 200
        assert resp.content == content
        assert resp.headers['Content-Type'] == 'text/plain'
        assert 'Etag' in resp.headers
        etag = resp.headers['Etag']
        assert resp.headers['Cache-Control'] == 'max-age=31536000'

        resp = requests.get(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=proc.port),
            content, headers={
                'If-None-Match': etag
            }
        )
        assert resp.status_code == 304
        assert resp.headers['Etag'] == etag


def test_remove_file_correctly():
    with running_cockatiel() as proc:
        content = 'Hello, this is a testfile'.encode('utf-8')
        checksum = hashlib.sha1(content).hexdigest()
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=proc.port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']
        assert path == '/foo/bar_%s.txt' % checksum

        resp = requests.delete(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=proc.port),
        )
        assert resp.status_code == 200

        resp = requests.get(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=proc.port),
            content
        )
        assert resp.status_code == 404
