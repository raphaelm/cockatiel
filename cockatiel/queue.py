import json
import os

import time


class FSQueue:
    """
    Implements a persistent, time-based queue that uses the filesystem as its storage.
    It can take any objects that can be serialized to JSON.

    It is safe to fill in data into the queue from multiple threads, however you
    should only get items from the queue from one thread at a time!
    """

    def __init__(self, dirname, prefix='qe-'):
        self.dirname = dirname
        self.prefix = prefix
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def put(self, obj):
        """
        Puts an element into the queue.

        :param obj: The object to put into the queue. Needs to be serializable by
                    the standard library's json module.
        """
        while True:
            timestamp = int(time.time() * 1000000)
            fpath = os.path.join(self.dirname, '{prefix}{time}'.format(
                prefix=self.prefix, time=timestamp))
            try:
                with open(fpath, 'x') as f:
                    json.dump(obj, f)
            except FileExistsError:
                continue
            else:
                break

    def get(self, delete=True):
        """
        Gets the first element from the queue but.

        :param delete: Whether or not to remove the item from the queue.
        :returns: A tuple consisting of an element ID and the element itself.
                  Returns None instead if the queue is empty.
        """
        el = self._ordered_elements
        if not el:
            return None

        fpath = os.path.join(self.dirname, el[0])
        with open(fpath, 'r') as f:
            obj = json.load(f)

        if delete:
            self.delete(el[0])

        return el[0], obj

    def delete(self, itemid):
        """
        Removes the item with the given ID from the queue.
        """
        fpath = os.path.join(self.dirname, itemid)
        os.remove(fpath)

    def __len__(self):
        return len(self._unordered_elements)

    @property
    def _unordered_elements(self):
        return [f for f in os.listdir(self.dirname) if f.startswith(self.prefix)]

    @property
    def _ordered_elements(self):
        return sorted(self._unordered_elements, key=lambda f: int(f[len(self.prefix):]))
