from __future__ import annotations
from typing import Type
from typing import Any

DEFAULTAGECATS = [
    'age_less_or_equal_18',
    'age_between_19_and_29',
    'age_between_30_and_39',
    'age_greater_or_equal_40'
]
DEFAULTGENDERCATS = ['male', 'female']

class GeoUnit:

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
        s += f"\n{indent}children: {' | '.join([child.code for child in self.children])}"
        print(s)

    def addChild(self, child: Type[GeoUnit]) -> None:
        self.children.append(child)

    def getChilds(self) -> None:
        return self.children

    def setAgeDistribution(ageDistribution: dict) -> None:
        assert ageDistribution.keys == self.ageCategories
        assert sum(map(float, ageDistribution.values)) == 100
        self.ageDistribution = ageDistribution

    def setGenderDistribution(genderDistribution: dict) -> None:
        assert genderDistribution.keys == self.genderCategories
        assert sum(map(float, genderDistribution.values)) == 100
        self.genderDistribution = genderDistribution

class DemoGraph:

    def showGeoUnit(self, indent: int = 0, geoUnit: GeoUnit | None = None) -> None:
        geoUnit.indentPrint()
        if geoUnit:
            for child in geoUnit.children:
                indent += 1
                self.showGeoUnit(indent, child)

    def showGeoUnits(self) -> None:
        self.showGeoUnit(0, self.rootGeoUnit)

    def getCountryAndCode(self):
        for d in self.demography:
            if d['level'] == '0':
                return d['label'], d['code']

    def checkDemography(self, demography: Iterable[Dict]) -> None:
        # check that there is only one level 0
        nb_first_levels = sum([1 for d in demography if d['level'] == '0'])
        if  nb_first_levels != 1:
            mssg = f"Found {nb_first_levels} firt levels. Must be only one."
            raise ValueError(mssg)

    def getGeoUnit(self, geoUnit, code: str):
        if geoUnit.code == code:
            return geoUnit
        for child in geoUnit.children:
            geoUnit = self.getGeoUnit(child, code)
            if geoUnit:
                return geoUnit

    def setGenderDistributions(geoUnit, genderDistribution: Iterable[Dict]) -> None:
        if geoUnit:
            for child in geoUnit.children:
                indent += 1
                self.showGeoUnit(indent, child)

    def setGenderDistributions(genderDistribution: Iterable[Dict]) -> None:
        self.setGenderDistributions(self.rootGeoUnit)

    def __init__(self, demography: Iterable[Dict]) -> None:
        """
        demography: list of Dicts (regarder comment faire dans Types)
        """
        self.checkDemography(demography)
        self.demography = demography
        country, code = self.getCountryAndCode()
        self.country = country
        self.countryCode = code
        self.rootGeoUnit = None
        self.buildGeoTree()

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
                    parent = self.getGeoUnit(
                            geoUnit=self.rootGeoUnit,
                            code=d['parent_code'])
                    parent.addChild(
                        GeoUnit(
                            label=d['label'],
                            level=int(d['level']),
                            code=d['code']))

