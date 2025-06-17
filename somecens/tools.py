import csv
import tempfile
import concurrent.futures
from subprocess import Popen, PIPE
from somecens.epo.conf import METADATAFIELDS


def writeCsv(file, rows, headers=None, verbose=False):
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
    commands = ['xan', 'search', '-s', search_col, '--ignore-case', '--regex', makeRegex(term), file]
    p = Popen(commands, stdout=PIPE)
    output = p.communicate()[0].decode()
    with tempfile.NamedTemporaryFile() as tmp:
        with open(tmp.name, 'w') as f:
            f.writelines(output)
        with open(tmp.name, 'r') as f:
            matchs = [l for l in csv.reader(f)][1:]
    return matchs

def regexMatchUsersLocations(locations, metadata, headers, search_col='location'):
    with tempfile.NamedTemporaryFile()  as tmp:
        # write metadata to tmp file
        writeCsv(tmp.name, metadata, headers=headers)
        # launch multiple threads searching locations terms with xan
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(searchOccurrences, tmp.name, locName, search_col)
                for locName in locations.values()
            ]
            # and collect results
            results = [f.result() for f in futures]
        # format results as dict
        results = {loc: res for loc, res in zip(locations, results)}
    return results


def matchUsersLocations(locations, metadata, headers, search_col='location', method='regex'):
    if method == 'regex':
        print(f"Searching users location matchs for {method} method ...")
        return regexMatchUsersLocations(locations, metadata, headers, search_col)
    else:
        raise  ValueError(f'NOT IMPLEMENTED METHOD {method}')

def searchMultipleOccurrences(file, terms, search_col):
    with tempfile.NamedTemporaryFile() as tmpTerms:
        regexs = [r for r in map(makeRegex, terms)]
        with open(tmpTerms.name, 'w') as f:
            f.writelines('\n'.join(regexs))
        commands = ['xan', 'search', '-s', search_col, '--ignore-case', '--regex', "--patterns", tmpTerms.name, file]
        print(' '.join(commands))
        p = Popen(commands, stdout=PIPE)
        output = p.communicate()[0].decode()

    with tempfile.NamedTemporaryFile() as tmp:
        with open(tmp.name, 'w') as f:
            f.writelines(output)
        with open(tmp.name, 'r') as f:
            matchs = [l for l in csv.reader(f)][1:]
    return matchs

def regexMatchUsersMultipleLocations(locations_groups, metadata, headers, search_col='location'):
    with tempfile.NamedTemporaryFile()  as tmp:
        # write metadata to tmp file
        writeCsv(tmp.name, metadata, headers=headers)
        # launch multiple threads searching locations terms with xan
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(searchMultipleOccurrences, tmp.name, locations, search_col)
                for locations in locations_groups.values()
            ]
            # and collect results
            results = [f.result() for f in futures]
        # results = [searchMultipleOccurrences(tmp.name, locations, search_col) for locations in locations_groups.values()]
        # format results as dict
        results = {loc: res for loc, res in zip(locations_groups.keys(), results)}
    return results

def matchUsersMultipleLocations(locations_groups, metadata, headers, search_col='location', method='exact'):
    if method == 'regex':
        print(f"Searching multiple users locations matchs for {method} method ...")
        return regexMatchUsersMultipleLocations(locations_groups, metadata, headers, search_col)
    else:
        raise  ValueError(f'NOT IMPLEMENTED METHOD {method}')
