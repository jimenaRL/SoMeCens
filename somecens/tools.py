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

def searchOccurrences(
    file: str,
    regex: str | list(str),
    search_col: str,
    banned_words: list(str) = []) -> Iterable[list]:
    """
    Use xan program to search for ocurrences of a regex (or list of regex) at
    the csv file in path. Returns a list containig the rows of the csv file
    that match the term at the 'search_col' column.
    """

    # if needed convert string regex to list
    if isinstance(regex, str):
        regex = [regex]

    # write down regex list to a tmp file to be used by xan
    with tempfile.NamedTemporaryFile() as tmpRegex:
        with open(tmpRegex.name, 'w') as f:
            f.writelines('\n'.join(regex))
        # perform search with xan
        commands = ['xan', 'search', '-s', search_col, '--ignore-case', '--regex', "--patterns", tmpRegex.name, file]
        p = Popen(commands, stdout=PIPE)
        # and capture string output
        output = p.communicate()[0].decode()

    # # write down output to file and read it again
    # with tempfile.NamedTemporaryFile() as tmp:
    #     with open(tmp.name, 'w') as f:
    #         f.writelines(output)
    #     with open(tmp.name, 'r') as f:
    #         matchs = [l for l in csv.reader(f)]

    # parse output
    matchs = list(csv.reader(output[:-1].split("\n")))

    # remove headers and return
    return matchs[1:]

def matchUsersLocations(
    locations: dict,
    data: Iterable[list[str]],
    stopwords: list[str],
    split_characters: list[str],
    search_index: int,
    banned_words: list[str] = [],
    has_headers: bool = True
    ):
    """
    Search for ocurrences of terms in locations groups.
    Uses multithreaded instances of searchMultipleOccurrences method.

    Input locations is a dictionary of the form

        {code: term} or {code: [term_1, ..., term_N]}

    Returns a dict of the form

        {code: rows of input data that matched terms}

    """

    msg = f"Searching location matchs for {len(locations)} groups and "
    msg += f"{len(data)} users. Usin stopwords {stopwords}"
    msg += f" and split characters {split_characters}."
    print(msg)

    # if needed convert values of dict from string to list
    for code, value in locations.items():
        if isinstance(value, str):
            locations[code] = [value]

    # create tokenizer
    tokenizer = FingerprintTokenizer(stopwords=stopwords, split=split_characters)

    # for each tuple in data, normalize string at index using the tokenizer
    normalized = [list(d) + [' '.join(tokenizer(d[search_index]))] for d in data]

    # write normalized data to a tmp file to be used by the search method
    with tempfile.NamedTemporaryFile()  as tmp:
        if has_headers:
            headers = data[0] + ["normalized"]
            data = data[1:]
        else:
            headers = [str(j) for j in range(len(data[0]))] + ["normalized"]
        writeCsv(tmp.name, normalized, headers)

        # launch multiple threads searching for terms
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    searchOccurrences,
                    tmp.name,
                    [makeRegex(' '.join(tokenizer(l))) for l in locations],
                    "normalized")
                for locations in locations.values()
            ]
            # and collect results
            results = [f.result() for f in futures]
    # format results as dict and return
    return {loc: res for loc, res in zip(locations.keys(), results)}
