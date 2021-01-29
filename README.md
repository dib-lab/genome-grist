# genome-grist: a quickstart tutorial.

This quickstart tutorial will take about 30 minutes to run, and
requires 5 GB of disk space and 4 GB of RAM, as well as a fairly
good Internet connection.

## What is genome-grist?

genome-grist is software that automates a number of tedious metagenome tasks related to reference-based analyses on Illumina metagenomes. Specifically, genome-grist will download public metagenomes from the SRA, preprocess them, and use `sourmash gather` to identify reference genomes for the metagenome. It will then download the reference genomes, map reads to them, and summarize the mapping.

## Installing genome-grist

We suggest installing in an isolated conda environment. The following will create a new environment, activate it, and install the latest version of genome-grist from PyPI (which is <a href="https://pypi.org/project/genome-grist/"><img alt="PyPI" src="https://badge.fury.io/py/genome-grist.svg"></a>).

```
conda create -y -n grist python=3.8 pip
conda activate grist
python -m pip install genome-grist
```
## Running genome-grist

We currently recommend running genome-grist in its own directory, for several reasons that include software installation (genome-grist uses snakemake and conda to install software under this directory).

Within the current working directory, genome-grist will create an `inputs` subdir, a `genbank_genomes` subdir, and any `outputs.NAME` subdirectories required by the configuration; it should be straightforward to keep projects separate by configuring the output directories appropriately.

So, create a subdirectory and change into it:
```shell
mkdir grist/
cd grist/
```
Note, genome-grist does not rely on the directory name or location in any way; it works entirely within the current working directory.

### Download a small example database

Download the GTDB release 95 set of ~32k guide genomes, in a pre-prepared sourmash database format:
```
curl -L https://osf.io/4n3m5/download -o gtdb-r95.nucleotide-k31-scaled1000.sbt.zip
```
(Any sourmash database will do as long as the sequences are named so that the full GenBank accession is the first field in the name.)

### Make a configuration file

Put the following in a config file named `conf-tutorial.yml`:
```
sample:
- HSMA33MX
outdir: outputs.tutorial/
metagenome_trim_memory: 1e9
sourmash_database_glob_pattern: gtdb-r95.nucleotide-k31-scaled1000.sbt.zip
```

Notes:
* you can put multiple samples IDs here, in a [YAML array format](https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started/) - put them on a new line after a dash (`-`).
* if you have multiple databases you can specify them here with an appropriate wild card pattern, e.g. `db/*` will work.
* if you are running this on the farm HPC at UC Davis, you can search all of genbank by *omitting* the database configuration line. Currently these files are not yet publicly available, which is why this tutorial uses GTDB instead.

### Do your first real run!

Execute:
```
genome-grist run conf-tutorial.yml summarize
```

This will perform the following steps:
* download the [HSMA33MX metagenome](https://www.ncbi.nlm.nih.gov/sra/?term=HSMA33MX) from the Sequence Read Archive (target `download_reads`).
* preprocess it to remove adapters and low-abundance k-mers (target `trim_reads`).
* build a sourmash signature from the preprocess reads. (target `smash_reads`).
* perform a `sourmash gather` against the specified database (target `gather_genbank`).
* download the matching genomes from GenBank into `genbank_genomes/` (target `download_matching_genomes`).
* map the metagenome reads to the various genomes (target `map_reads`).
* produce a summary notebook (target `summarize`).

The default target is `gather_genbank`, and you can put one or more targets on the command line as above with `summarize`.

## Output files

The key output files under the outputs directory are:

* `genbank/{sample}.x.genbank.gather.out` - human-readable output from [sourmash gather](https://sourmash.readthedocs.io/en/latest/classifying-signatures.html).
* `genbank/{sample}.x.genbank.gather.csv` - [sourmash gather CSV output](https://sourmash.readthedocs.io/en/latest/classifying-signatures.html).
* `genbank/{sample}.genomes.info.csv` - information about the matching genomes from genbank.
* `reports/report-{sample}.html` - a summary report.
* `abundtrim/{sample}.abundtrim.fq.gz` - trimmed and preprocessed reads.
* `sigs/HSMA33MX.abundtrim.sig` - sourmash signature for the preprocessed reads.

Note that `genome-grist run <config.yml> zip` will create a file named `transfer.zip` with the above files in it.

## Where to insert your own files

genome-grist is built on top of [the snakemake workflow](https://snakemake.readthedocs.io/en/stable/), which lets you substitute your own files in many places.

For example,
* you can put your own `SAMPLE_1.fastq.gz`, `SAMPLE_2.fastq.gz`, and `SAMPLE_unpaired.fastq.gz` files in `raw/` to have genome-grist process reads for you.
* you can put your own interleaved reads file in `abundtrim/SAMPLE.abundtrim.fq.gz` to run genome-grist on a private or preprocessed set of reads;
* you can put your own sourmash signature (k=31, scaled=1000) in `sigs/SAMPLE.abundtrim.sig` if you want to have it do the database search for you;

Please see [the genome-grist Snakefile](https://github.com/dib-lab/genome-grist/blob/latest/genome_grist/conf/Snakefile) for all the gory details.

## Other information

### Resource requirements

**Disk space:** genome-grist makes about 4-5 copies of each SRA metagenome.

**Memory:** the genbank search step on all of genbank takes ~120 GB of RAM. On GTDB, it's much, much less. Other than that, the other steps are all under 10 GB of RAM (unless you adjust `metagenome_trim_memory` upwards, which may be needed for complex metagenomes).

**Time:** This is largely dependent on the size of the metagenome; 100m reads takes less than a day or two, typically. The processing of multiple data sets can be done in parallel with `-j`, as well, although you probably want to specify resource limits. For example, here is the command that Titus uses on farm:
```
genome-grist run <config> -k --resources mem_mb=145000 -j 16
```
to run in 150GB of RAM, which will run at most one genbank search at a time.

### Installing unreleased versions.

You can run genome-grist from a git checkout directory by using pip to install it in editable mode:
```
pip install -e .
```

### Support

We like to support our software!

That having been said, genome-grist is early-stage beta-level software. Please be patient and kind :).

Please ask questions and add comments [on the github issue tracker for genome-grist](https://github.com/dib-lab/genome-grist/issues).

## Why the name `grist`?

'grist' is in the sourmash family of names (sourmash, wort, distillerycats, etc.) See [Grist in Wikipedia](https://en.wikipedia.org/wiki/Grist).

(It is not the [computing grist](https://en.wikipedia.org/wiki/Grist_(computing))!)

---

[CTB](https://twitter.com/ctitusbrown/) Jan 27, 2021
