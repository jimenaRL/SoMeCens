from __future__ import annotations

import os
import sqlite3
from glob import glob
from string import Template

from somecens.epo.conf import METADATAFIELDS, METADATATABLE

def getLastRelease(pathPattern: str, db: str, country: str, year: int) -> str:
    path = Template(pathPattern).substitute(db=db, country=country, year=year)
    canditates_paths = glob(path)
    if len(canditates_paths) == 0:
        raise ValueError(f"No canditate paths found at {path}.")
    canditates_paths.sort()
    last_release_path = canditates_paths[-1]
    print(f"Found last release at {last_release_path}.")
    return last_release_path

def getMetadata(
        dbpath: str,
        limit: int | None = None,
        not_null: str | None = None,
        columns:  Iterable[str] | None = None) -> list(tuple):
    if not os.path.exists(dbpath):
        raise ValueError(f"Unnable to find database at {dbpath}")
    if not columns:
        columns = METADATAFIELDS
    joinedColumns = ','.join(columns)
    query = f"SELECT {joinedColumns} FROM {METADATATABLE} "
    if not_null:
        query += f"WHERE {not_null} IS NOT NULL "
    if limit:
        query += f"LIMIT {limit} "
    with sqlite3.connect(dbpath) as con:
        cur = con.cursor()
        cur.execute(query)
        res = cur.fetchall()

    msg = f"Found {len(res)} rows in metadata with columns {joinedColumns}"
    if not_null:
        msg += f" and not NULL column {not_null}"
    print(msg)
    return res
