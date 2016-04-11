import socket
import tempfile
import time
from collections import namedtuple
from contextlib import contextmanager
from multiprocessing import Process

import pytest
import requests

from cockatiel.server import run

TestProcess = namedtuple('TestProcess', (
    'port', 'tmpdir', 'queuedir', 'process', 'args'
))


class ProcessManager:
    def __init__(self):
        self.processes = []

    def append(self, process):
        self.processes.append(process)

    def __getitem__(self, item):
        return self.processes[item]

    def terminate(self):
        for p in self.processes:
            if p.process.is_alive():
                p.process.terminate()

    def add(self, port, tmpdir, queuedir, args):
        p = Process(target=run, args=(args,))
        p.start()

        def up():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', port))
            s.close()

        p = TestProcess(port=port, tmpdir=tmpdir, queuedir=queuedir, process=p,
                        args=args)
        self.append(p)
        return p

    def recreate_process(self, oldproc):
        return self.add(oldproc.port, oldproc.tmpdir, oldproc.queuedir, oldproc.args)

    def wait_for_up(self):
        for p in self.processes:
            def up():
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', p.port))
                s.close()

            waitfor(up, interval=.05)


def get_free_ports(num=1):
    ports = []
    socks = []
    for i in range(num):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        ports.append(s.getsockname()[1])
        socks.append(s)
    for s in socks:
        s.close()
    return ports


@contextmanager
def running_cockatiel(port=None):
    port = port or get_free_ports()[0]
    with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as qdir:
        args = ('-p', str(port), '--storage', tmpdir, '--queue', qdir)
        p = Process(target=run, args=(args,))
        p.start()

        def up():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', port))
            s.close()

        waitfor(up, interval=.05)

        try:
            yield TestProcess(port=port, tmpdir=tmpdir, queuedir=qdir, process=p, args=args)
        finally:
            p.terminate()


@contextmanager
def running_cockatiel_cluster(nodenum=2):
    processes = ProcessManager()
    portnums = get_free_ports(nodenum)
    for i in range(nodenum):
        qdir = tempfile.TemporaryDirectory()
        storagedir = tempfile.TemporaryDirectory()
        port = portnums[i]

        args = ['-p', str(port), '--storage', storagedir.name, '--queue', qdir.name]
        for p in portnums:
            if p != port:
                args.append('--node')
                args.append('http://127.0.0.1:{}'.format(p))

        p = Process(target=run, args=(args,))
        p.start()
        processes.append(
            TestProcess(port=port, tmpdir=storagedir.name, queuedir=qdir.name, process=p,
                        args=args)
        )

    processes.wait_for_up()

    try:
        yield processes
    finally:
        processes.terminate()


def waitfor(func, timeout=10, interval=0.5):
    started = time.time()
    while True:
        try:
            func()
            break
        except:
            if time.time() - started >= timeout:
                raise
            else:
                time.sleep(interval)


def is_down(port):
    def f():
        with pytest.raises(IOError):
            # Assert that the server is actually down
            requests.get('http://127.0.0.1:{port}/_status'.format(port=port))
    return f


def is_up(port):
    def f():
        requests.get('http://127.0.0.1:{port}/_status'.format(port=port))
    return f


def queues_empty(port):
    def f():
        resp = requests.get('http://127.0.0.1:{port}/_status'.format(port=port))
        assert all(v['length'] == 0 for v in resp.json()['queues'].values())
    return f
