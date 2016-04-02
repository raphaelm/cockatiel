import tempfile
from contextlib import contextmanager
from multiprocessing import Process

import time

from cockatiel.server import run


portcounter = 18080


@contextmanager
def running_cockatiel(port=None):
    global portcounter
    port = port or portcounter
    portcounter += 1
    with tempfile.TemporaryDirectory() as tmpdir:
        args = ('-p', str(port), '--storage', tmpdir)
        p = Process(target=run, args=(args,))
        p.start()
        time.sleep(1)
        try:
            yield port
        finally:
            p.terminate()
