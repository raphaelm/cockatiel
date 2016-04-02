import os.path


def generate_filename(oldname, checksum):
    head, tail = os.path.split(oldname)
    purename, ext = os.path.splitext(tail)
    if purename.endswith('_%s' % checksum):
        basename = '%s%s' % (purename, ext)
    else:
        basename = '%s_%s%s' % (purename, checksum, ext)
    return os.path.join(head, basename)
