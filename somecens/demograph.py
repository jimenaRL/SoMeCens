from __future__ import annotations
from typing import Type
from typing import Any

DEFAULTAGECATS = {
    'age_less_or_equal_18',
    'age_between_19_and_29',
    'age_between_30_and_39',
    'age_greater_or_equal_40'
}
DEFAULTGENDERCATS = {
    'male',
    'female',
    'total'
}

class GeoUnit:

    ageDistTol = 0.000001
    genderDistTol = 0.000001

    def __init__(
        self,
        label: str ,
        level: int,
        code: str,
        age_categories: list[str] = DEFAULTGENDERCATS,
        gender_categories: list[str] = DEFAULTGENDERCATS,
        ) -> None:
        self.label = label
        self.code = code
        self.level = level
        self.children = []
        self.ageDistribution = age_categories
        self.genderDistribution = gender_categories

    def __str__(self) -> str:
        s = f"GeoUnit {self.label}\n\tlevel: {self.level}\n\tcode: {self.code}"
        s += f"\n\tchildren: {' | '.join([child.code for child in self.children])}"
        return s

    def indentPrint(self):
        indent = "    " * self.level
        s = f"{indent}---------------------------------"
        s += f"\n{indent}GeoUnit {self.label}"
        s += f"\n{indent}level: {self.level}"
        s += f"\n{indent}code: {self.code}"
        codes = ' | '.join([child.code for child in self.children])
        if self.children:
            s += f"\n{indent}children: {codes}"
        print(s)

    def addChild(self, child: Type[GeoUnit]) -> None:
        self.children.append(child)

    def getChilds(self) -> None:
        return self.children

    def setAgeDistribution(ageDistribution: dict) -> None:
        assert ageDistribution.keys == self.ageCategories
        assert abs(sum(ageDistribution.values) - 100) < self.ageDistTol
        self.ageDistribution = ageDistribution

    def setGenderDistribution(genderDistribution: dict) -> None:
        assert genderDistribution.keys == self.genderCategories
        assert abs(sum(genderDistribution.values) - 100) < self.genderDistTol
        self.genderDistribution = genderDistribution

class DemoGraph:

    demoKeys = {'country_code', 'label', 'level', 'code', 'parent_code'}
    defaultGenderCategories = DEFAULTGENDERCATS

    def _showGeoUnits(self, indent: int = 0, geoUnit: GeoUnit | None = None) -> None:
        if geoUnit:
            geoUnit.indentPrint()
            for child in geoUnit.children:
                indent += 1
                self._showGeoUnits(indent, child)

    def showGeoUnits(self) -> None:
        self._showGeoUnits(0, self.rootGeoUnit)

    def getCountryAndCode(self, demography):
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

    def _getGeoUnit(self, geoUnit, code: str):
        if geoUnit.code == code:
            return geoUnit
        for child in geoUnit.children:
            geoUnit = self._getGeoUnit(child, code)
            if geoUnit:
                return geoUnit

    def getGeoUnit(self, code: str):
        return self._getGeoUnit(geoUnit=self.rootGeoUnit, code=code)

    def checkGenderDistributions(self, genderDistribution: Iterable[Dict]) -> None:
        # check dicts's keys instances
        kt = set([isinstance(k, str) for d in demography for k in d.keys()])
        # check that dicts's values are convertible to float
        try:
            gD = [{k: float(v)} for d in demography for k, v in d.items()]
        except Exception as e:
            raise ValueError(
                """Unnable to parse genderDistribution.
                Please check that all values can be converted to float.""")
        # check dicts keys
        cats = self.genderCategories.union('code')
        dk = set([set(d.keys()) ==  cats for d in dD])
        assert dk == {True}
        # check that all geoUnits are present in the gender distribution
        # TO DO

    def __init__(
            self,
            demography: Iterable[Dict],
            genderCats: Iterable[str] | None = defaultGenderCategories) -> None:
        """
        demography: iterable of dicts
        Keys and values must be strings and dict keys equal to self.demoKeys
        genderCats: iterable of strings
        """
        self.checkDemography(demography)
        country, code = self.getCountryAndCode(demography)
        self.country = country
        self.countryCode = code
        self.demography = demography
        self.rootGeoUnit = None
        self.buildGeoTree()

        self.genderCategories = genderCats
        # self.ageDistribution = age_categories

    def __str__(self) -> str:
        return f"{self.country.capitalize()} ({self.countryCode}) DemoGraph"

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
        while level < max_level:
            level += 1
            for d in self.demography:
                if d['level'] == str(level):
                    parent = self.getGeoUnit(code=d['parent_code'])
                    parent.addChild(
                        GeoUnit(
                            label=d['label'],
                            level=int(d['level']),
                            code=d['code']))

