import os.path


def generate_filename(oldname, checksum, timestamp):
    head, tail = os.path.split(oldname)
    purename, ext = os.path.splitext(tail)
    if purename.endswith('_%s_%s' % (timestamp, checksum)):
        basename = '%s%s' % (purename, ext)
    else:
        basename = '%s_%s_%s%s' % (purename, timestamp, checksum, ext)
    return os.path.join(head, basename)


def get_hash_from_name(name):
    if name.count('_') < 2:
        raise ValueError('No hash contained in filename')
    first, second, third = name.rsplit("_", 2)
    if '.' in third:
        hashsum, _ = third.split('.', 1)
    else:
        hashsum = third
    return hashsum


def get_timestamp_from_name(name):
    if name.count('_') < 2:
        raise ValueError('No timestamp contained in filename')
    first, second, third = name.rsplit("_", 2)
    return second
