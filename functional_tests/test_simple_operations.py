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
        assert resp.headers['X-Content-SHA1'] == checksum

        resp = requests.get(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=proc.port), headers={
                'If-None-Match': etag
            }
        )
        assert resp.status_code == 304
        assert resp.headers['Etag'] == etag

        resp = requests.head(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=proc.port),
        )
        assert resp.status_code == 200
        assert resp.headers['Etag'] == etag
        assert resp.text.strip() == ""


def test_remove_file_correctly():
    with running_cockatiel() as proc:
        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=proc.port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        resp = requests.delete(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=proc.port),
        )
        assert resp.status_code == 200

        resp = requests.get(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=proc.port),
            content
        )
        assert resp.status_code == 404


def test_put_remove_conflict():
    with running_cockatiel() as proc:
        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=proc.port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        resp = requests.delete(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=proc.port),
        )
        assert resp.status_code == 200

        resp = requests.get(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=proc.port),
            content
        )
        assert resp.status_code == 404

        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=proc.port),
            content
        )
        assert resp.status_code == 409


def test_put_file_corrupted():
    with running_cockatiel() as proc:
        content = 'Hello, this is a testfile'.encode('utf-8')
        checksum = hashlib.sha1(content).hexdigest()
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=proc.port),
            'This is something else'.encode('utf-8'), headers={
                'X-Content-SHA1': checksum
            }
        )
        assert resp.status_code == 400
