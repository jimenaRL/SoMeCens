# =============================================================================
# Demograph
# =============================================================================
#
# Script implementing Demograph  class.
#
# Demograph class contains methods to create and manage GeoUnit tree structure
# from flatten input data, add sociodemographic information among others.
#

from __future__ import annotations
from typing import Type
from typing import Any
from functools import reduce

import os
import csv
import pandas as pd

from somecens import GeoUnit
from somecens.tools import checkIterable

from somecens.nuts.conf import NUTS3AGECATS, NUTS3GENDERCATS

DEFAULTAGECATS = NUTS3AGECATS
DEFAULTGENDERCATS = NUTS3GENDERCATS



class DemoGraph:
    """ Class to build and manage a GeoUnit tree structure.
    """

    demoKeys = {'country_code', 'label', 'level', 'code', 'parent_code'}
    ageDistributionsKeys = {'age_distributions', 'code'}

    def __init__(
            self,
            demography: Iterable[Dict],
            genderCats: Iterable[str] | None = DEFAULTGENDERCATS,
            ageCats: Iterable[str] | None = DEFAULTAGECATS,
            ) -> None:
        """
        demography: iterable of dicts of the form
                {
                    'country_code': 'FR',
                    'code': 'FRJ24',
                    'level': '3',
                    'label': 'Gers',
                    'parent_code': 'FRJ2'
                }
            representing geographical units.
        genderCats: iterable of strings wirh the accepted gender gategories.
        """

        self.checkDemography(demography)
        country, code = self._getCountryAndCode(demography)
        self.country = country
        self.countryCode = code
        self.demography = demography
        self.locations = {}
        self.geoUnits = []
        self.rootGeoUnit = None
        self.code2label = {}
        self.genderCategories = genderCats
        self.ageCategories = ageCats
        self.buildGeoTree()
        print(f"Created {self}")

    def __str__(self) -> str:
        return f"{self.country.capitalize()} ({self.countryCode}) DemoGraph"

    def _showGeoUnits(
        self,
        geoUnit: GeoUnit | None = None,
        max_level: int = -1
    ) -> None:
        if geoUnit:
            if geoUnit.level <= max_level:
                geoUnit.indentPrint()
            for child in geoUnit.children:
                self._showGeoUnits(child, max_level)

    def showGeoUnits(self, max_level: int = 1000) -> None:
        """ Print the demograph's geoUnits tree structure until given max level.
        """
        self._showGeoUnits(self.rootGeoUnit, max_level)

    def _getCountryAndCode(self, demography) -> (str, str):
        for d in demography:
            if d['level'] == '0':
                return d['label'], d['code']

    def getDeepestLevel(self) -> int:
        return max(map(int, set([d['level'] for d in self.demography])))

    def getLevelCodes(self, level: int) -> int:
        return [d['code'] for d in self.demography if int(d['level']) == level]

    def findLabelFromCode(self, code: str) -> str:
        if code not in self.code2label:
            raise ValueError(f"Code '{code}' is not present in demography.")
        return self.code2label[code]

    def findCodesFromLabel(self, label: str) -> str:
        reverseDict = {
            v: [k for k in self.code2label if self.code2label[k] == v]
            for v in self.code2label.values()
        }
        if label not in reverseDict:
            raise ValueError(f"Label '{label}' is not present in demography.")
        return reverseDict[label]

    def checkDemography(self, demography: Iterable[Dict]) -> None:
        # check dicts's keys and values instances
        kt = set([isinstance(k, str) for d in demography for k in d.keys()])
        vt = set([isinstance(v, str) for d in demography for v in d.values()])
        assert kt == vt == {True}
        # check dicts keys
        dk = set([set(d.keys()) == self.demoKeys for d in demography])
        assert dk == {True}
        # check that there is only one level 0
        nb_first_levels = sum([1 for d in demography if d['level'] == '0'])
        if nb_first_levels != 1:
            mssg = f"Found {nb_first_levels} firt levels. Must be only one."
            raise ValueError(mssg)

    def _getGeoUnit(self, geoUnit, code: str) -> Type[GeoUnit]:
        """
        If the geoUnit's associate code corresponds return the geoUnits,
        otherwise applies the method recursively to its childs.
        """
        if geoUnit.code == code:
            return geoUnit
        for child in geoUnit.children:
            geoUnit = self._getGeoUnit(child, code)
            if geoUnit:
                return geoUnit

    def getGeoUnit(self, code: str) -> Type[GeoUnit]:
        """
        Returns the geoUnit associate with the code
        """
        geoUnit = self._getGeoUnit(geoUnit=self.rootGeoUnit, code=code)
        if geoUnit is None:
            raise ValueError(f"There is no geoUnit with code '{code}'.")
        return geoUnit

    def _getGeoUnitByLabel(self, geoUnit, label: str) -> Type[GeoUnit]:
        if geoUnit.label == label:
            return geoUnit
        for child in geoUnit.children:
            geoUnit = self._getGeoUnitByLabel(child, label)
            if geoUnit:
                return geoUnit

    def getGeoUnitByLabel(self, label: str) -> Type[GeoUnit]:
        return self._getGeoUnitByLabel(geoUnit=self.rootGeoUnit, label=label)

    def _getDescendants(self, geoUnit: Type[GeoUnit], descendants):
        descendants.append([geoUnit])
        this_descendants = [
            self._getDescendants(child, []) for child in geoUnit.children]
        descendants += this_descendants
        return reduce(lambda x, y: x + y, descendants)

    def getDescendants(self, geoUnit) -> Type[GeoUnit]:
        """ Return a list of containing all descents of the input geoUnit.
        """
        return self._getDescendants(geoUnit, [])

    def getParentCode(self, geoUnit) -> Type[GeoUnit]:
        """ Return the parent of a geoUnit.
        """
        if geoUnit.level == 0:
            return ""
        for geo in self.geoUnits:
            if geoUnit.code in [child.code for child in geo.getChilds()]:
                return geo.code
        raise ValueError(f"Didn't find any parent for geoUnit {geoUnit}")

    def getAllSubUnits(self, max_level : int = -1) -> dict:
        return {g.code: g.getSubUnits() for g in self.geoUnits if g.level <= max_level}

    def getSubUnits(self, code) -> dict:
        for g in self.geoUnits:
            if code == g.code:
                return g.getSubUnits()
        raise ValueError(f"Code '{code}' is not present in demography.")

    def getLocalizedUsers(self, code: str, descendants: bool | False) -> None:
        """
        Return the localized users of a geoUnit and its descendants
        """
        geoUnit = self.getGeoUnit(code)
        if descendants:
            return {
                g.code:
                g.getLocalizedUsers() for g in self.getDescendants(geoUnit)}
        return {geoUnit.code: geoUnit.getLocalizedUsers()}

    def checkAgeDistributions(
        self,
        ageDistribution: Iterable[Dict],
        verbose: bool | False,
        raiseErrors: bool | False
    ) -> None:

        checkIterable(ageDistribution)

        # check dicts keys
        kt = set([
            isinstance(k, str) for d in ageDistribution for k in d.keys()])
        assert kt == {True}

        keys = self.ageDistributionsKeys
        for d in ageDistribution:
            if not keys.issubset(set(d.keys())):
                e = f"Expecting dict with keys {keys} but found {set(d.keys())}"
                e += f" for age distribution of geoUnit with code {d['code']}:"
                e += f"\n\t{d}"
                raise ValueError(e)
            missing_keys = set(self.ageCategories) - set(d["age_distributions"].keys())
            if  missing_keys:
                m = f"There are missing age age_distributions keys at:\n\t{d}"
                if raiseErrors:
                    raise ValueError(m)
                else:
                    m2 = f"Converting missing values to -1.0."
                    d['age_distributions'].update({k: -1.0 for k in missing_keys})
        # check that dicts's values are convertible to float
        for d in ageDistribution:
            for key in self.ageCategories:
                val = d['age_distributions'][key]
                try:
                    float(val)
                except Exception as e:
                    m = f"Unnable to convert ageDistribution value '{val}' to float for key {key} of {d['code']} age distribution. "
                    if raiseErrors:
                        m1 = "Please check that all values can be converted to float."
                        raise ValueError(m+m1)
                    else:
                        if verbose:
                            m2 = f"Converting value to -1.0."
                            print(m+m2)
                        d['age_distributions'][key] = -1.0

        # check that all geoUnits are present in the gender distribution
        codes_gd = {gd['code'] for gd in ageDistribution}
        codes_demo =  {gd['code'] for gd in self.demography}
        missing_codes = codes_demo - codes_gd
        if not codes_demo.issubset(codes_gd):
            mssg = f"There are missing geoUnits in the gender distribution:\n"
            mssg += f"{missing_codes}"
            if raiseErrors:
                raise ValueError(mssg)
            else:
                filling = [
                    {
                        'code': code,
                        # hot fix
                        'age_distributions': {k: -1.0 for k in self.ageCategories}
                    }
                    for code in missing_codes
                ]
                if verbose:
                    print(mssg + f"\nAdding {filling}.")
                ageDistribution.extend(filling)
        return ageDistribution

    def checkGenderDistributions(
        self,
        genderDistribution: Iterable[Dict]
    ) -> None:

        checkIterable(genderDistribution)

        # check dicts keys
        dk = set([
            set(d.keys()) == self.genderCategories for d in genderDistribution])
        # check dicts's keys instances
        kt = set([
            isinstance(k, str) for d in genderDistribution for k in d.keys()])
        assert kt == {True}
        # check that dicts's values are convertible to float
        try:
            [
                float(d[k])
                for d in genderDistribution for k in self.genderCategories
            ]
        except Exception as e:
            raise ValueError(
                """Unnable to parse genderDistribution.
                Please check that all values can be converted to float.""")
        # check that all geoUnits are present in the gender distribution
        codes_gd = {gd['code'] for gd in genderDistribution}
        codes_demo =  {gd['code'] for gd in self.demography}
        if not codes_demo.issubset(codes_gd):
            mssg = f"There are missing geoUnits in the gender distribution:\n"
            mssg += f"{codes_demo - codes_gd}"
            raise ValueError(mssg)

    def setGenderDistributions(
        self,
        genderDistribution: Iterable[Dict]
    ) -> None:
        self.checkGenderDistributions(genderDistribution)
        self._setGenderDistributions(self.rootGeoUnit, genderDistribution)
        return

    def _setGenderDistributions(
        self,
        geoUnit: Type[GeoUnit], genderDistribution: Iterable[Dict]
    ) -> None:
        # we already check that all codes are presents in the distribution
        ugd = [gd for gd in genderDistribution if gd['code'] == geoUnit.code][0]
        geoUnit.setGenderDistribution(ugd)
        for child in geoUnit.children:
            geoUnit = self._setGenderDistributions(child, genderDistribution)

    def setAgeDistributions(
            self,
            ageDistribution: Iterable[Dict],
            verbose: bool = False,
            raiseErrors: bool = False,
    ) -> None:
        ageDistribution = self.checkAgeDistributions(ageDistribution, verbose, raiseErrors)
        self._setAgeDistributions(self.rootGeoUnit, ageDistribution)
        return

    def _setAgeDistributions(
        self,
        geoUnit: Type[GeoUnit],
        ageDistribution: Iterable[Dict]
    ) -> None:
        # we already check that all codes are presents in the distribution
        ugd = [gd for gd in ageDistribution if gd['code'] == geoUnit.code][0]
        geoUnit.setAgeDistribution(ugd)
        for child in geoUnit.children:
            geoUnit = self._setAgeDistributions(child, ageDistribution)

    def setUsersLocations(self, usersLocations: Iterable[Dict]) -> None:
        self._setUsersLocations(self.rootGeoUnit, usersLocations)
        return

    def _setUsersLocations(
        self,
        geoUnit: Type[GeoUnit],
        usersLocations: Iterable[Dict]
    ) -> None:
        if geoUnit.code in usersLocations:
            geoUnit.setUsersLocations(usersLocations[geoUnit.code])
        else:
            print(
                f"Didn't find users for geoUnit {geoUnit.code} {geoUnit.label}")
        for child in geoUnit.children:
            geoUnit = self._setUsersLocations(child, usersLocations)

    def setSubUnitsNames(self, subUnits: Iterable[Dict]) -> None:
        """ subUnits msut be a list of dictionary of the form
                {'code' : list of corresponding geographical sub-units names}
        where 'code' corresponds to one geoUnit of the demograph.
        ).
        """
        self._setSubUnitsNames(self.rootGeoUnit, subUnits)
        return

    def _setSubUnitsNames(
        self,
        geoUnit: Type[GeoUnit],
        subUnitsNames: Iterable[Dict]
    ) -> None:
        if geoUnit.code in subUnitsNames:
            geoUnit.setSubUnitsNames(subUnitsNames[geoUnit.code])
        else:
            for child in geoUnit.children:
                geoUnit = self._setSubUnitsNames(child, subUnitsNames)

    def buildGeoTree(self) -> None:
        max_level = self.getDeepestLevel()
        level = 0
        for d in self.demography:
            # we already check that there is only one level 0
            if d['level'] == '0':
                self.rootGeoUnit = GeoUnit(
                    label=d['label'],
                    level=int(d['level']),
                    code=d['code'],
                    gender_categories=self.genderCategories,
                    age_categories=self.ageCategories
                )
                self.locations[d['code']] = d['label']
                self.geoUnits.append(self.rootGeoUnit)
                self.code2label[d['code']] = d['label']


        while level < max_level:
            level += 1
            for d in self.demography:
                if d['level'] == str(level):
                    parent = self.getGeoUnit(code=d['parent_code'])
                    geoUnit = GeoUnit(
                        label=d['label'],
                        level=int(d['level']),
                        code=d['code'],
                        gender_categories=self.genderCategories,
                        age_categories=self.ageCategories
                    )
                    parent.addChild(geoUnit)
                    self.locations[d['code']] = d['label']
                    self.geoUnits.append(geoUnit)
                    self.code2label[d['code']] = d['label']


    def getUniqueUsersMatched(self, code: str, descendants: bool = True) -> set:
        return {
            match[0]
            for matched in self.getLocalizedUsers(code, descendants).values()
            for match in matched
        }

    def exportUnitsReport(self, path: str | None = None) -> Iterable:

        max_level = self.getDeepestLevel()
        columns = ["level", "code", "parent_code", "label", "subunits"]
        columns += ['unit_nb_matchs', 'unit_percent_matched', 'descendants_nb_matchs', 'descendants_percent_matched']
        columns += [c for c in self.genderCategories]
        columns += [c for c in self.ageCategories]

        data = []
        for geo in self.geoUnits:
            unit_matched = len(self.getUniqueUsersMatched(geo.code, descendants=False))
            desc_matched = len(self.getUniqueUsersMatched(geo.code, descendants=True))

            total = float(geo.genderDistribution['total'])

            geoData = [
                geo.level,
                geo.code,
                self.getParentCode(geo),
                geo.label,
                " | ".join(geo.subUnitsNames)
            ]
            geoData += [unit_matched, 100 * unit_matched / total, desc_matched, 100 * desc_matched / total]
            geoData += [geo.genderDistribution[c] for c in self.genderCategories]
            geoData += [geo.ageDistribution[c] for c in self.ageCategories]

            data.append(geoData)

        if path:
            with open(path, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(data)
            print(f"File saved as {path}")

        return data, columns


    def exportLocalizedUsers(self, path: str | None = None, full_path: str | None = None) -> Iterable:

        max_level = self.getDeepestLevel()
        columns = ["pseudo_id", "location", "screen_name", "normalized_location"]

        # get matched user per unit and store by unit level
        frames = {level: [] for level in range(max_level+1)}
        for geo in self.geoUnits:
            frames[geo.level].append(
                pd.DataFrame(geo.getLocalizedUsers(), columns=columns, dtype=str) \
                    .assign(code=geo.code) \
                    .assign(label=geo.label) \
                    .rename(columns={"code": f"level_{geo.level}_code"}))

        # concat matched users from same unit level and aggregate by unit name
        for level in frames:
            frames[level] = pd.concat(frames[level]) \
                .groupby(columns)[f'level_{level}_code'] \
                .apply(lambda x: ' | '.join(x)) \
                .reset_index()

        # merge all
        if max_level < 1:
            return frames[0]

        localizedUsers = frames[0].merge(frames[1], how='outer', on=columns)
        for level in range(2, max_level+1):
            localizedUsers = localizedUsers.merge(frames[level], how='outer', on=columns)
        localizedUsers = localizedUsers.fillna("")

        def getLabels(text):
            if not text:
                return text
            return ' | '.join([self.code2label[t] for t in text.split(' | ')])

        for level in range(0, max_level+1):
            localizedUsers = localizedUsers \
                .assign(label=localizedUsers[f'level_{level}_code'].apply(getLabels)) \
                .rename(columns={"label": f'level_{level}_label'})

        # order columns
        for level in range(0, max_level+1):
            columns.append(f'level_{level}_code')
            columns.append(f'level_{level}_label')
        localizedUsers = localizedUsers[columns]

        # save
        data = localizedUsers.values.tolist()
        if path:
            with open(path, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(data)
            print(f"Localized users file saved as {path}")

            if full_path:
                drop_columns = [f"level_{l}_label" for l in range(0, max_level + 1)]
                df = localizedUsers
                df.drop(columns=drop_columns, inplace=True)
                for l in reversed(range(1, max_level + 1)):
                    level_codes = self.getLevelCodes(l)

                    for code in level_codes:
                        idx = df[df[f"level_{l}_code"] == code].index
                        prev_level = df.loc[idx, f"level_{l - 1}_code"]
                        parent_code = self.getParentCode(self.getGeoUnit(code))
                        def fn(v):
                            v = set(v.split(" | ")) - {""}
                            return " | ".join(list(set(v).union({parent_code})))
                        prev_level = prev_level.apply(fn)
                        df.loc[idx, f"level_{l - 1}_code"] = prev_level

                    # trait multiple codes per level
                    gn = lambda code : self.getParentCode(self.getGeoUnit(code))
                    idx = df[df[f"level_{l}_code"].apply(lambda v: " | " in v)].index
                    this_level = df.loc[idx, f"level_{l}_code"]
                    this_level_parents = this_level.apply(lambda v: " | ".join(list(map(gn, v.split(" | ")))))
                    prev_level = df.loc[idx, f"level_{l - 1}_code"]
                    df.loc[idx, f"level_{l - 1}_code"] = prev_level + " | " + this_level_parents
                    hn = lambda v: " | ".join(set(v.split(" | ")) - {""})
                    df.loc[idx, f"level_{l - 1}_code"] = df.loc[idx, f"level_{l - 1}_code"].apply(hn)

                with open(full_path, 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow(df.columns)
                    writer.writerows(df.values.tolist())
                print(f"Localized users file saved as {path}")

        return  data, columns


    def exportLocalizationsMatchesNb(
        self,
        level: int,
        path: str,
        descendants: bool = True,
        add_headers: bool = False
    ) -> None:
        headers = ['code', 'nb_matchs']
        data = []
        for geoUnit in self.geoUnits:
            if geoUnit.level == level:
                nb_unique_matched = len(self.getUniqueUsersMatched(geo.code, descendants=descendants))
                data.append([geoUnit.code, nb_unique_matched])
        with open(path, 'w') as f:
            writer = csv.writer(f)
            if add_headers:
                writer.writerow(headers)
            writer.writerows(data)
        print(f"File saved as {path}")

    def exportLocalizationsMatchesPerc(
        self,
        level: int,
        path: str,
        descendants: bool = True,
        add_headers: bool = False
    ) -> None:
        headers = ['code', 'nb_matchs_perc']
        data = []
        for geoUnit in self.geoUnits:
            if geoUnit.level == level:
                total = float(geoUnit.genderDistribution['total'])
                # get unique twitter_ids (at index 0)
                nb_unique_matched = len(self.getUniqueUsersMatched(geoUnit.code, descendants=descendants))
                data.append([
                    geoUnit.code,
                    100 * nb_unique_matched / total
                ])

        with open(path, 'w') as f:
            writer = csv.writer(f)
            if add_headers:
                writer.writerow(headers)
            writer.writerows(data)
        print(f"File saved as {path}")
