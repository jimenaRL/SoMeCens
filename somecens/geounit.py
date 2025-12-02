# =============================================================================
# Geounit
# =============================================================================
#
# Script implementing GeoUnit classes.
#
# GeoUnit class implements a tree structure where leaves are administrative
# divisions of a country (e.g. a NUTS in the European standard system)
# and may contain sociodemographic information like age and genre distributions.
#

from __future__ import annotations
from typing import Type
from typing import Any

from somecens.nuts.conf import NUTS3AGECATS, NUTS3GENDERCATS

DEFAULTAGECATS = NUTS3AGECATS
DEFAULTGENDERCATS = NUTS3GENDERCATS

class GeoUnit:
    """ Class implementing a tree structure of administrative geographics units.
    """
    ageDistTol = 0.000001
    genderDistTol = 0.000001

    def __init__(
        self,
        label: str,
        level: int,
        code: str,
        age_categories: set[str] = DEFAULTAGECATS,
        gender_categories: set[str] = DEFAULTGENDERCATS,
        **kwargs
    ) -> None:
        self.label = label
        self.code = code
        self.level = int(level)
        self.children = []
        self.ageCategories = age_categories
        self.ageDistribution = None
        self.genderCategories = gender_categories
        self.genderDistribution = None
        self.usersLocations = []
        self.subUnitsNames = []

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
            stringAgeDistribution = '\n' + '\n'.join([
                f"{ageIndent}{k}: {v}" for k, v in self.ageDistribution.items()])
        s += f"\n{indent}age distribution: {stringAgeDistribution}"

        if self.usersLocations:
            usersIndent = "    " * (self.level + 1)
            stringUsersLocations = '\n' \
                + '\n'.join([
                    f"{usersIndent}{u}" for u in self.usersLocations[:5]]) \
                + f'\n{usersIndent}...'
            s += f"\n{indent}nb localized users: {len(self.usersLocations)}"
            s += f"\n{indent}localized users examples: {stringUsersLocations}"

        sIndent = "    " * (self.level + 1)
        subUnitsNames = f'\n{sIndent}' + f'\n{sIndent}'.join(
            [s for s in self.subUnitsNames])
        if self.subUnitsNames:
            s += f"\n{indent}sub units names:{subUnitsNames}"

        print(s)

    def addChild(self, child: Type[GeoUnit]) -> None:
        self.children.append(child)

    def getChilds(self) -> None:
        return self.children

    def setUsersLocations(self, usersLocations: dict) -> None:
        self.usersLocations = usersLocations

    def setSubUnitsNames(self, subUnitsNames: Iterable[str]) -> None:
        self.subUnitsNames = subUnitsNames

    def setAgeDistribution(self, ageDistribution: dict) -> None:
        ageDistribution = ageDistribution['age_distributions']
        assert set(self.ageCategories).issubset(set(ageDistribution.keys()))
        self.ageDistribution = ageDistribution

    def setGenderDistribution(self, genderDistribution: dict) -> None:
        assert set(self.genderCategories).issubset(set(genderDistribution.keys()))
        gd = {k: genderDistribution[k] for k in self.genderCategories}
        self.genderDistribution = gd

    def getLocalizedUsers(self) -> Iterable[tuple]:
        return self.usersLocations

    def getSubUnits(self) -> Iterable[str]:
        return [self.label] + self.subUnitsNames
