import os
import shutil
import socket
import tempfile
import time
from collections import namedtuple
from contextlib import contextmanager
from multiprocessing import Process

from cockatiel.server import run

portcounter = 18080

TestProcess = namedtuple('TestProcess', (
    'port', 'tmpdir', 'queuedir', 'process'
))


@contextmanager
def running_cockatiel(port=None):
    global portcounter
    port = port or portcounter
    portcounter += 1
    with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as qdir:
        args = ('-p', str(port), '--storage', tmpdir, '--queue', qdir)
        p = Process(target=run, args=(args,))
        p.start()
        while True:  # wait for server to come up
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', port))
                s.close()
                break
            except IOError:
                time.sleep(0.05)
        try:
            yield TestProcess(port=port, tmpdir=tmpdir, queuedir=qdir, process=p)
        finally:
            p.terminate()


@contextmanager
def running_cockatiel_cluster(nodenum=2):
    global portcounter

    processes = []
    for port in range(portcounter, portcounter + nodenum):
        qdir = tempfile.TemporaryDirectory()
        storagedir = tempfile.TemporaryDirectory()

        args = ['-p', str(port), '--storage', storagedir.name, '--queue', qdir.name]
        for p in range(portcounter, portcounter + nodenum):
            if p != port:
                args.append('--node')
                args.append('http://localhost:{}'.format(p))

        p = Process(target=run, args=(args,))
        p.start()
        processes.append(TestProcess(port=port, tmpdir=storagedir.name, queuedir=qdir.name, process=p))

    portcounter += nodenum

    for proc in processes:
        while True:  # wait for server to come up
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', proc.port))
                s.close()
                break
            except IOError:
                time.sleep(0.05)

    try:
        yield processes
    finally:
        for p in processes:
            p.process.terminate()
