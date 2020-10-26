import glob, os, csv

#SAMPLE='SRR606249'
SAMPLE='p8808mo11'
#SAMPLE='p8808mo9'
GATHER_CSV=f'outputs/big/{SAMPLE}.x.genbank.gather.csv'

sourmash_db = 'all-gather-genomes.sbt.zip'


#gather_csv = ['outputs/big/p8808mo11.x.genbank.gather.csv',
#              'outputs/big/p8808mo9.x.genbank.gather.csv',
#              '']

mapping_targets = []
with open(GATHER_CSV, 'rt') as fp:
   r = csv.DictReader(fp)
   for row in r:
      acc = row['name'].split(' ')[0]
      mapping_targets.append(f'outputs/minimap/{SAMPLE}.x.{acc}.bam')


# load in all the genomes; this could be changed to a more targeted approach!
acc_to_genome = {}
for filename in glob.glob('genomes/*.fna.gz'):
    basename = os.path.basename(filename)
    acc = basename.split('_')[:2]
    acc = '_'.join(acc)
    acc_to_genome[acc] = filename

genome_accs = []
with open(GATHER_CSV, 'rt') as fp:
   r = csv.DictReader(fp)
   for row in r:
      acc = row['name'].split(' ')[0]
      genome_accs.append(acc)

if 'GCA_002160645.1' in genome_accs:
    genome_accs.remove('GCA_002160645.1')

def input_acc_to_genome(w):
    return acc_to_genome[w.acc]



rule all:
    input:
        expand(f"outputs/minimap/{SAMPLE}.x.{{acc}}.mapped.fq.gz",
               acc=genome_accs),
        expand(f"outputs/leftover/{SAMPLE}.x.{{acc}}.bam",
               acc=genome_accs),
        f"outputs/minimap/depth/{SAMPLE}.summary.csv",
        f"outputs/leftover/depth/{SAMPLE}.summary.csv"


rule zip:
    shell: """
        zip -r transfer.zip outputs/leftover/depth/*.summary.csv \
                outputs/minimap/depth/*.summary.csv \
                outputs/*.gather.csv
    """


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
    conda: 'env/trim.yml'
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
    conda: 'env/trim.yml'
    shell:'''
    interleave-reads.py {input} | 
        trim-low-abund.py -C 3 -Z 18 -M 30e9 -V - -o {output}
    '''

rule minimap:
    output:
        bam="outputs/minimap/{sra_id}.x.{acc}.bam",
    input:
        query = input_acc_to_genome,
        metagenome = "outputs/abundtrim/{sra_id}.abundtrim.fq.gz",
    conda: "env/minimap2.yml"
    threads: 4
    shell: """
        minimap2 -ax sr -t {threads} {input.query} {input.metagenome} | \
            samtools view -b -F 4 - | samtools sort - > {output.bam}
    """

rule samtools_fastq:
    output:
        mapped="outputs/minimap/{bam}.mapped.fq.gz",
    input:
        bam="outputs/minimap/{bam}.bam",
    conda: "env/minimap2.yml"
    threads: 4
    shell: """
        samtools bam2fq {input.bam} | gzip > {output.mapped}
    """

rule samtools_depth:
    output:
        depth="outputs/{dir}/depth/{bam}.txt",
    input:
        bam="outputs/{dir}/{bam}.bam",
    conda: "env/minimap2.yml"
    shell: """
        samtools depth -aa {input.bam} > {output.depth}
    """

rule summarize_samtools_depth:
    output: f"outputs/{{dir}}/depth/{SAMPLE}.summary.csv"
    input:
        expand("outputs/{{dir}}/depth/{s}.x.{g}.txt",
               s=SAMPLE, g=genome_accs)
    run:
        import pandas as pd

        runs = {}
        for sra_stat in input:
            print(f'reading from {sra_stat}...')
            data = pd.read_table(sra_stat, names=["contig", "pos", "coverage"])
            sra_id = sra_stat.split("/")[-1].split(".")[0]
            genome_id = sra_stat.split("/")[-1].split(".")[2]

            d = {}
            value_counts = data['coverage'].value_counts()
            d['genome bp'] = int(len(data))
            d['missed'] = int(value_counts.get(0, 0))
            d['percent missed'] = 100 * d['missed'] / d['genome bp']
            d['coverage'] = data['coverage'].sum() / len(data)
            d['genome_id'] = genome_id
            d['sample_id'] = sra_id
            runs[genome_id] = d

        pd.DataFrame(runs).T.to_csv(output[0])


