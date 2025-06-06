from __future__ import annotations
from typing import Type
from typing import Any
from functools import reduce

import csv
from somecens.tools import writeCsv, matchUsersLocations
from somecens.nuts.conf  import NUTS3AGECATS

DEFAULTAGECATS = set(NUTS3AGECATS)
DEFAULTGENDERCATS = {
    'male',
    'female',
    'total',
}

class GeoUnit:

    ageDistTol = 0.000001
    genderDistTol = 0.000001

    def __init__(
        self,
        label: str ,
        level: int,
        code: str,
        age_categories: set[str] = DEFAULTAGECATS,
        gender_categories: set[str] = DEFAULTGENDERCATS,
        ) -> None:
        self.label = label
        self.code = code
        self.level = level
        self.children = []
        self.ageCategories = age_categories
        self.ageDistribution = None
        self.genderCategories = gender_categories
        self.genderDistribution = None
        self.usersLocations = []

    def __str__(self) -> str:
        s = f"GeoUnit \n\tlabel: {self.label}\n\tlevel: {self.level}\n\tcode: {self.code}"
        if self.children:
            s += f"\n\tchildren: {' | '.join([child.code for child in self.children])}"
        return s

    def indentPrint(self):
        indent = "    " * self.level
        s = f"{indent}---------------------------------------------------------"

        s += f"\n{indent}GeoUnit"
        s += f"\n{indent}label: {self.label}"
        s += f"\n{indent}level: {self.level}"
        s += f"\n{indent}code: {self.code}"

        childrens = ' | '.join([child.code for child in self.children])
        if self.children:
            s += f"\n{indent}children: {childrens}"

        s += f"\n{indent}gender distribution: {self.genderDistribution}"

        stringAgeDistribution = None
        if self.ageDistribution is not None:
            ageIndent = "    " * (self.level + 1)
            stringAgeDistribution = '\n'+'\n'.join([
                f"{ageIndent}{k}: {v}" for k, v in self.ageDistribution.items()])
        s += f"\n{indent}age distribution: {stringAgeDistribution}"


        if self.usersLocations:
            usersIndent = "    " * (self.level + 1)
            stringUsersLocations = '\n' \
            +'\n'.join([f"{usersIndent}{u}" for u in self.usersLocations[:5]]) \
            + f'\n{usersIndent}...'
            s += f"\n{indent}nb localized users: {len(self.usersLocations)}"
            s += f"\n{indent}localized users examples: {stringUsersLocations}"

        print(s)

    def addChild(self, child: Type[GeoUnit]) -> None:
        self.children.append(child)

    def getChilds(self) -> None:
        return self.children

    def setUsersLocations(self, usersLocations: dict) -> None:
        self.usersLocations = usersLocations['users']

    def setAgeDistribution(self, ageDistribution: dict) -> None:
        ageDistribution = ageDistribution['age_distributions']
        assert self.ageCategories.issubset(set(ageDistribution.keys()))
        self.ageDistribution = ageDistribution

    def setGenderDistribution(self, genderDistribution: dict) -> None:
        assert self.genderCategories.issubset(set(genderDistribution.keys()))
        gd = {k: genderDistribution[k] for k in self.genderCategories}
        self.genderDistribution = gd

    def getLocalizedUsers(self) -> Iterable[tuple]:
        return self.usersLocations

