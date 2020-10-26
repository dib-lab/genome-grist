# genome-grist - download genomes from NCBI, and map metagenomes to them

(1) download a metagenome
(2) process it into trimmed reads, and make a [sourmash signature](https://sourmash.readthedocs.io/)
(3) search the sourmash signature with 'gather' against sourmash databases, e.g. all of genbank
(4) download the matching genomes from genbank
(5) map all metagnome reads to genomes using minimap
(6) extract matching reads iteratively based on gather, successively eliminating reads that matched to previous gather matches
(7) run mapping on “leftover” reads to genomes
(8) summarize all mapping results for comparison and graphing

## Leftover text

[podar ref genomes](https://osf.io/vbhy5/download)

[Snakefile based on @luizirber code](https://github.com/luizirber/phd/blob/ed2d89769bd6908a5f28a7b8415d2bcdc509e2bb/experiments/wort/sra_search/Snakefile)

