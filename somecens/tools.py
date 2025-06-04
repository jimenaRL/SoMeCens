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

def getOccurrences(file, term, search_col):
    p = Popen(['xan', 'search', '-s', search_col, term, file], stdout=PIPE)
    output = p.communicate()[0].decode()
    with tempfile.NamedTemporaryFile() as tmp:
        with open(tmp.name, 'w') as f:
            f.writelines(output)
        with open(tmp.name, 'r') as f:
            matchs = [l for l in csv.reader(f)][1:]
        return {
            'loc': term,
            'nb_matchs': len(matchs),
            'users': matchs,
            }

def matchUsersLocations(locations, metadata, headers, search_col = 'location'):
    with tempfile.NamedTemporaryFile() as tmp:
        # write metadata to tmp file
        writeCsv(tmp.name, metadata, headers=headers)
        # launch multiple threads searching locations terms with xan
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(getOccurrences, tmp.name, loc, search_col)
                for loc in locations
            ]
            # and collect results
            results = [f.result() for f in futures]

    return results

