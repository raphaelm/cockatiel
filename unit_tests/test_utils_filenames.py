from cockatiel.utils.filenames import generate_filename


def test_filename_checksum():
    assert generate_filename('foo/bar/baz.html', 'abcdefghijk12345') == 'foo/bar/baz_abcdefghijk12345.html'
    assert generate_filename('foo/bar/baz', 'abcdefghijk12345') == 'foo/bar/baz_abcdefghijk12345'
