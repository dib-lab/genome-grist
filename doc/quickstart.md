# A genome-grist quickstart

<!-- CTB: this is doc/quickstart.md in dib-lab/genome-grist -->

## Installation

We suggest installing in an isolated conda environment. The following will create a new environment, activate it, and install the latest version of genome-grist from PyPI (which is <a href="https://pypi.org/project/genome-grist/"><img alt="PyPI" src="https://badge.fury.io/py/genome-grist.svg"></a>).


Run:
```shell
conda create -y -n grist python=3.9 pip
conda activate grist
python -m pip install genome-grist
```

Note: genome-grist should run in Python 3.7 onwards; we haven't tested it extensively in Python 3.10 yet (as of Jan 2022).

## Running genome-grist

We currently recommend running genome-grist in its own directory, for several reasons; in particular, genome-grist uses snakemake and conda to install software under the working directory, and it's nice to have all the outputs be isolated.

Within the current working directory, genome-grist will create a `genbank_cache/` subdir, and any `outputs.NAME` subdirectories requested by the configuration.  We recommend always running genome-grist in this directory and naming the output directories after the different projects using genome-grist.

So, create a subdirectory and change into it:
```shell
mkdir grist/
cd grist/
```
Note, genome-grist works entirely within the current working directory and temp directories.

### Download a small example database

Download the GTDB r06 rs202 set of ~48,000 guide genomes, in a pre-prepared sourmash database format:
```
curl -L https://osf.io/w4bcm/download -o gtdb-rs202.genomic-reps.k31.sbt.zip
```
(You can use any sourmash database that uses Genbank identifiers here; see [available databases](https://sourmash.readthedocs.io/en/latest/databases.html) for more info.)

### Make a configuration file

Put the following in a config file named `conf-tutorial.yml`:
```yaml
samples:
- SRR5950647
outdir: outputs.tutorial/
metagenome_trim_memory: 1e9

sourmash_databases:
- gtdb-rs202.genomic-reps.k31.sbt.zip
```

### Do your first real run!

Execute:
```
genome-grist run conf-tutorial.yml summarize_gather summarize_mapping
```


This will perform the following steps:

* download the [SRR5950647 metagenome](https://www.ncbi.nlm.nih.gov/sra/?term=SRR5950647) from the Sequence Read Archive (target `download_reads`).
* preprocess it to remove adapters and low-abundance k-mers (target `trim_reads`).
* build a sourmash signature from the preprocess reads. (target `smash_reads`).
* perform a `sourmash gather` against the specified database (target `gather_reads`).
* download the matching genomes from GenBank into `genbank_cache/` (target `download_matching_genomes`).
* map the metagenome reads to the various genomes (target `map_reads`).
* produce two summary notebooks (targets `summarize_gather` and `summarize_mapping`).

You can put one or more targets on the command line as above with `summarize_gather` and `summarize_mapping`.

## Output files

The key output files under the outputs directory are:

* `gather/{sample}.x.genbank.gather.out` - human-readable output from [sourmash gather](https://sourmash.readthedocs.io/en/latest/classifying-signatures.html).
* `gather/{sample}.x.genbank.gather.csv` - [sourmash gather CSV output](https://sourmash.readthedocs.io/en/latest/classifying-signatures.html).
* `gather/{sample}.genomes.info.csv` - information about the matching genomes from genbank.
* `reports/report-{sample}.html` - a summary report.
* `abundtrim/{sample}.abundtrim.fq.gz` - trimmed and preprocessed reads.
* `sigs/{sample}.abundtrim.sig` - sourmash signature for the preprocessed reads.

Note that `genome-grist run <config.yml> zip` will create a file named `transfer.zip` with the above files in it.

