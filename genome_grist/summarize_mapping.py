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
    p.add_argument('depth_txts', nargs='+',
                   help='output of samtools depth -aa {bamfile}')
    p.add_argument('-o', '--output', required=True, help='output CSV file')
    args = p.parse_args()

    sample = args.sample_name
    runs = {}
    for n, depth_txt in enumerate(args.depth_txts):
        assert depth_txt.endswith('.depth.txt')
        vcf_gz = depth_txt[:-len('.depth.txt')] + '.vcf.gz'
        assert os.path.exists(vcf_gz)
        print(f"reading from '{vcf_gz}'", file=sys.stderr)
        _, n_chrom, n_snps = summarize_vcf(vcf_gz)

        print(f"reading from '{depth_txt}", file=sys.stderr)

        data = pd.read_table(depth_txt, names=["contig", "pos", "coverage"])

        filename = os.path.basename(depth_txt)
        sample_check, _, genome_id, *rest = filename.split(".")

        assert sample_check == sample, (sample_check, sample)

        d = {}
        d['n_chrom'] = n_chrom
        d['n_snps'] = n_snps

        value_counts = data['coverage'].value_counts()
        d['genome bp'] = int(len(data))
        d['missed'] = int(value_counts.get(0, 0))
        d['percent missed'] = 100 * d['missed'] / d['genome bp']
        d['coverage'] = data['coverage'].sum() / len(data)
        if d['missed'] != 0:
            uniq_cov = d['coverage'] / (1 - d['missed'] / d['genome bp'])
            d['unique_mapped_coverage'] = uniq_cov
        else:
            d['unique_mapped_coverage'] = d['coverage']
        covered_bp = (1 - d['percent missed']/100.0) * d['genome bp']
        d['covered_bp'] = round(covered_bp + 0.5)
        d['genome_id'] = genome_id
        d['sample_id'] = sample

        runs[genome_id] = d

    pd.DataFrame(runs).T.to_csv(args.output)
    print(f"Wrote CSV to {args.output}", file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
