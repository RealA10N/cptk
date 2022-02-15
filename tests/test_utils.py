import os

from .utils import EasyDirectory


def test_find_tree_files(tempdir: EasyDirectory):
    from cptk.utils import find_tree_files

    tempdir.create('', 'a', 'b', 'c.txt')
    tempdir.create('', 'a', 'b.txt')
    tempdir.create('', 'a.txt')
    os.mkdir(tempdir.join('emptydir'))

    res = set(find_tree_files(tempdir.path))
    assert res == {tempdir.join(a) for a in {'a/b/c.txt', 'a/b.txt', 'a.txt'}}


def test_find_common_files(tempdir: EasyDirectory):
    from cptk.utils import find_common_files

    os.makedirs(tempdir.join('a', 'a'))
    tempdir.create('', 'a/b/c.txt')
    tempdir.create('', 'b/b/c.txt')

    tempdir.create('', 'a/a.txt')
    tempdir.create('', 'b/b.txt')

    tempdir.create('text a', 'a/t.txt')
    tempdir.create('text b', 'b/t.txt')

    res = set(find_common_files(tempdir.join('a'), tempdir.join('b')))
    assert res == {'b/c.txt', 't.txt'}
