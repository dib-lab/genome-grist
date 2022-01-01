#! /usr/bin/env python
"""
Summarize mapping depth information (produced by samtools depth -aa {bamfile}).
"""
import argparse
import sys
import pandas as pd
import os


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
        print(f'reading from {depth_txt}', file=sys.stderr)

        data = pd.read_table(depth_txt, names=["contig", "pos", "coverage"])

        filename = os.path.basename(depth_txt)
        sample_check, _, genome_id, *rest = filename.split(".")

        assert sample_check == sample, (sample_check, sample)

        d = {}
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
        d['covered_bp'] = (1 - d['percent missed']/100.0) * d['genome bp']
        d['genome_id'] = genome_id
        d['sample_id'] = sample

        runs[genome_id] = d

    pd.DataFrame(runs).T.to_csv(args.output)
    print(f"Wrote CSV to {args.output}", file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
