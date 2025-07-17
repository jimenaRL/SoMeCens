from __future__ import annotations

import os
import sqlite3
from glob import glob
from string import Template

from somecens.epo.conf import METADATAFIELDS, METADATATABLE

def getLastRelease(pathPattern: str, db: str, country: str, year: int):
    path = Template(pathPattern).substitute(db=db, country=country, year=year)
    canditates_paths = glob(path)
    if len(canditates_paths) == 0:
        raise ValueError(f"No canditate paths found at {path}.")
    canditates_paths.sort()
    last_release_path = canditates_paths[-1]
    print(f"Found last release at {last_release_path}.")
    return last_release_path

def getMetadata(dbpath: str, columns:  Iterable[str] | None = None):
    if not os.path.exists(dbpath):
        raise ValueError(f"Unnable to find database at {dbpath}")
    if not columns:
        columns = METADATAFIELDS
    joinedColumns = ','.join(columns)
    query = f"SELECT {joinedColumns} FROM {METADATATABLE}"
    with sqlite3.connect(dbpath) as con:
        cur = con.cursor()
        cur.execute(query)
        res = cur.fetchall()
    print(f"Found {len(res)} rows in metadata with columns {joinedColumns}.")
    return res
