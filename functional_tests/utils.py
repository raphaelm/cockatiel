import tempfile
from contextlib import contextmanager
from multiprocessing import Process

from cockatiel.server import run


portcounter = 18080


@contextmanager
def running_cockatiel(port=portcounter):
    global portcounter
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Process(target=run, args=('-p', str(port), '--storage', tmpdir))
        p.start()
        try:
            portcounter += 1
            yield port
        finally:
            p.terminate()
