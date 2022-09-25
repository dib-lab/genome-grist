#! /usr/bin/env python
"""
Summarize mapping depth information (produced by samtools depth -aa {bamfile}).
Also summarize SNP counts from VCF file.
"""
import argparse
import sys
import pandas as pd
import os
import gzip
from collections import defaultdict


def summarize_vcf(vcf_gz):
    "Count number of distinct SNP locations"
    by_pos = defaultdict(dict)
    n_lines = 0
    with gzip.open(vcf_gz, 'rt') as fp:
        for line in fp:
            # skip comments
            if line.startswith('#'):
                continue

            n_lines += 1
            chrom, pos, ident, ref, alt, qual, *rest = line.split('\t')

            # skip indels for now
            if len(ref) > 1 or len(alt) > 1:
                continue

            pos = int(pos)
            by_pos[chrom][pos] = 1

    n_chrom = len(by_pos)

    n_snps = 0
    for chrom in by_pos:
        n_snps += len(by_pos[chrom])

    return n_lines, n_chrom, n_snps


def main():
    p = argparse.ArgumentParser()
    p.add_argument('sample_name')

    # take in multiple depth.txt files and then below we figure out
    # the names of the vcf.gz and count_mapped_reads.txt files.
    # this is a little clunky but seems to be the simplest way to
    # avoid complicated argument passing.
    p.add_argument('depth_txts', nargs='+',
                   help='output of samtools depth -aa {bamfile}')
    p.add_argument('-o', '--output', required=True, help='output CSV file')
    args = p.parse_args()

    sample = args.sample_name
    runs = {}
    for n, depth_txt in enumerate(args.depth_txts):
        # figure out the names/paths of the other required files -
        assert depth_txt.endswith('.depth.txt')
        prefix = depth_txt[:-len('.depth.txt')]
        vcf_gz = prefix + '.vcf.gz'
        assert os.path.exists(vcf_gz)
        mapcount = prefix + '.count_mapped_reads.txt'
        assert os.path.exists(mapcount)

        print(f"reading from '{vcf_gz}'", file=sys.stderr)
        _, n_chrom, n_snps = summarize_vcf(vcf_gz)

        print(f"reading from '{mapcount}", file=sys.stderr)
        with open(mapcount, 'rt') as fp:
            lines = fp.readlines()
            assert len(lines) == 1
            line = lines[0].strip()
            n_mapped_reads = int(line)

        print(f"reading from '{depth_txt}", file=sys.stderr)

        data = pd.read_table(depth_txt, names=["contig", "pos", "coverage"])

        filename = os.path.basename(depth_txt)
        sample_check, _, genome_id, *rest = filename.split(".")

        assert sample_check == sample, (sample_check, sample)

        d = {}
        d['n_chrom'] = n_chrom
        d['n_snps'] = n_snps

        value_counts = data['coverage'].value_counts()
        d['n_genome_bp'] = int(len(data))
        d['n_missed_bp'] = int(value_counts.get(0, 0))
        d['f_missed_bp'] = d['n_missed_bp'] / d['n_genome_bp']

        covered_bp = d['n_genome_bp'] - d['n_missed_bp']
        d['n_covered_bp'] = covered_bp
        d['f_covered_bp'] = covered_bp / d['n_genome_bp']

        # average over all (incl uncovered) bases:
        sum_coverage = data['coverage'].sum()
        d['avg_coverage'] = sum_coverage / len(data)

        # only average over covered bases
        d['effective_coverage'] = sum_coverage / covered_bp

        # store identifier info etc.
        d['genome_id'] = genome_id
        d['sample_id'] = sample

        # track num mapped_reads
        d['n_mapped_reads'] = n_mapped_reads

        # common sense checks, b/c math is hard
        assert d['n_missed_bp'] + d['n_covered_bp'] == d['n_genome_bp']
        assert round(d['f_covered_bp'] + d['f_missed_bp'], 3) == 1
        if d['n_missed_bp'] == 0:
            assert d['effective_coverage'] == d['avg_coverage']

        # store for output.
        runs[genome_id] = d

    # convert dictionary into CSV via a pandas DataFrame.
    pd.DataFrame(runs).T.to_csv(args.output, index_label="index")
    print(f"Wrote CSV to {args.output}", file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