class DemoGraph:

    demoKeys = {'country_code', 'label', 'level', 'code', 'parent_code'}
    genderCategories = DEFAULTGENDERCATS

    def __init__(
            self,
            demography: Iterable[Dict],
            genderCats: Iterable[str] | None = DEFAULTGENDERCATS) -> None:
        """
        demography: iterable of dicts
        Keys and values must be strings and dict keys equal to self.demoKeys
        genderCats: iterable of strings
        """
        self.checkDemography(demography)
        country, code = self._getCountryAndCode(demography)
        self.country = country
        self.countryCode = code
        self.demography = demography
        self.locations = []
        self.geoUnits = []
        self.rootGeoUnit = None
        self.buildGeoTree()

        self.genderCategories = genderCats
        # self.ageDistribution = age_categories

    def __str__(self) -> str:
        return f"{self.country.capitalize()} ({self.countryCode}) DemoGraph"

    def _showGeoUnits(self, indent: int = 0, geoUnit: GeoUnit | None = None) -> None:
        if geoUnit:
            geoUnit.indentPrint()
            for child in geoUnit.children:
                indent += 1
                self._showGeoUnits(indent, child)

    def showGeoUnits(self) -> None:
        self._showGeoUnits(0, self.rootGeoUnit)

    def _getCountryAndCode(self, demography) -> (str, str):
        for d in demography:
            if d['level'] == '0':
                return d['label'], d['code']

    def checkDemography(self, demography: Iterable[Dict]) -> None:
        # check dicts's keys and values instances
        kt = set([isinstance(k, str) for d in demography for k in d.keys()])
        vt = set([isinstance(v, str) for d in demography for v in d.values()])
        assert kt == vt == {True}
        # check dicts keys
        dk = set([set(d.keys()) ==  self.demoKeys for d in demography])
        assert dk == {True}
        # check that there is only one level 0
        nb_first_levels = sum([1 for d in demography if d['level'] == '0'])
        if  nb_first_levels != 1:
            mssg = f"Found {nb_first_levels} firt levels. Must be only one."
            raise ValueError(mssg)

    def _getGeoUnit(self, geoUnit, code: str) -> Type[GeoUnit]:
        if geoUnit.code == code:
            return geoUnit
        for child in geoUnit.children:
            geoUnit = self._getGeoUnit(child, code)
            if geoUnit:
                return geoUnit

    def getGeoUnit(self, code: str) -> Type[GeoUnit]:
        return self._getGeoUnit(geoUnit=self.rootGeoUnit, code=code)

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
        this_descendants = [self._getDescendants(child, []) for child in geoUnit.children]
        descendants += this_descendants
        return reduce(lambda x, y: x + y, descendants)

    def getDescendants(self, geoUnit) -> Type[GeoUnit]:
        return self._getDescendants(geoUnit, [])

    def getLocalizedUsers(self, code: str) -> None:
        geoUnit = self.getGeoUnit(code)
        descendants = self.getDescendants(geoUnit)
        return {g.code: g.getLocalizedUsers() for g in descendants}

    def checkGenderDistributions(self, genderDistribution: Iterable[Dict]) -> None:
        # check dicts keys
        dk = set([set(d.keys()) ==  self.genderCategories for d in genderDistribution])
        # check dicts's keys instances
        kt = set([isinstance(k, str) for d in genderDistribution for k in d.keys()])
        assert kt == {True}
        # check that dicts's values are convertible to float
        try:
            [float(d[k]) for d in genderDistribution for k in ['male', 'female', 'total']]
        except Exception as e:
            raise ValueError(
                """Unnable to parse genderDistribution.
                Please check that all values can be converted to float.""")
        # check that all geoUnits are present in the gender distribution
        codes = {gd['code'] for gd in genderDistribution}
        assert codes == {gd['code'] for gd in self.demography}

    def setGenderDistributions(self, genderDistribution: Iterable[Dict]) -> None:
        self.checkGenderDistributions(genderDistribution)
        self._setGenderDistributions(self.rootGeoUnit, genderDistribution)
        return

    def _setGenderDistributions(self, geoUnit: Type[GeoUnit], genderDistribution: Iterable[Dict]) -> None:
        # we already check that all codes are presents in the distribution
        ugd = [gd for gd in genderDistribution if gd['code'] == geoUnit.code][0]
        geoUnit.setGenderDistribution(ugd)
        for child in geoUnit.children:
            geoUnit = self._setGenderDistributions(child, genderDistribution)

    def setAgeDistributions(self, ageDistribution: Iterable[Dict]) -> None:
        # self.checkAgeDistributions(ageDistribution)
        self._setAgeDistributions(self.rootGeoUnit, ageDistribution)
        return

    def _setAgeDistributions(self, geoUnit: Type[GeoUnit], ageDistribution: Iterable[Dict]) -> None:
        # we already check that all codes are presents in the distribution
        ugd = [gd for gd in ageDistribution if gd['code'] == geoUnit.code][0]
        geoUnit.setAgeDistribution(ugd)
        for child in geoUnit.children:
            geoUnit = self._setAgeDistributions(child, ageDistribution)

    def setUsersLocations(self, usersLocations: Iterable[Dict]) -> None:
        # self.checkUsersLocations(usersLocations)
        self._setUsersLocations(self.rootGeoUnit, usersLocations)
        return

    def _setUsersLocations(self, geoUnit: Type[GeoUnit], usersLocations: Iterable[Dict]) -> None:
        ugd = [gd for gd in usersLocations if gd['loc'] == geoUnit.label]
        if ugd:
            geoUnit.setUsersLocations(ugd[0])
        else:
            print(f"Didn't find user for localisation {geoUnit.code} {geoUnit.label}")
        for child in geoUnit.children:
            geoUnit = self._setUsersLocations(child, usersLocations)

    def buildGeoTree(self) -> None:
        max_level = max(map(int, set([d['level'] for d in self.demography])))
        level = 0
        for d in self.demography:
            # we already check that there is only one level 0
            if d['level'] == '0':
                self.rootGeoUnit = GeoUnit(
                        label=d['label'],
                        level=int(d['level']),
                        code=d['code'])
                self.locations.append(d['label'])
                self.geoUnits.append(self.rootGeoUnit)

        while level < max_level:
            level += 1
            for d in self.demography:
                if d['level'] == str(level):
                    parent = self.getGeoUnit(code=d['parent_code'])
                    geoUnit =  GeoUnit(
                            label=d['label'],
                            level=int(d['level']),
                            code=d['code'])
                    parent.addChild(geoUnit)
                    self.locations.append(d['label'])
                    self.geoUnits.append(geoUnit)

    def exportLocaliationsMatches(self, level: int, path: str) -> None:
        headers = ['code', 'nb_matchs']
        data = []
        for geoUnit in self.geoUnits:
            if geoUnit.level == level:
                data.append([
                    geoUnit.code,
                    sum(map(len, self.getLocalizedUsers(geoUnit.code).values()))
                ])
        with open(path, 'w') as f:
            writer = csv.writer(f)
            # writer.writerow(headers)
            writer.writerows(data)
        print(f"File saved as {path}")