from setuptools import setup, find_packages

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
    name = 'genome-grist',
    version = "0.1",
    description="tools to support genome and metagenome analysis",
    url="https://github.com/dib-lab/genome-grist",
    author="C. Titus Brown, Luiz Irber, Tessa Pierce, Taylor Reiter",
    author_email="titus@idyll.org,lcirberjr@ucdavis.edu,ntpierce@gmail.com,tereiter@ucdavis.edu",
    license="BSD 3-clause",
    packages = find_packages(),
    classifiers = CLASSIFIERS,
    entry_points = {'console_scripts': [
        'genome-grist  = genome_grist.__main__:main'
        ]
    },
    include_package_data=True,
    package_data = { "genome_grist": ["Snakefile", "*.yml", "*.ipynb"] },
    setup_requires = [ "setuptools>=38.6.0",
                       'setuptools_scm', 'setuptools_scm_git_archive' ],
    use_scm_version = {"write_to": "genome_grist/version.py"},
    install_requires = ['snakemake>=5.10', 'click>=7']
)
