import requests
import time

from functional_tests.utils import running_cockatiel_cluster


def test_put_propagation():
    with running_cockatiel_cluster() as ports:
        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=ports[0].port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        time.sleep(2)

        resp = requests.get(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=ports[1].port),
            content
        )
        assert resp.content == content
        assert resp.headers['Content-Type'] == 'text/plain'


def test_delete_propagation():
    with running_cockatiel_cluster() as ports:
        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=ports[0].port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        time.sleep(2)

        resp = requests.get(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=ports[1].port),
            content
        )
        assert resp.status_code == 200
        assert resp.content == content
        assert resp.headers['Content-Type'] == 'text/plain'

        resp = requests.delete(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=ports[1].port),
        )
        assert resp.status_code == 200

        time.sleep(2)

        resp = requests.delete(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=ports[0].port),
        )
        assert resp.status_code == 404