rule sourmash_reads:
    input:
        metagenome = "outputs/abundtrim/{sra_id}.abundtrim.fq.gz",
    output:
        sig = "outputs/sigs/{sra_id}.abundtrim.sig"
    conda: "env/sourmash.yml"
    shell: """
        sourmash compute -k 21,31,51 --scaled=1000 {input} -o {output} \
           --name {wildcards.sra_id} --track-abundance
    """


rule sourmash_gather_reads:
    input:
        sig = "outputs/sigs/{sra_id}.abundtrim.sig",
        db = sourmash_db,
    output:
        csv = "outputs/{sra_id}.gather.csv",
        out = "outputs/{sra_id}.gather.out",
    conda: "env/sourmash.yml"
    shell: """
        sourmash gather {input.sig} {input.db} -o {output.csv} > {output.out}
    """


# @CTB update subtract-gather to take sample ID as param
rule extract_leftover_reads:
    input:
        csv = GATHER_CSV,
        reads = expand(f"outputs/minimap/{SAMPLE}.x.{{acc}}.mapped.fq.gz",
                       acc=genome_accs),
    output:
        expand(f"outputs/minimap/{SAMPLE}.x.{{acc}}.leftover.fq.gz",
               acc=genome_accs),
    conda: "env/sourmash.yml"
    shell: """
        scripts/subtract-gather.py {input.csv}
    """


rule map_leftover_reads:
    output:
        bam="outputs/leftover/{sra_id}.x.{acc}.bam",
    input:
        query = input_acc_to_genome,
        reads = "outputs/minimap/{sra_id}.x.{acc}.leftover.fq.gz",
    conda: "env/minimap2.yml"
    threads: 4
    shell: """
        minimap2 -ax sr -t {threads} {input.query} {input.reads} | \
            samtools view -b -F 4 - | samtools sort - > {output.bam}
    """

rule sourmash_gather_reads_podar:
    input:
        sig = "outputs/sigs/SRR606249.abundtrim.sig",
        db = 'test.sbt.zip'
    output:
        csv = "outputs/big/SRR606249.x.podar.gather.csv"
    conda: "env/sourmash.yml"
    shell: """
        sourmash gather {input.sig} {input.db} -o {output.csv}
    """

rule sourmash_gather_reads_genbank:
    input:
        sig = "outputs/sigs/SRR606249.abundtrim.sig",
        db = glob.glob('/home/irber/sourmash_databases/outputs/sbt/genbank-*x1e5*k31*')
    output:
        csv = "outputs/big/SRR606249.x.genbank.gather.csv",
        matches = "outputs/big/SRR606249.x.genbank.gather.sig",
    conda: "env/sourmash.yml"
    shell: """
        sourmash gather {input.sig} {input.db} -o {output.csv} --save-matches {output.matches}
    """

rule sourmash_gather_reads_ter1:
    input:
        sig = "/home/tereiter/github/2020-ibd/outputs/sigs/p8808mo11.sig",
        db = glob.glob('/home/irber/sourmash_databases/outputs/sbt/genbank-*x1e5*k31*')
    output:
        csv = "outputs/big/p8808mo11.x.genbank.gather.csv",
        matches = "outputs/big/p8808mo11.x.genbank.gather.sig"
    conda: "env/sourmash.yml"
    shell: """
        sourmash gather {input.sig} {input.db} -o {output.csv} --save-matches {output.matches}
    """

rule sourmash_gather_reads_ter2:
    input:
        sig = "/home/tereiter/github/2020-ibd/outputs/sigs/p8808mo9.sig",
        db = glob.glob('/home/irber/sourmash_databases/outputs/sbt/genbank-*x1e5*k31*')
    output:
        csv = "outputs/big/p8808mo9.x.genbank.gather.csv",
        matches = "outputs/big/p8808mo9.x.genbank.gather.sig"
    conda: "env/sourmash.yml"
    shell: """
        sourmash gather {input.sig} {input.db} -o {output.csv} --save-matches {output.matches}
    """
