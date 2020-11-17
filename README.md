# genome-grist - reference-based exploration of Illumina metagenomes

<a href="https://pypi.org/project/genome-grist/"><img alt="PyPI" src="https://badge.fury.io/py/genome-grist.svg"></a>
<a href="https://github.com/dib-lab/pybbhash/blob/latest/LICENSE.txt"><img alt="License: 3-Clause BSD" src="https://img.shields.io/badge/License-BSD%203--Clause-blue.svg"></a>

## In brief

genome-grist automates a number of tasks around genome-based
metagenome interpretation.

One key point of genome-grist is this: we can take advantage of
[sourmash gather](https://sourmash.readthedocs.io/en/latest/classifying-signatures.html)
to find the smallest set of genomes to which to map metagenome reads.
genome-grist automates all the stuff AROUND doing that!

So, `genome-grist` is a toolkit to do the following:

1. download a metagenome
2. process it into trimmed reads, and make a [sourmash signature](https://sourmash.readthedocs.io/)
3. search the sourmash signature with 'gather' against sourmash databases, e.g. all of genbank
4. download the matching genomes from genbank
5. map all metagenome reads to genomes using minimap
6. extract matching reads iteratively based on gather, successively eliminating reads that matched to previous gather matches
7. run mapping on “leftover” reads to genomes
9. summarize all mapping results

## Installation

The command:
```
python -m pip install genome-grist
```
will install the latest version. Plase use python3.7 or later. We suggest
using an isolated conda environment; the following commands should work for
conda:

```
conda create -n grist python=3.7 pip
conda activate grist
python -m pip install genome-grist
```

## Quick start:

Run the following three commands.

First, download SRA sample HSMA33MX, trim reads, and build a sourmash
signature:
```
genome-grist process HSMA33MX smash_reads
```

Next, run sourmash signature against genbank:
```
genome-grist process HSMA33MX gather_genbank
```
(NOTE, this depends on the latest genbank genomes and won't work for most
people just yet; for now, use cached results from the repo:
```
cp tests/test-data/HSMA33MX.x.genbank.gather.csv outputs/genbank/
touch outputs/genbank/HSMA33MX.x.genbank.gather.out
```
)

Finally, download the reference genomes, map reads and produce a summary
report:
```
genome-grist process HSMA33MX summarize -j 8
```

(You can run all of the above with `make test` in the repo.)

The summary report will be in `outputs/reports/report-HSMA33MX.html`.

You can see some example reports for this and other data sets online:

* [HSMA33MX report](https://ctb.github.io/2020-grist-examples/reports/report-HSMA33MX.html)
* [Illumina metagenome from Shakya et al., 2014](https://ctb.github.io/2020-grist-examples/reports/report-SRR606249.html)) [(ref)](https://pubmed.ncbi.nlm.nih.gov/23387867/)
* [sample 1 from Hu et al., 2016 (oil well metagenome)](https://ctb.github.io/2020-grist-examples/reports/report-SRR1976948.html) [(ref)](https://mbio.asm.org/content/7/1/e01669-15)

## Compute requirements

You'll need enough disk space to store about 5 copies of your raw
metagenome.

The peak memory requirement is in the k-mer trimming and sourmash
gather steps.  You'll probably want between 30 and 60 GB of RAM for
those, although for smaller or less diverse metagenomes, you will use
a lot less.

## Full set of top-level `process` targets

- download_reads
- trim_reads
- smash_reads
- gather_genbank
- download_matching_genomes
- map_reads
- summarize

## Support

genome-grist is alpha-level software. Please be patient and kind :).

Please ask questions and add comments
[by filing github issues](https://github.com/dib-lab/genome-grist/issues).

## Why the name `grist`?

'grist' is in the sourmash family of names (sourmash, wort,
distillerycats, etc.) See
[Grist](https://en.wikipedia.org/wiki/Grist).

(It is not the
[computing grist](https://en.wikipedia.org/wiki/Grist_(computing))!)

---

CTB Nov 8, 2020
