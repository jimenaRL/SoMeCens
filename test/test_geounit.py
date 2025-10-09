# =============================================================================
# GeoUnit class tests
# =============================================================================
#

import os
import yaml

from somecens import GeoUnit

dir_path = os.path.dirname(os.path.realpath(__file__))
DATADIR = os.path.join(dir_path, "data")

with open(os.path.join(DATADIR, "geounits.yml")) as f:
    GEOUNITS = yaml.safe_load(f)

with open(os.path.join(DATADIR, "age_distribution.yml")) as f:
    AGEDIST = yaml.safe_load(f)

with open(os.path.join(DATADIR, "gender_distribution.yml")) as f:
    GENDERDIST = yaml.safe_load(f)


def test_geoUnits():
    geoUnit = GeoUnit(**GEOUNITS[-1])
    age_dist = [a for a in AGEDIST if a['code'] == geoUnit.code][0]
    gender_dist = [a for a in GENDERDIST if a['code'] == geoUnit.code][0]
    geoUnit.setAgeDistribution(age_dist)
    geoUnit.setGenderDistribution(gender_dist)
    geoUnit.indentPrint()


if __name__ == "__main__":
    test_geoUnits()
