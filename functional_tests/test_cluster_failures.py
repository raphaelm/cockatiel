import tempfile

import pytest
import requests

from . import utils


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
    portnums = utils.get_free_ports(3)
    for i in range(3):
        qdir = tempfile.TemporaryDirectory()
        storagedir = tempfile.TemporaryDirectory()
        port = portnums[i]

        args = ['-p', str(port), '--storage', storagedir.name, '--queue', qdir.name]

        if i > 0:
            args.append('--node')
            args.append('http://127.0.0.1:{}'.format(portnums[i - 1]))
        if i < 2:
            args.append('--node')
            args.append('http://127.0.0.1:{}'.format(portnums[i + 1]))

        p = utils.Process(target=utils.run, args=(args,))
        p.start()
        processes.append(
            utils.TestProcess(port=port, tmpdir=storagedir.name, queuedir=qdir.name, process=p,
                              args=args)
        )

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


def test_recover_put_from_missing_server():
    with utils.running_cockatiel_cluster() as procs:
        # Kill one of the servers
        procs[1].process.terminate()

        utils.waitfor(utils.is_down(procs[1].port))

        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=procs[0].port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        resp = requests.get('http://127.0.0.1:{port}/_status'.format(port=procs[0].port))
        respdata = resp.json()
        assert respdata['queues']['http://127.0.0.1:{port}'.format(port=procs[1].port)]['length'] == 1

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


def test_issue9_hanging_deletion():
    """
    Scenario:

    * User uploads file to node A, does not get replicated to B because of network issues
    * User sends DELETE command to B, B does not do anyting because it does not know the file
    * Network issues are resolved, file is transferred from A to B and now present on every node,
      even though it should be deleted.
    """
    with utils.running_cockatiel_cluster() as procs:
        # Kill one of the servers
        procs[1].process.terminate()
        utils.waitfor(utils.is_down(procs[1].port))

        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=procs[0].port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        procs[0].process.terminate()
        utils.waitfor(utils.is_down(procs[0].port))
        procs.recreate_process(procs[1])
        utils.waitfor(utils.is_up(procs[1].port))

        resp = requests.delete(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[1].port),
        )
        assert resp.status_code == 404

        procs.recreate_process(procs[0])
        utils.waitfor(utils.is_up(procs[0].port))
        utils.waitfor(utils.queues_empty(procs[0].port))
        utils.waitfor(utils.queues_empty(procs[1].port))

        resp = requests.get(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[0].port),
        )
        assert resp.status_code == 404

        resp = requests.get(
            'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[1].port),
        )
        assert resp.status_code == 404
