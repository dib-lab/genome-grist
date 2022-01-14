# genome-grist docs: supporting private genome databases

[![hackmd-github-sync-badge](https://hackmd.io/p7QfD_SsQg6sElDbrzpcsA/badge)](https://hackmd.io/p7QfD_SsQg6sElDbrzpcsA)


[toc]

Note: this currently requires [genome-grist#130](https://github.com/dib-lab/genome-grist/pull/130).

# Supporting private genomes

## Overview

genome-grist does the following:

* runs `sourmash gather` on metagenome signatures, using one or more sourmash databases
* retrieves the full genomes for any matches
* incorporates taxonomy information for the genomes into the taxonomy summary report (if taxonomy reporting is requested)

For Genbank genomes, all the necessary information is available already!

sourmash already provides pre-built databases containing [all GTDB genomes (R06 rs202)](https://sourmash.readthedocs.io/en/latest/databases.html) as well as [all 700,000 Genbank microbial genomes from July 2020](https://github.com/sourmash-bio/sourmash/issues/1749#issuecomment-947920226).

For genomes available through Genbank (aka with Genbank accessions), genome-grist does the genome retrieval automatically, so you don't need to have them downloaded already.

Taxonomy spreadsheets are available for GTDB (at the databases page) and for Genbank 700k/July 2020 (link upon request).

## Preparing information on private genomes

If you want to use unpublished genomes with genome-grist, you'll need to provide your own sourmash database, your own set of genome files and information, and your own taxonomy spreadsheet. Luckily this is all pretty straightforward and we provide tools to help you! Read on!

Note that you can absolutely combine Genbank with your own databases here, or just use your own databases.

### Choosing identifiers for your genomes

You'll need to choose unique identifiers for your genomes. genome-grist requires that your identifier does not have a space, colon (:), or forward slash (/) in it; everything else should be fine.

### Preparing your genome files

You'll need one FASTA file per genome (gzip or bz2 compressed is fine). The filename doesn't matter. It's probably easiest if they're all in one directory, although this isn't necessary.

We suggest naming at the first sequence in each FASTA file with the identifier at the start, space delimited - for example `MY_ID_1.1 first_sequence_name is very special` .

### Creating a sourmash database

Sketch all your genomes with the following command:
```
sourmash sketch dna -p k=31,scaled=1000
```

If you've named your genomes so that the first sequence contains the identifer, you can add `--name-from-first` and then the sequences will be named the right thing for the next step.

If not, you'll need to manually adjust the names of the signatures produced by `sourmash sketch`. (You can do this with `sourmash sig rename`, but there's no simple way to do this in bulk.)

Once you have all your genome signatures, you can combine them into a single file with 

```
sourmash index output.sbt.zip *.sig
```
and that will then be your sourmash database that you can cherish and treasure!

If you have lots of genomes (1000 or more?) there are other approaches that might make your life more convenient; just ask for suggestions on [the sourmah issue tracker](https://github.com/dib-lab/sourmash/issues).

We chose k=31 above because that matches our default parameters, and we have provided Genbank databases for k=31 (as well as k=21 and k=51). But the only real limitation here is that all your databases support the same k-mer and scaled sizes.

### Providing your genomes to genome-grist

info file contents
generating an info file
editing info file
renaming your genomes

### Providing taxonomy information

sourmash taxonomy file format info
how to specify taxonomies

### Testing it all out

maybe try it with a "fake" metagenome that's just one or two of your genome signatures concatenated, to make sure it all works.

## An example for you to try: the `podar-ref` database

[Comparative metagenomic and rRNA microbial diversity characterization using archaeal and bacterial synthetic communities, Shakya et al., 2014](https://pubmed.ncbi.nlm.nih.gov/23387867/) made a lovely mock metagenome containing approximately 65 different strains of microbes.

[Evaluating Metagenome Assembly on a Simple Defined Community with Many Strain Variants, Awad et al., 2017](https://www.biorxiv.org/content/10.1101/155358v3) used sourmash to analyze this community, and produced an updated list of reference genomes that is available for  download.

While this list of reference genomes is in fact in Genbank, they use non-Genbank identifiers, and so it's a good example data set for "private" genomes.

So! Let's run through setting up these reference genomes as a private (non-Genbank) database for genome-grist to use, and then test it out by applying genome-grist to the mock metagenome!

It should take under 10 minutes total to run all the commands.

Note: If you have a developer installation of `genome-grist`, you can run everything below with `make test-private` in the root `genome-grist/` directory.

### Step 0: Install genome-grist and set up your directory

<!-- EITHER follow the installation instructions (@@) -->

For now, do this in the genome-grist development directory. Clone the genome-grist repo, create the grist environment with conda, and then:

Switch to the appropriate branch:

```
git switch allow/private
git pull
```

and make sure you've installed things appropriately:
```
pip install -e .
```
you may also need sourmash...
```
pip install sourmash
```

Now you should be good to go!

### Step 1: Download and unpack the `podar` reference genomes

First, we need to get our hands on the genome sequences themselves.

The genomes from Awad et al., 2017, are available for download [from a project on the Open Science Framework](https://osf.io/vbhy5/). The following commands will download them and unpack them into the directory `databases/podar-ref/`

```
mkdir -p databases/podar-ref
curl -L https://osf.io/vbhy5/download -o databases/podar-ref.tar.gz
cd databases/podar-ref/ && tar xzf ../podar-ref.tar.gz
cd ../../
```

### Step 2: Build sketches and construct a sourmash database

genome-grist uses sourmash to generate a *minimum metagenome cover* containing the best matches to the metagenome, so we need to turn the downloaded genomes into a sourmash database.

The following command will sketch all of the `.fa` files and save the resulting sourmash signatures into `databases/podar-ref.zip`:
```shell
sourmash sketch dna -p k=31,scaled=1000 --name-from-first \
        databases/podar-ref/*.fa -o databases/podar-ref.zip
```
note the use of `--name-from-first`, which names the sketches after the first FASTA header in each file.

If you look at the zip file with `sourmash sig describe databases/podar-ref.zip`, you'll see that all of the signature names start with their accessions, which is what we want.

### Step 3: Copy the genomes in to a new location with new names

genome-grist needs the genomes in their own individual files, in a directory. The files need to be named by their identifiers in the format `{ident}_genomic.fna.gz`. 

genome-grist has a utility to do this for you, based on the contents of genome files. To use it, run this command:
```
python -m genome_grist.copy_private_genomes databases/podar-ref/*.fa -o databases/podar-ref.info.csv -d databases/podar-ref.d
````
The subdirectory `databases/podar-ref.d/` should now contain 64 genome files, named by their identifiers. 

There will also be an "information file", `databases/podar-ref.info.csv`, that contains three columns. These were autogenerated by the script from the FASTA files you gave it. You can edit the `ncbi_tax_name` column and change it to whatever you want; the other columns need to match with other information so please don't change those!

Note that `ncbi_tax_name` is just for display purposes; this allows grist to translate identifiers to (for example) a species and strain name to put on generated graphs.

### Step 4: Build genome "info files" for genome-grist

Next, we need to provide genome-grist with individual "info" files for each genome, named as `{ident}.info.csv`. This should be autogenerated from the aggregate `info.csv` file created in the previous step.

genome-grist has a utility that will create these files for you. Run:
```
python -m genome_grist.make_info_file databases/podar-ref.info.csv
```
to use the combined info CSV from the previous step to create the necessary info files.

The subdirectory `databases/podar-ref.d/` should now contain 128 files - 64 genome files, and 64 '.info.csv' files, one for each genome.

### Step 5: Download the taxonomy file

Last but not least, you'll want a taxonomy file for these genomes, in a format that `sourmash taxonomy` can use. ([See `sourmash tax` docs](https://sourmash.readthedocs.io/en/latest/command-line.html#sourmash-tax-subcommands-for-integrating-taxonomic-information-into-gather-result).)

For this data set, you can get it [from a project on the Open Science Framework](https://osf.io/4yhjw/).

To download it, run:
```
curl -L https://osf.io/4yhjw/download -o databases/podar-ref.tax.csv
```

This will create with superkingdom, phylum, etc. entries for each of the reference genomes you've downloaded.

### Step 6: Try it out on a (small) mock metagenome!

While you can certainly run this on the entire metagenome from Shakya et al., 2014, that will take a while. So we've prepared a 1m read subset of the data for you to try out.

You can download this subsetted metagenome like so:
```shell
mkdir -p outputs.private/abundtrim
curl -L https://osf.io/ckbq3/download -o outputs.private/abundtrim/podar.abundtrim.fq.gz
```
and then confirm that the config file `conf-private.yml` has the following content:
```yaml=
sample:
- podar

outdir: outputs.private/

private_databases:
- databases/podar-ref.zip

private_databases_info:
- databases/podar-ref.info.csv

taxonomies:
- databases/podar-ref.tax.csv
```

Now run:

```
genome-grist run conf-private.yml summarize_gather summarize_mapping -j 4 -p
```

and (hopefully) it will all work!!

Assuming there are no errors and everything is green, look at the HTML files in `outputs.private/reports/*.html`.

## The complete set of config file options

The options below can be set and/or overriden in a project specific config file that is passed into `genome-grist`.

Config files can be either [YAML](https://en.wikipedia.org/wiki/YAML) or JSON. We suggest YAML since it's nicer to edit.

Every genome-grist installation comes with two config files in the `conf/` subdirectory of the `genome_grist/` Python package, `defaults.conf` and `system.conf`.  They are read in the order `defaults.conf`, `system.conf`, and project-specific config. So, you can ignore the first two and just override options in the project-specific config file. But you can also change the install-wide default parameters in `system.conf` if you like.

You can use `showconf` to show the current aggregate config like so: `genome-grist run conf.yml showconf`.

### An annotated config file

```yaml=
# NOTE: all paths are relative to the working directory.

### PROJECT-SPECIFIC PARAMETERS YOU MUST SET FOR EACH PROJECT

# samples: a list of metagenome names. REQUIRED.
# - the sample names cannot contain periods
# - you can use SRA accessions for automatic download, or provide the reads yourself
samples:
- metagenome_one
- metagenome_two

# outdir: a directory where all the output will be placed, e.g. outputs.myproject. REQUIRED.
# this will be created if it doesn't exist.
outdir: some_directory

# metagenome_trim_memory: how much memory (RAM) to use when trimming reads with khmer's trim-low-abund.
# set to 1e9 for very low diversity samples,
# 10e9 for medium-diversity samples,
# and 50e9 if you're foolishly working with soil :)
# The default is set to 1e9, which is too low for your data.
# WARNING: this much memory _will_ be allocated when running genome-grist!
metagenome_trim_memory: 10e9

### INSTALLATION INFORMATION YOU NEED TO SET AT LEAST ONCE
#
# These must be set after you install genome-grist and download the various databases.

# genbank_databases: a list of sourmash databases that use Genbank identifiers
# you'll need to point this at a local download of 
# databases from e.g. https://sourmash.readthedocs.io/en/latest/databases.html
# note that GTDB databases use genbank identifiers :)
# can be an empty list, []
genbank_databases:
- /path/to/sourmash-db/database1
- /path/to/sourmash-db/database2

# taxonomies: a list of files to use for taxonomy information. See documentation for `sourmash taxonomy`.
# can be empty list, [].
taxonomies:
- /path/to/taxonomy/files

### INTERMEDIATE CONFIGURATION OPTIONS
#
# These are ways you can fine-tune genome-grist.
# We suggest changing these only once you've successfully run genome-grist a few times!

# private_databases: a list of sourmash databases that use non-Genbank identifiers.
# can be an empty list, []
private_databases:
- /path/to/local-sourmash-db/database3

# private_databases_info: a list of database info files.
# can be empty list, [].
# see documentation for more details.
private_databases_info: 
- /path/to/local-sourmash-db/database3.info.csv

# picklist: a --picklist argument to use when searching the sourmash database, to limit which signatures to search.
# see sourmash command line documentation for more details.
# EXAMPLE:
#     picklist: some_sig_list.csv:ident:ident
picklist: ""

# sourmash_database_ksize: k-mer size to use when searching sourmash databases.
# DEFAULT: 31
sourmash_database_ksize: 31

# sourmash_compute_ksizes: a list of k-mer sizes
# to use when creating sketches for samples. should include the database ksize.
# DEFAULTS: 21, 31, 15
sourmash_compute_ksizes:
- 21
- 31
- 51

# sourmash_compute_scaled: a scaled parameter to use when creating sketches for samples. See sourmash docs for details.
# DEFAULT: 1000
sourmash_compute_scaled: 1000

# sourmash_sigtype: 'DNA' or 'protein' - the type of signature to compute for samples.
# DEFAULT: DNA
sourmash_sigtype: DNA

### SYSTEM SPECIFIC PARAMETERS
#
# These are good defaults for small projects, but you may
# want to change them if you're doing big things on a cluster, or something.

# tempdir: a directory where SRA download temporary files will go, e.g. /tmp
# new subdirs will be created, used, and then removed.
tempdir: some_other_directory

# genbank_cache: where genomes downloaded from genbank will be cached.
# this needs to be writeable by people executing genome-grist; if it's system-wide, suggest making a a+rwxt directory.
# DEFAULT ./genbank_cache
genbank_cache: ./genbank_cache

### ADVANCED TECHNICAL PARAMETERS
#
# These probably don't need to be changed unless
# you actually run into problems running genome-grist.

# prefetch_memory: how much memory to allow for
# sourmash prefetch when running genome-grist.
# this memory may not actually be used, depending on sourmash databases used.
# the default is set for the all-Genbank database.
# DEFAULT: 100e9
prefetch_memory: 100e9
```

