import shutil
import socket
import tempfile
import time
from contextlib import contextmanager
from multiprocessing import Process

from cockatiel.server import run

portcounter = 18080


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
            yield port
        finally:
            p.terminate()


@contextmanager
def running_cockatiel_cluster(nodenum=2):
    global portcounter
    ports = list(range(portcounter, portcounter + nodenum))
    portcounter += nodenum

    processes = []
    tmpdirs = []

    for port in ports:
        qdir = tempfile.TemporaryDirectory().name
        tmpdirs.append(qdir)
        storagedir = tempfile.TemporaryDirectory().name
        tmpdirs.append(storagedir)

        args = ('-p', str(port), '--storage', storagedir, '--queue', qdir)
        p = Process(target=run, args=(args,))
        p.start()
        processes.append(p)

    for port in ports:
        while True:  # wait for server to come up
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', port))
                s.close()
                break
            except IOError:
                time.sleep(0.05)

    try:
        yield ports
    finally:
        for p in processes:
            p.terminate()

        for tmpdir in tmpdirs:
            shutil.rmtree(tmpdir)
