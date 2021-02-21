import json
from math import floor
from sys import argv

path = argv[1]

with open(path, "r") as f:
    report = json.load(f)

totals = report["totals"]
cov = totals["percent_covered"]
totals["rounded_percent_covered"] = floor(cov * 10) / 10

with open(path, "w") as f:
    json.dump(report, f)
