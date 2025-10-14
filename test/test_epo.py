# =============================================================================
# EPO databases tools tests
# =============================================================================
#

import os
import warnings
import pytest

from somecens.epo.tools import getMetadata

dir_path = os.path.dirname(os.path.realpath(__file__))
DBPATH = os.path.join(dir_path, "data", "test_belgium_2020.db")
COLUMNS = ['pseudo_id', 'location', 'screen_name']
NOTNULL = "location"


def test_getMetadata(dbpath=DBPATH, columns=COLUMNS):

    if os.path.exists(DBPATH):
        metadata = getMetadata(
            dbpath,
            columns=columns,
            not_null_column=NOTNULL)

        assert isinstance(metadata, list)
        assert len(metadata[0]) == len(COLUMNS)

        badpath = "qehfzefasashvze.db"
        with pytest.raises(Exception) as exc_info:
            getMetadata(badpath, columns)
        assert exc_info.value.args[0] == f"Unnable to find database at {badpath}"
    else:
        w = "Not testing getMetadata method from somecens.epo.tools beacuse of missing database at {DBPATH}"
        warnings.warn(w)

if __name__ == "__main__":
    test_getMetadata()
