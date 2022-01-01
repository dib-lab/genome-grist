from setuptools import setup, find_packages

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

CLASSIFIERS = [
    "Environment :: Console",
    "Environment :: MacOS X",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Natural Language :: English",
    "Operating System :: POSIX :: Linux",
    "Operating System :: MacOS :: MacOS X",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
]

setup(
    name="genome-grist",
    description="tools to support genome and metagenome analysis",
    url="https://github.com/dib-lab/genome-grist",
    author="C. Titus Brown, Luiz Irber, Tessa Pierce, Taylor Reiter",
    author_email="titus@idyll.org,lcirberjr@ucdavis.edu,ntpierce@gmail.com,tereiter@ucdavis.edu",
    license="BSD 3-clause",
    packages=find_packages(),
    classifiers=CLASSIFIERS,
    entry_points={"console_scripts": ["genome-grist  = genome_grist.__main__:main"]},
    include_package_data=True,
    package_data={"genome_grist": ["Snakefile", "*.yml", "*.ipynb"]},
    setup_requires=[
        "setuptools>=38.6.0",
        "setuptools_scm",
        "setuptools_scm_git_archive",
        "pytest-runner",
    ],
    use_scm_version={"write_to": "genome_grist/version.py"},
    install_requires=["snakemake==6.12.3", "click>=7,<8", "lxml==4.6.4",
                      "pandas>1,<2"],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
