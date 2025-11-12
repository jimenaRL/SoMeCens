from __future__ import annotations
import csv
import time
import emoji
import tempfile
import concurrent.futures
from subprocess import Popen, PIPE

from fog.tokenizers import FingerprintTokenizer

from somecens.conf import PAYS, COUNTRIES, UNITALIASES, COUNTRYALIASES

def getTokenizer(
    stopwords: Iterable[str] = [],
    split: list[str] = [],
    sort: bool = False
)-> Iterable[str]:
    if not split:
        return FingerprintTokenizer(stopwords=stopwords, sort=sort)
    else:
        return FingerprintTokenizer(stopwords=stopwords, split=split, sort=sort)

def tokenize(
    string: str,
    stopwords: Iterable[str] = [],
    split: list[str] = [],
    sort: bool = False
)-> Iterable[str]:
    tok = getTokenizer(stopwords=stopwords, split=split, sort=sort)
    return ' '.join(tok(string))

def tokenizeList(
    strings: Iterable[str],
    stopwords: Iterable[str] = [],
    split: list[str] = [],
    sort: bool = False
)-> Iterable[str]:
    tok = getTokenizer(stopwords=stopwords, split=split, sort=sort)
    return [' '.join(tok(s)) for s in strings]


def getOtherCountriesNames(country: str) -> Iterable[str]:

    countries = set(tokenizeList(COUNTRIES.union(PAYS)))
    country_aliases = [tokenizeList(aliases) for aliases in COUNTRYALIASES]

    for aliases_groups in country_aliases:
        if country in aliases_groups:
            country_aliases.remove(aliases_groups)
            this_country_aliases = set(aliases_groups)

    other_countries = countries - this_country_aliases

    # add aliases
    for aliases_groups in country_aliases:
        assert not this_country_aliases & set(aliases_groups)
        other_countries = other_countries.union(set(aliases_groups))

    return other_countries

def getUnitsAliases(country: str) -> Iterable[str]:
    return UNITALIASES[country]


def getCountryAliases(country: str) -> Iterable[str]:
    country = tokenize(country)
    country_aliases = [tokenizeList(aliases) for aliases in COUNTRYALIASES]

    for aliases_groups in country_aliases:
        if country in aliases_groups:
            return aliases_groups

    print(f"Didn't find aliases fro country {country}")
    return [country]

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


def reverseSearch(
    csvfile: str,
    search_col: str,
    banned_regex_file: str,
    verbose: bool = False,
    ) -> Iterable[list]:
    """
    Spawn a new process to perform an inverted regex search using xan and
    return the captured string output. Returns a list containig the rows of
    the input csv file that didn't match  at the 'search_col' column
    the terms in the file banned_regex_file.
    """
    commands = ['xan', 'search', '-s', search_col, '--ignore-case', '--regex']
    commands += ["--invert-match", "--patterns", banned_regex_file, csvfile]
    if verbose:
        mssg = "Preforming a xan reverse search to remove banned regex, "
        mssg += f"the command is:\n\t{' '.join(commands)}"
        print(mssg)
    p = Popen(commands, stdout=PIPE)
    return p.communicate()[0].decode()

def searchOccurrences(
    csvfile: str,
    regex: list(str),
    search_col: str = "location",
    allowed_emojis: str | list(str) = [],
    banned_emojis: str | list(str) = [],
    verbose: bool = False,
    ) -> Iterable[list]:
    """
    Use xan program to search for ocurrences of a list of regex in a csv file.
    Returns a list containig the rows of the csv file that matched
    the term at the 'search_col' column.
    """

    with tempfile.NamedTemporaryFile() as tmpRegex:

        # save list of regex to a temporary file
        with open(tmpRegex.name, 'w') as f:
            f.writelines('\n'.join(regex))

        # spawn a new xan process
        commands = ['xan', 'search', '-s', search_col, '--ignore-case']
        commands += ['--regex', "--patterns", tmpRegex.name, csvfile]
        if verbose:
            mssg = "Preforming a xan search, "
            mssg += f"the command is:\n\t{' '.join(commands)}"
            start = time.time()
        p = Popen(commands, stdout=PIPE)
        if verbose:
            print(f"Search took {time.time() - start} seconds.")
        #  capture string output
        output = p.communicate()[0].decode()
        # parse output
        try:
            matchs = list(csv.reader(output[:-1].split("\n")))
        except Exception as exc:
            print(f"Something went wrong when parsing subprocess output:")
            print(exc)

    # remove headers
    matchs = matchs[1:]

    # remove matchs with banned emojis
    ematchs = []
    removed = []
    if banned_emojis:
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
        matchs = ematchs

        if nb_removed > 0 and verbose:
            print(f"Removed {nb_removed} matched terms with banned emojis:")
            print(removed)

    return matchs


