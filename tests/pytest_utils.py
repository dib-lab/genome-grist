"""
Utility functions for tests.
"""

import os.path
import csv
import gzip


def relative_file(filename):
    "Return the filename relative to the top level directory of this repo."
    thisdir = os.path.dirname(__file__)
    pkgdir = os.path.join(thisdir, "..")
    newpath = os.path.join(pkgdir, filename)
    return os.path.abspath(newpath)


def load_csv(filename):
    xopen = open
    if filename.endswith('.gz'):
        xopen = gzip.open
    with xopen(filename, "rt") as fp:
        r = csv.DictReader(fp)
        for row in r:
            yield row
