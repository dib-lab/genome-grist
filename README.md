# genome-grist - map Illumina metagenomes to GenBank genomes

(1) download a metagenome
(2) process it into trimmed reads, and make a [sourmash signature](https://sourmash.readthedocs.io/)
(3) search the sourmash signature with 'gather' against sourmash databases, e.g. all of genbank
(4) download the matching genomes from genbank
(5) map all metagenome reads to genomes using minimap - `map_reads` and `extract_mapped_reads`
(6) extract matching reads iteratively based on gather, successively eliminating reads that matched to previous gather matches - `extract_gather`
(7) run mapping on “leftover” reads to genomes - `map_gather`
(8) summarize all mapping results for comparison and graphing - `summarize_gather`

## Why the name `grist`?

In the sourmash family of names (sourmash, wort, distillerycats, etc.)

NOT:
https://en.wikipedia.org/wiki/Grist_(computing)

THIS:
https://en.wikipedia.org/wiki/Grist

## Leftover text

[podar ref genomes](https://osf.io/vbhy5/download)

[Snakefile based on @luizirber code](https://github.com/luizirber/phd/blob/ed2d89769bd6908a5f28a7b8415d2bcdc509e2bb/experiments/wort/sra_search/Snakefile)

[Genome URL generation code](https://github.com/dib-lab/sourmash_databases/pull/11/files#diff-3b4f98e8183094e86c5e5492ec95fb7cb078de369b41be91d061940474ce80e5R118-R139)

[download SRA code](https://github.com/luizirber/phd/blob/ed2d89769bd6908a5f28a7b8415d2bcdc509e2bb/experiments/wort/sra_search/Snakefile)
