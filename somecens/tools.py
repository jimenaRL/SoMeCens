from __future__ import annotations
import csv
import emoji
import tempfile
import concurrent.futures
from subprocess import Popen, PIPE

from fog.tokenizers import FingerprintTokenizer


def writeCsv(
    file: str,
    rows: Iterable[tuple],
    headers: Iterable[str] | None = None,
    verbose: bool = False
):
    if not isinstance(headers, list):
        raise ValueError(
            f"Headers must be a list. Found {type(headers)} for '{headers}'.")
    with open(file, 'w') as f:
        writer = csv.writer(f)
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
    banned_regex: str | list(str) = [],
    allowed_emojis: str | list(str) = [],
    banned_emojis: str | list(str) = [],
) -> Iterable[list]:
    """
    Use xan program to search for ocurrences of a regex (or list of regex) at
    the csv file in path. Returns a list containig the rows of the csv file
    that match the term at the 'search_col' column.
    """

    # if needed convert strings to list
    if isinstance(regex, str):
        regex = [regex]

    if isinstance(banned_regex, str):
        banned_regex = [banned_regex]

    commands = ['xan', 'search', '-s', search_col, '--ignore-case', '--regex']

    with tempfile.NamedTemporaryFile() as tmpFile:

        # 1/ perform invert search with banned regex

        # write down banned_regex list to a tmp file to be used by xan
        with tempfile.NamedTemporaryFile() as tmpBannedRegex:
            with open(tmpBannedRegex.name, 'w') as f:
                f.writelines('\n'.join(banned_regex))

            # perform invert search with xan
            invert_search_cmds = commands + ["--invert-match", "--patterns", tmpBannedRegex.name, file]
            p = Popen(invert_search_cmds, stdout=PIPE)
            # capture string output
            output = p.communicate()[0].decode()
            # and write down output to temp file
            with open(tmpFile.name, 'w') as f:
                f.writelines(output)

        # 2/ perform regular search with regex

        # write down regex list to a tmp file to be used by xan
        with tempfile.NamedTemporaryFile() as tmpRegex:
            with open(tmpRegex.name, 'w') as f:
                f.writelines('\n'.join(regex))

            # perform invert search with xan
            search_cmds = commands + ["--patterns", tmpRegex.name, tmpFile.name]
            p = Popen(search_cmds, stdout=PIPE)
            # and capture string output
            output = p.communicate()[0].decode()
            # parse output
            try:
                matchs = list(csv.reader(output[:-1].split("\n")))
            except Exception as exc:
                print(f"!!!!!!!!!!!!!!!!!!!!!!!! SOMETHING WENT WRONG! !!!!!!!!!!!!!!!")
                print(exc)

    # remove headers
    matchs = matchs[1:]

    # remove matchs with banned emojis
    ematchs = []
    removed = []
    for match in matchs:
        location = match[1]
        found_emojis = emoji.distinct_emoji_list(location)
        found_demojize_emojis = [emoji.demojize(e) for e in found_emojis]
        if any([e in allowed_emojis for e in found_demojize_emojis]):
            ematchs.append(match)
            continue
        if any([e in banned_emojis for e in found_demojize_emojis]):
            removed.append(match)
        else:
            ematchs.append(match)

    nb_removed = len(matchs) - len(ematchs)
    # if nb_removed > 0:
    #     print(f"Removed {nb_removed} matched terms with banned emojis:")
    #     print(removed)

    return ematchs


def matchUsersLocations(
    locations: dict,
    data: Iterable[list[str]],
    stopwords: list[str],
    split_characters: list[str],
    search_index: int,
    banned_words: Iterable[str] = [],
    allowed_emojis: Iterable[str] = [],
    banned_emojis: Iterable[str] = [],
    has_headers: bool = True,
    verbose: bool = False
):
    """
    Search for ocurrences of terms in locations groups.
    Uses multithreaded instances of searchMultipleOccurrences method.

    Input 'locations' is a dictionari of the form

        {code: term} or {code: [term_1, ..., term_N]}

    Input 'data' is a list of tuples of the form

        [(id_1, location_1), ..., (id_M, location_M)]

    Returns a dict with the same keys of 'locations' and values

        {code: [(id_j, location_j, normalized_location_that_matched_j), ...]

    """

    if verbose:
        msg = f"Searching location matchs for {len(locations)} groups and "
        msg += f"{len(data)} users. Using stopwords {stopwords} "
        msg += f"and split characters {split_characters}."
        print(msg)

    # if needed convert values of dict from string to list
    for code, value in locations.items():
        if isinstance(value, str):
            locations[code] = [value]

    # create tokenizer
    tokenizer = FingerprintTokenizer(
        stopwords=stopwords, split=split_characters, sort=False)

    # for each tuple in data, normalize string at index using the tokenizer
    normalized = [
        list(d) + [' '.join(tokenizer(d[search_index]))] for d in data]

    # write normalized data to a tmp file to be used by the search method
    with tempfile.NamedTemporaryFile() as tmp:
        if has_headers:
            if isinstance(data[0], tuple):
                data[0] = list(data[0])
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
                    [makeRegex(' '.join(tokenizer(loc))) for loc in locations],
                    "normalized",
                    [makeRegex(' '.join(tokenizer(b))) for b in banned_words],
                    allowed_emojis,
                    banned_emojis)
                for locations in locations.values()
            ]
            # and collect results
            results = [f.result() for f in futures]

    # format results as dict and return
    results = {loc: res for loc, res in zip(locations.keys(), results)}

    if verbose:
        for loc, res in results.items():
            print(f"{loc}: {len(res)}")

    return results
