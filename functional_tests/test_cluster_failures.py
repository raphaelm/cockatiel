import tempfile

import multiprocessing

import aiohttp
import requests
import time

from functional_tests import utils_proxy
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


def test_do_not_accept_corrupted_file():
    """
    Normally, the propagation of a file causes 2 replication requests, as tested by
    test_proxy_propagation. This proxy corrupts the data in the first three requests,
    then stops corrupting. As we expect the system to detect the corruption and
    re-try the request, we'll expect to end up with X replication requests. Also, we
    of course check that it arrived correctly.
    """
    class CorruptingProxy(utils_proxy.ProxyRequestHandler):
        cnt = multiprocessing.Value('i', 0)

        def intercept_request(self, message, data):
            with self.cnt.get_lock():
                if self.cnt.value < 3:
                    self.logger.info('Performing corruption')
                    if data:
                        data = data.replace(b"a", b"b")
                self.cnt.value += 1
            return message, data

    with utils.running_cockatiel_cluster(proxy=CorruptingProxy) as procs:
        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=procs[0].port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        def check_arrived():
            resp = requests.get(
                'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[1].port)
            )
            assert resp.status_code == 200
            assert resp.content == content
            assert resp.headers['Content-Type'] == 'text/plain'

        utils.waitfor(check_arrived)

    assert CorruptingProxy.cnt.value > 3


def test_interrupted_transfer():
    """
    Normally, the propagation of a file causes 2 replication requests, as tested by
    test_proxy_propagation. This proxy interrupts the request in flight the first
    few times. As we expect the system to detect the corruption and re-try the request,
    we'll expect to end up with X replication requests. Also, we of course check that
    it arrived correctly.
    """
    class InterruptingProxy(utils_proxy.ProxyRequestHandler):
        cnt = multiprocessing.Value('i', 0)

        def intercept_request(self, message, data):
            with self.cnt.get_lock():
                self.cnt.value += 1
                if self.cnt.value < 3:
                    self.writer.close()
                    return None, None
            return message, data

    with utils.running_cockatiel_cluster(proxy=InterruptingProxy) as procs:
        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=procs[0].port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        def check_arrived():
            resp = requests.get(
                'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[1].port)
            )
            assert resp.status_code == 200
            assert resp.content == content
            assert resp.headers['Content-Type'] == 'text/plain'

        utils.waitfor(check_arrived)

    assert InterruptingProxy.cnt.value >= 3


def test_transfer_timeout():
    """
    This delays the first replication by 40 seconds to trigger a timeout
    """
    class DelayingProxy(utils_proxy.ProxyRequestHandler):
        cnt = multiprocessing.Value('i', 0)

        def intercept_request(self, message, data):
            with self.cnt.get_lock():
                self.cnt.value += 1
                if self.cnt.value < 2:
                    time.sleep(40)
            return message, data

    with utils.running_cockatiel_cluster(proxy=DelayingProxy) as procs:
        content = 'Hello, this is a testfile'.encode('utf-8')
        resp = requests.put(
            'http://127.0.0.1:{port}{path}'.format(path='/foo/bar.txt', port=procs[0].port),
            content
        )
        assert resp.status_code == 201
        path = resp.headers['Location']

        def check_arrived():
            resp = requests.get(
                'http://127.0.0.1:{port}{path}'.format(path=path, port=procs[1].port)
            )
            assert resp.status_code == 200
            assert resp.content == content
            assert resp.headers['Content-Type'] == 'text/plain'

        utils.waitfor(check_arrived, timeout=60)

    assert DelayingProxy.cnt.value >= 2
