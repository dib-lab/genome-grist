# https://www.ebi.ac.uk/ena/browser/view/SRR606249
SAMPLES = ['SRR606249']
GENOMES = ['2', '63', '47']

rule all:
    input:
        expand("inputs/raw/{sample}_1.fastq.gz", sample = SAMPLES),
        expand("outputs/trim/{sample}_R1.trim.fq.gz", sample=SAMPLES),
        expand("outputs/abundtrim/{sample}.abundtrim.fq.gz", sample=SAMPLES),
        expand("outputs/minimap/{s}.x.{g}.bam", s=SAMPLES, g=GENOMES),
        expand("outputs/minimap/depth/{s}.x.{g}.txt", s=SAMPLES, g=GENOMES),
        expand("outputs/minimap/{s}.x.{g}.mapped.fastq", s=SAMPLES, g=GENOMES),
        expand("outputs/minimap/{s}.x.{g}.read-names.txt", s=SAMPLES, g=GENOMES),

rule download_reads:
    output: 
        r1='inputs/raw/{sample}_1.fastq.gz',
        r2='inputs/raw/{sample}_2.fastq.gz'
    shell:'''
    wget -O {output.r1} ftp://ftp.ebi.ac.uk/vol1/fastq/SRR606/SRR606249/SRR606249_1.fastq.gz
    wget -O {output.r2} ftp://ftp.ebi.ac.uk/vol1/fastq/SRR606/SRR606249/SRR606249_2.fastq.gz
    '''

rule adapter_trim:
    input:
        r1 = "inputs/raw/{sample}_1.fastq.gz",
        r2 = 'inputs/raw/{sample}_2.fastq.gz',
        adapters = 'inputs/adapters.fa'
    output:
        r1 = 'outputs/trim/{sample}_R1.trim.fq.gz',
        r2 = 'outputs/trim/{sample}_R2.trim.fq.gz',
        o1 = 'outputs/trim/{sample}_o1.trim.fq.gz',
        o2 = 'outputs/trim/{sample}_o2.trim.fq.gz'
    conda: 'env.yml'
    shell:'''
     trimmomatic PE {input.r1} {input.r2} \
             {output.r1} {output.o1} {output.r2} {output.o2} \
             ILLUMINACLIP:{input.adapters}:2:0:15 MINLEN:25  \
             LEADING:2 TRAILING:2 SLIDINGWINDOW:4:2
    '''

rule kmer_trim_reads:
    input: 
        "outputs/trim/{sample}_R1.trim.fq.gz", 
        "outputs/trim/{sample}_R2.trim.fq.gz"
    output: "outputs/abundtrim/{sample}.abundtrim.fq.gz"
    conda: 'env.yml'
    shell:'''
    interleave-reads.py {input} | 
        trim-low-abund.py -C 3 -Z 18 -M 30e9 -V - -o {output}
    '''

rule minimap:
    output:
        bam="outputs/minimap/{sra_id}.x.{g}.bam",
    input:
        query = "inputs/genomes/{g}.fa.gz",
        metagenome = "outputs/abundtrim/{sra_id}.abundtrim.fq.gz",
    conda: "env-minimap2.yml"
    threads: 4
    shell: """
        minimap2 -ax sr -t {threads} {input.query} {input.metagenome} | \
            samtools view -b -F 4 - | samtools sort - > {output.bam}
    """

rule samtools_fastq:
    output:
        mapped="outputs/minimap/{bam}.mapped.fastq",
    input:
        bam="outputs/minimap/{bam}.bam",
    conda: "env-minimap2.yml"
    threads: 4
    shell: """
        samtools bam2fq {input.bam} > {output.mapped}
    """

rule samtools_depth:
    output:
        depth="outputs/minimap/depth/{bam}.txt",
    input:
        bam="outputs/minimap/{bam}.bam",
    conda: "env-minimap2.yml"
    threads: 4
    shell: """
        samtools depth -aa {input.bam} > {output.depth}
    """

rule read_names:
    output:
        names="outputs/minimap/{bam}.read-names.txt",
    input:
        mapped="outputs/minimap/{bam}.mapped.fastq",
    run:
        import screed
        with open(output.names, 'wt') as fp:
           for record in screed.open(input.mapped):
              fp.write(f"{record.name}\n")
