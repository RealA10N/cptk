import pytest
from slugify import slugify
from .utils import EasyDirectory


@pytest.fixture
def tempdir(request, tmpdir_factory):
    name = slugify(request.node.nodeid)
    return EasyDirectory(tmpdir_factory.mktemp(name))
