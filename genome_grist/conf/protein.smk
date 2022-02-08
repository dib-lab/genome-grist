### rules for protein workflow ###
#import snakemake
#import os, csv, tempfile, shutil, sys


# joint rules:
# - smash reads
# - prefetch
# - gather

## protein-specific rules **protein mapping workflow should be entirely independent of k-mer workflow -- could use protein
# mapping with DNA matches if desired, same with protein matches --> DNA mapping
# - download proteomes
# - prodigal translate if no proteome?
# - IF paired end: merge reads (BBmerge allows interleaved input; PEAR does not)
    #name: bbtools-env
    #channels:
    #   - conda-forge
    #   - bioconda
    #   - defaults
    #dependencies:
    #   - bbmap=38.93

# index proteomes for mapping
# paladin:  v1.4.6
# - paladin map reads --> protein reference
# - protein mapping report (prot gather vs paladin mapping, etc)
#--> this can basically copy the dna mapping report
# DNA VS PROT report
# --> can we interconvert #hashes/kmers. == bp_equivalent?
# protein-bp * 3 = dna-bp. get all on same plot?
# do we want to run protein _after_ running the dna?
# --> how would you remove 'known' reads? Could do it post dna mapping, but is there a way to do it w/kmers alone?
# potential k-mer way: translate "known" k-mers (single frame), intersect with protein k-mer sig; remove matching hashes?

# bbmerge reads
rule bbmerge_paired_reads_wc:
    input: 
        interleaved = ancient(outdir + '/trim/{sample}.trim.fq.gz'),
    output:
        merged = protected(outdir + '/merge_reads/{sample}.merged.fq.gz'),
        unmerged = protected(outdir + '/merge_reads/{sample}.unmerged.fq.gz'),
        insert_size_hist = protected(outdir + '/merge_reads/{sample}.insert-size-histogram.txt'),
    conda: 'env/bbmap.yml'
    threads: 6
    resources:
        mem_mb = int(ABUNDTRIM_MEMORY / 1e6),
    params:
        mem = ABUNDTRIM_MEMORY,
    shell: """
            bbmerge.sh -t {threads} -Xmx {params.mem} in={input} \
            out={output.merged} outu={output.unmerged} \
            ihist={output.ihist}
    """

# download proteomes from genbank if they exist
rule download_matching_proteome_wc:
    input:
        csvfile = ancient(f'{GENBANK_CACHE}/{{ident}}.info.csv')
    output:
        proteome = f"{GENBANK_CACHE}/proteomes/{{ident}}_protein.faa.gz"
    run:
        with open(input.csvfile, 'rt') as infp:
            r = csv.DictReader(infp)
            rows = list(r)
            assert len(rows) == 1
            row = rows[0]
            ident = row['ident']
            assert wildcards.ident.startswith(ident)
            url = row['protein_url']
            url = row['genome_url']
            #name = row['ncbi_tax_name']
            name = row['display_name']

            print(f"downloading proteome for ident {ident}/{name} from NCBI...",
                file=sys.stderr)
            with open(output.proteome, 'wb') as outfp:
                try:
                    with urllib.request.urlopen(url) as response:
                        content = response.read()
                        outfp.write(content)
                        print(f"...wrote {len(content)} bytes to {output.proteome}",
                              file=sys.stderr)
                except:
                    shell('touch {output}')
