import time

import requests

from functional_tests.utils import running_cockatiel_cluster, waitfor


def test_put_propagation():
    with running_cockatiel_cluster() as procs:
        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=procs[0].port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        def get():
            resp = requests.get(
                'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[1].port),
                content
            )
            assert resp.status_code == 200
            assert resp.content == content
            assert resp.headers['Content-Type'] == 'text/plain'

        waitfor(get)


def test_delete_propagation():
    with running_cockatiel_cluster() as procs:
        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=procs[0].port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        def check_arrived():
            resp = requests.get(
                'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[1].port),
                content
            )
            assert resp.status_code == 200
            assert resp.content == content
            assert resp.headers['Content-Type'] == 'text/plain'

        waitfor(check_arrived)

        resp = requests.delete(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[1].port),
        )
        assert resp.status_code == 200

        def check_deleted():
            resp = requests.get(
                'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[0].port),
            )
            assert resp.status_code == 404

        waitfor(check_deleted)


def test_recover_put_from_missing_server():
    with running_cockatiel_cluster() as procs:
        procs[1].process.terminate()

        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=procs[0].port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        time.sleep(1)
        procs.recreate_process(procs[1])

        def get():
            resp = requests.get(
                'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[1].port),
                content
            )
            assert resp.status_code == 200
            assert resp.content == content
            assert resp.headers['Content-Type'] == 'text/plain'

        waitfor(get)
