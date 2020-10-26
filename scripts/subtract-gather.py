#! /usr/bin/env python
import screed
import argparse
import sys
import gzip
import csv
import os


def read_readnames(filename):
    with open(filename, 'rt') as fp:
        names = [ x.strip() for x in fp ]

    return set(names)


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('gather_csv')
    args = p.parse_args()

    sample_id = os.path.basename(args.gather_csv).split('.')[0]

    print(f'reading gather results from {args.gather_csv}')
    rows = []
    with open(args.gather_csv, 'rt') as fp:
        r = csv.DictReader(fp)
        for row in r:
            rows.append(row)
    print(f'...loaded {len(rows)} results total.')

    print(f'checking input/output pairs:')
    pairs = []
    fail = False
    for row in rows:
        acc = row['name'].split('_')[:2]
        acc = '_'.join(acc)

        filename = f'outputs/minimap/{sample_id}.x.{acc}.mapped.fq.gz'
        outfile = f'outputs/minimap/{sample_id}.x.{acc}.leftover.fq.gz'

        if not os.path.exists(filename):
            print(f'ERROR: input filename {filename} does not exist. Will exit.')
            fail = True

        pairs.append((acc, filename, outfile))

    if fail:
        print(f'Some required input files not found - exiting.')
        sys.exit(-1)

    ignore_reads = set()
    for (acc, filename, outfile) in pairs:
        fp = gzip.open(outfile, 'wt')

        print(f'reading sequences from {filename};')
        print(f'writing remaining to {outfile}')
        n_wrote = 0
        for record in screed.open(filename):
            if record.name in ignore_reads:
                continue
            ignore_reads.add(record.name)

            fp.write(f'@{record.name}\n{record.sequence}\n+\n{record.quality}\n')
            n_wrote += 1

        print(f'wrote {n_wrote} records for {sample_id}.x.{acc};')
        print(f'{len(ignore_reads)} total reads to ignore moving forward.')

    return 0


if __name__ == '__main__':
    sys.exit(main())
