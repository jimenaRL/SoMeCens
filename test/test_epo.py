# =============================================================================
# EPO databases tools tests
# =============================================================================
#

import os
import pytest

from somecens.epo.tools import getMetadata

dir_path = os.path.dirname(os.path.realpath(__file__))
DBPATH = os.path.join(dir_path, "data", "test_belgium_2020.db")
COLUMNS = ['pseudo_id', 'location', 'screen_name']

def test_getMetadata(dbpath = DBPATH, columns = COLUMNS):

    metadata = getMetadata(dbpath, columns)
    assert type(metadata) == list
    assert len(metadata[0]) == len(COLUMNS)

    badpath = "qehfzefasashvze.db"
    with pytest.raises(Exception) as exc_info:
        getMetadata(badpath, columns)
    assert exc_info.value.args[0] == f"Unnable to find database at {badpath}"

if __name__ == "__main__":
    test_getMetadata()