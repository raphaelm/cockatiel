import tempfile

from cockatiel.dellog import DeletionLog


def test_log_operations():
    with tempfile.NamedTemporaryFile() as f:
        log = DeletionLog(f.name)
        log.put('foo')
        log.put('bar')
        assert 'foo' in log
        assert 'bar' in log
        assert 'baz' not in log


def test_log_persistence():
    with tempfile.NamedTemporaryFile() as f:
        log = DeletionLog(f.name)
        log.put('foo')
        assert 'foo' in log

        log2 = DeletionLog(f.name)
        assert 'foo' in log2
