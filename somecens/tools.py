import os
import csv
import tempfile
import concurrent.futures
from subprocess import Popen, PIPE
from somecens.epo.conf import METADATAFIELDS

from fog.tokenizers import FingerprintTokenizer

def writeCsv(file, rows, headers=None, verbose=False):
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

def searchOccurrences(file, term, search_col):
    cmds = ['xan', 'search', '-s', search_col, '--ignore-case', '--regex', term, file]
    p = Popen(cmds, stdout=PIPE)
    output = p.communicate()[0].decode()
    with tempfile.NamedTemporaryFile() as tmp:
        with open(tmp.name, 'w') as f:
            f.writelines(output)
        with open(tmp.name, 'r') as f:
            matchs = [l for l in csv.reader(f)][1:]
    return matchs

def regexMatchUsersLocations(locations, metadata, stopwords, search_index):
    tokenizer = FingerprintTokenizer(stopwords=stopwords)
    nb_cols = len(metadata[0])
    headers = list(map(str, range(nb_cols))) + ["normalized"]
    normalized_metadata = [list(m) + [' '.join(tokenizer(m[search_index]))] for m in metadata]
    with tempfile.NamedTemporaryFile()  as tmp:
        # write normalized metadata to tmp file
        writeCsv(tmp.name, normalized_metadata, headers)
        # launch multiple threads searching terms with xan
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(searchOccurrences, tmp.name, makeRegex(' '.join(tokenizer(locName))), "normalized")
                for locName in locations.values()
            ]
            # and collect results
            results = [f.result() for f in futures]
    # format results as dict and return
    return {loc: res for loc, res in zip(locations.keys(), results)}

def searchMultipleOccurrences(file, terms, search_col):
    with tempfile.NamedTemporaryFile() as tmpTerms:
        regexs = [r for r in map(makeRegex, terms)]
        with open(tmpTerms.name, 'w') as f:
            f.writelines('\n'.join(regexs))
        commands = ['xan', 'search', '-s', search_col, '--ignore-case', '--regex', "--patterns", tmpTerms.name, file]
        p = Popen(commands, stdout=PIPE)
        output = p.communicate()[0].decode()

    with tempfile.NamedTemporaryFile() as tmp:
        with open(tmp.name, 'w') as f:
            f.writelines(output)
        with open(tmp.name, 'r') as f:
            matchs = [l for l in csv.reader(f)][1:]
    return matchs

def regexMatchUsersMultipleLocations(locations_groups, metadata, stopwords, search_index):
    tokenizer = FingerprintTokenizer(stopwords=stopwords)
    nb_cols = len(metadata[0])
    headers = list(map(str, range(nb_cols))) + ["normalized"]
    normalized_metadata = [list(m) + [' '.join(tokenizer(m[search_index]))] for m in metadata]
    with tempfile.NamedTemporaryFile()  as tmp:
        # write metadata to tmp file
        writeCsv(tmp.name, normalized_metadata, headers=headers)
        # launch multiple threads searching locations terms with xan
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(searchMultipleOccurrences, tmp.name, locations, "normalized")
                for locations in locations_groups.values()
            ]
            # and collect results
            results = [f.result() for f in futures]
        # format results as dict
        results = {loc: res for loc, res in zip(locations_groups.keys(), results)}
    return results


def matchUsersLocations(locations, metadata, stopwords, search_index, method='regex'):
    if method == 'regex':
        print(f"Searching users location matchs for {method} method with stopwords {stopwords} ...")
        return regexMatchUsersLocations(locations, metadata, stopwords, search_index)
    else:
        raise  ValueError(f'NOT IMPLEMENTED METHOD {method}')

def matchUsersMultipleLocations(locations_groups, metadata, stopwords, search_index, method='exact'):
    if method == 'regex':
        print(f"Searching multiple users locations matchs for {method} method ...")
        return regexMatchUsersMultipleLocations(locations_groups, metadata, stopwords, search_index)
    else:
        raise  ValueError(f'NOT IMPLEMENTED METHOD {method}')
