import os


class DeletionLog:
    """
    Implements a persistent log that is used for file names that are known to be
    deleted.
    """

    def __init__(self, filename):
        self.filename = filename
        self.cache = self._load()

    def _load(self):
        s = set()
        if not os.path.exists(self.filename):
            with open(self.filename, 'w'):
                pass  # Just create it
        else:
            with open(self.filename) as f:
                for line in f:
                    s.add(line.strip())
        return s

    def put(self, obj):
        """
        Puts an element into the log.

        :param obj: The string to put into the log.
        """
        if obj in self.cache:
            return
        self.cache.add(obj)
        with open(self.filename, mode='a') as f:
            f.write(obj + '\n')

    def __len__(self):
        return len(self.cache)

    def __contains__(self, item):
        return item in self.cache
