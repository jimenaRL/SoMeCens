from __future__ import annotations
import os
import csv
import tempfile
import concurrent.futures
from subprocess import Popen, PIPE
from somecens.epo.conf import METADATAFIELDS

from fog.tokenizers import FingerprintTokenizer

def writeCsv(
    file: str,
    rows: Iterable[tuple],
    headers: Iterable[str] | None = None,
    verbose: bool = False):
    if not isinstance(headers, list):
        raise ValueError(
            f"Headers must be a list. Found {type(headers)} for '{headers}'.")
    with open(file, 'w') as f:
        writer =  csv.writer(f)
        if headers:
            writer.writerow(headers)
        writer.writerows(rows)
    if verbose:
        print(f"Csv file saved at {file}.")

def makeRegex(term: str) -> str:
    return f'\\b{term.rstrip().lstrip()}\\b'

def searchOccurrences(file_path: str, regex: str, search_col: str) -> Iterable[list]:
    """
    Use xan program to search for ocurrences of a regex at the csv file in path.
    Returns a list containig the rows of the csv file that match the term at the
    'search_col' column.
    """
    cmds = ['xan', 'search', '-s', search_col, '--ignore-case', '--regex', regex, file_path]
    p = Popen(cmds, stdout=PIPE)
    output = p.communicate()[0].decode()
    with tempfile.NamedTemporaryFile() as tmp:
        with open(tmp.name, 'w') as f:
            f.writelines(output)
        with open(tmp.name, 'r') as f:
            matchs = [l for l in csv.reader(f)]
    # remove headers and return
    return matchs[1:]

def matchUsersLocations(
    locations: dict,
    data: Iterable[list[str]],
    stopwords: list[str],
    split_characters: list[str],
    search_index: int,
    has_headers: bool = True) -> dict:
    """
    Search for ocurrences of terms in locations in the input data at search_index.
    Uses multithreaded instances of searchOccurrences method.

    Input locations is a dictionary of the form

        {code: location_name}

    Returns a dict of the form

        {code: rows of input data that matched terms}

    """
    msg = f"Searching location matchs for {len(locations)} terms, "
    msg += f"{len(data)} users. Usin stopwords {stopwords}"
    msg += f" and split characters {split_characters}."
    print(msg)

    # create tokenizer
    tokenizer = FingerprintTokenizer(stopwords=stopwords, split=split_characters)
    # for each tuple in data, normalize string at index using the tokenizer
    normalized = [list(d) + [' '.join(tokenizer(d[search_index]))] for d in data]
    with tempfile.NamedTemporaryFile()  as tmp:
        # write normalized data to tmp file
        if has_headers:
            headers = data[0] + ["normalized"]
            data = data[1:]
        else:
            headers = [str(j) for j in range(len(data[0]))] + ["normalized"]
        writeCsv(tmp.name, normalized, headers)
        # and launch multiple threads of searchOccurrences method
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    searchOccurrences,
                    tmp.name,
                    makeRegex(' '.join(tokenizer(locName))),
                    "normalized")
                for locName in locations.values()
            ]
            # and collect results
            results = [f.result() for f in futures]
    # format results as dict and return
    return {loc: res for loc, res in zip(locations.keys(), results)}

def searchMultipleOccurrences(file, regex_list, search_col):
    with tempfile.NamedTemporaryFile() as tmpRegex:
        with open(tmpRegex.name, 'w') as f:
            f.writelines('\n'.join(regex_list))
        commands = ['xan', 'search', '-s', search_col, '--ignore-case', '--regex', "--patterns", tmpRegex.name, file]
        p = Popen(commands, stdout=PIPE)
        output = p.communicate()[0].decode()

    with tempfile.NamedTemporaryFile() as tmp:
        with open(tmp.name, 'w') as f:
            f.writelines(output)
        with open(tmp.name, 'r') as f:
            matchs = [l for l in csv.reader(f)]

    # remove headers and return
    return matchs[1:]

def matchUsersMultipleLocations(
    locations_groups: dict,
    data: Iterable[list[str]],
    stopwords: list[str],
    split_characters: list[str],
    search_index: int,
    has_headers: bool = True
    ):
    """
    Search for ocurrences of terms in locations groups.
    Uses multithreaded instances of searchMultipleOccurrences method.

    Input locations_groups is a dictionary of the form

        {code: list_of_terms}

    Returns a dict of the form

        {code: rows of input data that matched terms}

    """

    msg = f"Searching location matchs for {len(locations_groups)} groups and "
    msg += f"{len(data)} users. Usin stopwords {stopwords}"
    msg += f" and split characters {split_characters}."
    print(msg)

    # create tokenizer
    tokenizer = FingerprintTokenizer(stopwords=stopwords, split=split_characters)
    # for each tuple in data, normalize string at index using the tokenizer
    normalized = [list(d) + [' '.join(tokenizer(d[search_index]))] for d in data]
    with tempfile.NamedTemporaryFile()  as tmp:
        # write normalized data to tmp file
        if has_headers:
            headers = data[0] + ["normalized"]
            data = data[1:]
        else:
            headers = [str(j) for j in range(len(data[0]))] + ["normalized"]
        writeCsv(tmp.name, normalized, headers)

        # launch multiple threads searching locations terms with xan
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    searchMultipleOccurrences,
                    tmp.name,
                    [makeRegex(' '.join(tokenizer(l))) for l in locations],
                    "normalized")
                for locations in locations_groups.values()
            ]
            # and collect results
            results = [f.result() for f in futures]
    # format results as dict and return
    return {loc: res for loc, res in zip(locations_groups.keys(), results)}
