import tempfile

from cockatiel.queue import FSQueue


def test_queue_order():
    with tempfile.TemporaryDirectory() as qdir:
        queue = FSQueue(dirname=qdir)
        queue.put({'test': 1})
        queue.put({'test': 2})
        queue.put({'test': 3})
        assert len(queue) == 3
        assert queue.get()[1]['test'] == 1
        assert queue.get()[1]['test'] == 2
        assert queue.get()[1]['test'] == 3
        assert queue.get() is None


def test_queue_delete():
    with tempfile.TemporaryDirectory() as qdir:
        queue = FSQueue(dirname=qdir)
        queue.put({'test': 1})
        queue.put({'test': 2})
        assert len(queue) == 2
        oid, obj = queue.get(delete=False)
        assert obj['test'] == 1
        assert queue.get(delete=False)[1]['test'] == 1
        queue.delete(oid)
        assert queue.get(delete=False)[1]['test'] == 2


def test_queue_prefixes():
    with tempfile.TemporaryDirectory() as qdir:
        queue = FSQueue(dirname=qdir, prefix='abc')
        queue2 = FSQueue(dirname=qdir, prefix='def')
        queue.put({'test': 1})
        queue.put({'test': 2})
        queue.put({'test': 3})
        queue2.put({'test': 4})
        assert len(queue) == 3
        assert queue2.get()[1]['test'] == 4
        assert queue2.get() is None
        assert queue.get()[1]['test'] == 1
        assert queue.get()[1]['test'] == 2
        assert queue.get()[1]['test'] == 3
        assert queue.get() is None
