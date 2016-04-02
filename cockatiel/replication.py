import string

from . import config
from .queue import FSQueue


def get_queue_for_node(node_url):
    prefix = "".join(c for c in node_url if c in string.ascii_letters or c in string.digits)
    return FSQueue(dirname=config.args.queue, prefix=prefix + '-')


def get_all_queues():
    nodes = config.args.node
    if not nodes:
        return []

    return [get_queue_for_node(n) for n in nodes]


def queue_operation(operation, filename):
    for queue in get_all_queues():
        queue.put({
            'operation': operation,
            'filename': filename
        })
