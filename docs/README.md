# genome-grist

genome-grist is software that automates a number of tedious metagenome tasks related to reference-based analyses on Illumina metagenomes. Specifically, genome-grist will download public metagenomes from the SRA, preprocess them, and use [sourmash](https://sourmash.bio) `gather` to identify reference genomes for the metagenome. It will then download the reference genomes, map reads to them, and summarize the mapping.
