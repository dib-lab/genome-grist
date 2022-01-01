#! /usr/bin/env python
import sys
import argparse
import gzip
from collections import defaultdict


def main():
    p = argparse.ArgumentParser()
    p.add_argument('vcf_gz')
    args = p.parse_args()

    by_pos = defaultdict(dict)
    n_lines = 0
    with gzip.open(args.vcf_gz, 'rt') as fp:
        for line in fp:
            if line.startswith('#'):
                continue

            n_lines += 1
            chrom, pos, ident, ref, alt, qual, *rest = line.split('\t')
            # skip indels for now
            if len(ref) > 1 or len(alt) > 1:
                continue

            pos = int(pos)
            by_pos[chrom][pos] = 1

    print(f"num lines: {n_lines}")
    print(f"num chrom: {len(by_pos)}")

    total = 0
    for chrom in by_pos:
        total += len(chrom)

    print(f"num snps: {total}")


if __name__ == '__main__':
    sys.exit(main())
