import tempfile

import pytest
import requests

from . import utils


def test_put_propagation():
    with utils.running_cockatiel_cluster(nodenum=3) as procs:
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

            resp = requests.get(
                'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[2].port),
                content
            )
            assert resp.status_code == 200
            assert resp.content == content
            assert resp.headers['Content-Type'] == 'text/plain'

        utils.waitfor(get)


def test_delete_propagation():
    with utils.running_cockatiel_cluster() as procs:
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

        utils.waitfor(check_arrived)

        resp = requests.delete(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[1].port),
        )
        assert resp.status_code == 200

        def check_deleted():
            resp = requests.get(
                'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[0].port),
            )
            assert resp.status_code == 404

        utils.waitfor(check_deleted)


def test_recover_put_from_missing_server():
    with utils.running_cockatiel_cluster() as procs:
        # Kill one of the servers
        procs[1].process.terminate()

        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=procs[0].port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        with pytest.raises(IOError):
            # Assert that the server is actually down
            requests.get('http://127.0.0.1:{port}{path}'.format(path=path, port=procs[1].port))

        # Re-create the killed server
        procs.recreate_process(procs[1])

        def get():
            resp = requests.get(
                'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[1].port)
            )
            assert resp.status_code == 200
            assert resp.content == content
            assert resp.headers['Content-Type'] == 'text/plain'

        utils.waitfor(get)


def test_partial_network_failure():
    """
    This test assumes that we have three nodes (A, B and C). We will simulate
    that the network between A and C is broken, such that A can only talk to
    B, B can talk to both of them and C can only talk to A. We then push a
    file to A, that should eventually also appear on C.

    We will simulate this condition very naively by just removing the unwanted
    connection from the configuration.
    """
    processes = utils.ProcessManager()
    for i in range(3):
        port = utils.portcounter + i
        qdir = tempfile.TemporaryDirectory()
        storagedir = tempfile.TemporaryDirectory()

        args = ['-p', str(port), '--storage', storagedir.name, '--queue', qdir.name]

        if i > 0:
            args.append('--node')
            args.append('http://localhost:{}'.format(port - 1))
        if i < 2:
            args.append('--node')
            args.append('http://localhost:{}'.format(port + 1))

        p = utils.Process(target=utils.run, args=(args,))
        p.start()
        processes.append(
            utils.TestProcess(port=port, tmpdir=storagedir.name, queuedir=qdir.name, process=p,
                              args=args)
        )

    utils.portcounter += 3
    processes.wait_for_up()

    try:
        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=processes[0].port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        def get():
            resp = requests.get(
                'http://127.0.0.1:{port}{path}'.format(path=path, port=processes[1].port),
                content
            )
            assert resp.status_code == 200
            assert resp.content == content
            assert resp.headers['Content-Type'] == 'text/plain'

            resp = requests.get(
                'http://127.0.0.1:{port}{path}'.format(path=path, port=processes[2].port),
                content
            )
            assert resp.status_code == 200
            assert resp.content == content
            assert resp.headers['Content-Type'] == 'text/plain'

        utils.waitfor(get)
    finally:
        processes.terminate()
