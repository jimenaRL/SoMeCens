from __future__ import annotations

import os
import tempfile
import sqlite3
import pandas as pd
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
    not_null_column: str | None = None,
    columns: Iterable[str] | None = None,
    ids_dbpath: str | None = None
) -> list(tuple):

    if not os.path.exists(dbpath):
        raise ValueError(f"Unnable to find database at {dbpath}")

    if not columns:
        columns = METADATAFIELDS

    joinedColumns = ','.join(columns)
    query = f"SELECT {joinedColumns} FROM {METADATATABLE} "

    if not_null_column:
        query += f"WHERE {not_null_column} IS NOT NULL "

    with sqlite3.connect(dbpath) as con:
        cur = con.cursor()
        cur.execute(query)
        res = cur.fetchall()

    msg = f"Found {len(res)} rows in metadata with columns {joinedColumns}"
    if not_null_column:
        msg += f" and {not_null_column} NOT NULL"
    print(msg)

    if ids_dbpath:
        with sqlite3.connect(ids_dbpath) as con:
            cur = con.cursor()
            cur.execute("SELECT twitter_id,pseudo_id from lut")
            ids = cur.fetchall()

    l1 = len(res)
    res = pd.DataFrame(data=res, columns=columns, dtype=str) \
        .merge(
            pd.DataFrame(data=ids, columns=["twitter_id","pseudo_id"], dtype=str),
            on="pseudo_id")
    assert l1 == len(res)

    return res.drop(columns=["pseudo_id"])[['twitter_id', 'location', 'screen_name']].to_numpy()
