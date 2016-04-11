from cockatiel.utils.filenames import generate_filename, get_hash_from_name


def test_filename_checksum():
    assert generate_filename('foo/bar/baz.html', 'abcdefghijk12345', 13) == 'foo/bar/baz_13_abcdefghijk12345.html'
    assert generate_filename('foo/bar/baz', 'abcdefghijk12345', 13) == 'foo/bar/baz_13_abcdefghijk12345'
    assert generate_filename(
        'foo/bar/baz_13_abcdefghijk12345.html', 'abcdefghijk12345', 13) == 'foo/bar/baz_13_abcdefghijk12345.html'


def test_get_hash_from_name():
    assert get_hash_from_name('foo/bar/baz_13_abc12345.html') == 'abc12345'
    assert get_hash_from_name('foo/bar/baz_13_abc12345') == 'abc12345'