def searchOccurrence(
    csvfile: str,
    regex: str,
    search_col: str,
    allowed_emojis: str | list(str) = [],
    banned_emojis: str | list(str) = [],
    ) -> Iterable[list]:
    """
    Use xan program to search for ocurrences of a regex in a csv file.
    Returns a list containig the rows of the csv file that matched
    the term at the 'search_col' column.
    """
    return searchOccurrences(
        csvfile=csvfile,
        regex=[regex],
        search_col=search_col,
        allowed_emojis=allowed_emojis,
        banned_emojis=banned_emojis
    )

def matchUsersLocations(
    locations: dict,
    data: Iterable[list[str]],
    stopwords: list[str],
    split_characters: list[str],
    search_index: int | Iterable[int],
    banned_words: Iterable[str] = [],
    aliases: Dict = {},
    allowed_emojis: Iterable[str] = [],
    banned_emojis: Iterable[str] = [],
    has_headers: bool = True,
    verbose: bool = False
    ):
    """
    Search for ocurrences of terms in locations groups.
    Uses multithreaded instances of searchMultipleOccurrences method.

    Input 'locations' is a dictionary of the form

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

    # if needed convert search index to a list of int
    if isinstance(search_index, int):
            search_index = [search_index]

    # if needed convert dict value's from string to list
    for code, value in locations.items():
        if isinstance(value, str):
            locations[code] = [value]

    # count rows
    nb_rows = len(data) - 1 if has_headers else len(data)

    # create tokenizer
    tokenizer = FingerprintTokenizer(
        stopwords=stopwords, split=split_characters, sort=False)

    # for each tuple in data, normalize string at index using the tokenizer
    normalized = [
        list(d) + [' '.join([item for sublist in [tokenizer(d[i]) for i in search_index] for item in sublist])] for d in data]

    banned_regex = [makeRegex(' '.join(tokenizer(b))) for b in banned_words]

    # add aliases
    for code, locs in locations.items():
        for alias_code, alias in aliases.items():
            if code == alias_code:
                locs.extend(alias)

    # set search column
    search_col = "normalized"
    # write down banned_regex list to a tmp file to be used by xan
    with tempfile.NamedTemporaryFile() as tmpBannedRegex:
        with open(tmpBannedRegex.name, 'w') as f:
            f.writelines('\n'.join(banned_regex))

        # write normalized data to a tmp file to be used by the search method
        with tempfile.NamedTemporaryFile() as tmp:
            # add or modify headers to take into account the new search column
            # with normalized tokens from column at search_index
            if has_headers:
                if isinstance(data[0], tuple):
                    data[0] = list(data[0])
                headers = data[0] + [search_col]
                normalized = normalized[1:]
            else:
                headers = [str(j) for j in range(len(data[0]))] + [search_col]
            # write tmp file
            writeCsv(tmp.name, normalized, headers)

            # remove lines with banned words by making a reverse search
            # and write down captured string output to the tmp file
            start = time.time()
            output = reverseSearch(
                csvfile=tmp.name,
                search_col=search_col,
                banned_regex_file=tmpBannedRegex.name,
                verbose=verbose)
            if verbose:
                print(f"Reverse search took {time.time() - start} seconds.")
            with open(tmp.name, 'w') as f:
                f.writelines(output)

            # count lines removed
            if verbose:
                nb_output_lines = len(output.split('\n')) - 1
                if has_headers:
                    nb_output_lines -= 1
                r = nb_rows - nb_output_lines
                if r > 0:
                    print(
                        f"Removed {r} rows from reverse search with banned words.")

            # launch multiple threads searching for terms
            if verbose:
                mssg = "Launching asynchronous pools of threads xan search "
                mssg += f"for {len(locations)} locations."
                print(mssg)
            start = time.time()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        searchOccurrences,
                        tmp.name,
                        [makeRegex(' '.join(tokenizer(loc))) for loc in locations_values],
                        search_col,
                        allowed_emojis,
                        banned_emojis,
                        False)
                    for locations_values in locations.values()
                ]
                # and collect results
                results = [f.result() for f in futures]
            if verbose:
                print(f"Asynchronous searchs took {time.time() - start} seconds.")

        # format results as dict and return
        results = {loc: res for loc, res in zip(locations.keys(), results)}

    if verbose:
        for loc, res in results.items():
            if len(res) > 0:
                print(f"Found {len(res)} matchs for location {loc}.")

    return results
