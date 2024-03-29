# A guide to genome-grist output files

genome-grist runs many steps and because of that it creates _a lot_ of
output files. In brief, genome-grist can do some or all of the following
steps:

* downloads and trims metagenomes from the SRA;
* runs `sourmash gather` on Genbank or GTDB databases to find genomes;
* downloads matching genomes from Genbank;
* maps metagenome reads to the downloaded genomes;
* does a
  [second round of mapping](#second-pass-mapping-the-files-in-leftover)
  that ensures reads are not double-counted;
* produces summary reports of metagenome composition, taxonomy, and mapping;

and each of these steps has its own set of outputs.

Below is a guide to the various outputs! We welcome questions and
comments; please ask questions in
[the genome-grist issue tracker](https://github.com/dib-lab/genome-grist/issues)
as you have them!

## Configuring your output directory

genome-grist places all files in the `{outdir}` folder, which must be
set in the config file; for example, if your config file contains
```
outdir: outputs.metag
```
then all of the directories below will be created under `outputs.metag/`.

## Files and subdirectories within {outdir}

Below, we use "sample" and "metagenome" interchangeably.

### Metagenome reads

* `{outdir}/raw/` - untrimmed reads, from the SRA or private sequencing.
* `{outdir}/trim/` - adapter and quality-trimmed reads, starting from `raw/`; inputs into downstream steps.
* `{outdir}/abundtrim/` - optional output of variable-coverage k-mer trimming; not used in genome-grist.

### sourmash output

* `{outdir}/sigs/` - sourmash sketches calculated from trimmed reads in `{outdir}/trim/`.
* `{outdir}/gather/` - sourmash outputs; see details below.

### Genomes and mapping information

* `{outdir}/genomes/` - sequence files and associated information for any genomes found in a sample.
* `{outdir}/mapping/` - mapping results for sample reads to genomes.
* `{outdir}/leftover/` - "leftover" mapping results for second-pass mapping; see details below.

### Reporting and summary output

* `{outdir}/reports/` - summary reports of sourmash gather output, minimap output, and sourmash taxonomy.
* `{outdir}/{sample}.info.yaml` - summary information on each sample

## Second-pass mapping - the files in `leftover/`

genome-grist actually does _two_ different rounds of mapping.

The first round is straightforward mapping: all reads are mapped to all genomes. In brief, the metagenome reads are mapped to all genomes from the [minimum metagenome cover](https://www.biorxiv.org/content/10.1101/2022.01.11.475838v2) generated by `sourmash gather`. All of the statistics and outputs in the `{outdir}/mapping/` location come from this process.

Crucially, during this process, reads may map to more than one genome. There is no specialized handling of multi-mapping reads.

During the second pass of mapping, this changes!

For the second round, grist does the following prior to generating the mapping results in the `leftover/` directory. 
1. for the first genome in the gather results,
2. maps reads to that genome
3. removes those reads from further consideration for mapping,
4. and then proceeds to the second step.

In effect, what this means is that if there's a region shared between multiple genomes in the minimum metagenome cover, all of the reads that would map to the shared region are "claimed" by the genome that is ranked earlier in the gather results.

Reads that did map to such a shared region but were claimed by an earlier genome are saved for each genome to a file with the extension `overlap.fq.gz` within the `mapping/` directory; reads that will be mapped to a particular genome are saved in a file `leftover.fq.gz`, also within the `mapping/` directory.

To summarize: under the `mapping/` directory,

* the `mapped.fq.gz` files contain all the reads that map to the genomes;
* the `leftover.fq.gz` files contain the subset of mapped reads that will be mapped to that genome in the second round;
* the `overlap.fq.gz` files contain the subset of mapped reads that were removed from consideration due to overlap with an earlier rank genome;

Then, the `leftover/` directory contains the mapping results for the `leftover.fq.gz`.

A key outcome of this is that **read mapping information under `mapping/` includes multimapped reads**. So you can't just e.g. sum the numbers of mapped reads from that directory, or you may be double-counting some reads. However, **the read mapping information under `leftover/` only counts each read once**, so you can work with those numbers more easily.

## Details of specific output files

### sourmash outputs

Primary outputs:

* `{outdir}/gather/{sample}.gather.csv` - CSV output of `sourmash gather`
* `{outdir}/gather/{sample}.gather.out` - human-readable output of `sourmash gather`
* `{outdir}/gather/{sample}.gather.with-lineages.csv` - gather CSV annotated with taxonomy

Interim outputs that are used or summarized elsewhere:

* `{outdir}/gather/{sample}.prefetch.csv` - CSV output of `sourmash prefetch`
* `{outdir}/gather/{sample}.genomes.info.csv` - summary information on matching genomes
* `{outdir}/gather/{sample}.prefetch.report.txt` - summary of prefetch information
* `{outdir}/gather/{sample}.known.sig.gz` - known sourmash hashes
* `{outdir}/gather/{sample}.unknown.sig.gz` - unknown sourmash hashes

### mapping outputs

#### `mapping/` and `leftover/` subdirectory files

`{sample_id}.summary.csv` - summary of the mapping. See below for details.

* `{sample_id}.x.{genome_id}.bam` - output of mapping
* `{sample_id}.x.{genome_id}.depth.txt` - output of `samtools depth`
* `{sample_id}.x.{genome_id}.count_mapped_reads.txt` - output of `samtools view -c`
* `{sample_id}.x.{genome_id}.leftover.fq.gz` - reads remaining after reads from earlier-rank gather results are mapped **(only in `mapping/` subdirectory)**
* `{sample_id}.x.{genome_id}.mapped.fq.gz` - all of the mapped reads
* `{sample_id}.x.{genome_id}.overlap.fq.gz` - ...
* `{sample_id}.x.{genome_id}.bcf` - output of `samtools mpileup` and `samtools call` (BCF file)
* `{sample_id}.x.{genome_id}.vcf.gz` - output of `samtools mpileup` and `samtools call` (VCF file)
* `{sample_id}.x.{genome_id}.vcf.gz.csi` - ancillary output of `samtools mpileup` and `samtools call`

#### mapping summary file: `{metagenome}.summary.csv` in `/mapping/` and `/leftover/`

these files are produced by `genome_grist/summarize_mapping.py` and contains one row for each genome in `{metagenome}`, with the following columns:

* `index` - index column unique to each row.  Equivalent to `genome_id`.
* `genome_id` - genome identifier.
* `sample_id` - metagenome/sample identifier.
* `n_chrom` - number of contigs in the genome.
* `n_snps` - number of SNPs in the genome relative to the metagenome reads (as called by `samtools call`).
* `n_genome_bp` - size of genome in bp.
* `n_missed_bp` - the number of positions in the genome with 0 coverage.
* `f_missed_bp` - the fraction of the genome that has no matches: `missed` / `genome_bp`.
* `avg_coverage` - average coverage of genome; includes bases with 0 coverage.
* `effective_coverage` - sum of depth divided by number of covered bases; does not include bases with 0 coverage.
* `n_covered_bp` - the number of bp covered by at least one read.
* `f_covered_bp` - fraction of bp covered by at least one read, aka read-mapping-based "detection".
* `n_mapped_reads` - total count of primary mapped reads.
