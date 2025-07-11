# =============================================================================
# Demograph tests
# =============================================================================
#

import os
import json
import yaml

from somecens import DemoGraph

# dir_path = os.path.dirname(os.path.realpath(__file__))
# geounits_path = os.path.join(dir_path, "data", "geounits.yml")
DATADIR = os.path.join("/home/jimena/work/dev/SoMeCens/tests/data")

with open(os.path.join(DATADIR, "geounits.yml")) as f:
    GEOUNITS = yaml.safe_load(f)

for g in GEOUNITS:
    print(json.dumps(g, indent=2))

with open(os.path.join(DATADIR, "subunits.yml")) as f:
    SUBUNITS = yaml.safe_load(f)

print(json.dumps(SUBUNITS, indent=2))

def test_demograph():
    demo = DemoGraph(demography=GEOUNITS)
    demo.setSubUnitsNames(SUBUNITS)


