import os.path


def generate_filename(oldname, checksum):
    head, tail = os.path.split(oldname)
    purename, ext = os.path.splitext(tail)
    if purename.endswith('_%s' % checksum):
        basename = '%s%s' % (purename, ext)
    else:
        basename = '%s_%s%s' % (purename, checksum, ext)
    return os.path.join(head, basename)


def get_hash_from_name(name):
    if '_' not in name:
        raise ValueError('No hash contained in filename')
    first, second = name.split("_", 1)
    if '.' in second:
        hashsum, _ = second.split('.', 1)
    else:
        hashsum = second
    return hashsum
