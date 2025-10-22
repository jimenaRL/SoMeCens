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

import csv

from somecens import GeoUnit
from somecens.nuts.conf import NUTS3AGECATS

DEFAULTAGECATS = set(NUTS3AGECATS)
DEFAULTGENDERCATS = {
    'male',
    'female',
    'total',
}


class DemoGraph:
    """ Class to build and manage a GeoUnit tree structure.
    """

    demoKeys = {'country_code', 'label', 'level', 'code', 'parent_code'}
    genderCategories = DEFAULTGENDERCATS

    def __init__(
            self,
            demography: Iterable[Dict],
            genderCats: Iterable[str] | None = DEFAULTGENDERCATS) -> None:
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
        self.buildGeoTree()

        self.genderCategories = genderCats
        # self.ageDistribution = age_categories

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

    def checkGenderDistributions(
        self,
        genderDistribution: Iterable[Dict]
    ) -> None:
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
                for d in genderDistribution for k in ['male', 'female', 'total']
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

    def setAgeDistributions(self, ageDistribution: Iterable[Dict]) -> None:
        # self.checkAgeDistributions(ageDistribution)
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
        max_level = max(map(int, set([d['level'] for d in self.demography])))
        level = 0
        for d in self.demography:
            # we already check that there is only one level 0
            if d['level'] == '0':
                self.rootGeoUnit = GeoUnit(
                    label=d['label'],
                    level=int(d['level']),
                    code=d['code'])
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
                        code=d['code'])
                    parent.addChild(geoUnit)
                    self.locations[d['code']] = d['label']
                    self.geoUnits.append(geoUnit)
                    self.code2label[d['code']] = d['label']

    def exportLocalizationsMatches(
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
                data.append([
                    geoUnit.code,
                    sum(map(len, self.getLocalizedUsers(geoUnit.code,descendants).values()))
                ])
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
                matched = sum(map(
                    len,
                    self.getLocalizedUsers(geoUnit.code, descendants).values()
                ))
                data.append([
                    geoUnit.code,
                    100 * matched / total
                ])

        with open(path, 'w') as f:
            writer = csv.writer(f)
            if add_headers:
                writer.writerow(headers)
            writer.writerows(data)
        print(f"File saved as {path}")

    def getGeoUnitLocalizationsStats(self, code: str) -> Iterable:
        for g in self.geoUnits:
            if g.code == code:

                total = float(g.genderDistribution['total'])

                nb_unit_matched = sum(map(
                    len,
                    self.getLocalizedUsers(g.code, descendants=False).values()
                ))

                # use a set to avoid duplicated users
                descendant_unique_matched = set()
                descendant_matched = self.getLocalizedUsers(
                    g.code,
                    descendants=True)
                for user_list in descendant_matched.values():
                    # update set with matched users pseudo_ids
                    descendant_unique_matched.update({u[0] for u in user_list})
                nb_descendant_matched = len(descendant_unique_matched)

                return [
                    g.level,
                    g.code,
                    g.label,
                    total,
                    nb_unit_matched,
                    nb_descendant_matched,
                    100 * nb_descendant_matched / total,
                ]
