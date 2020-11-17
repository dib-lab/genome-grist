import os.path


def relative_file(filename):
    "Return the filename relative to the top level directory of this repo."
    thisdir = os.path.dirname(__file__)
    pkgdir = os.path.join(thisdir, "..")
    newpath = os.path.join(pkgdir, filename)
    return os.path.abspath(newpath)
