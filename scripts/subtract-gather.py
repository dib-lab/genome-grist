#! /usr/bin/env python
import screed
import argparse
import sys
import gzip
import csv


def read_readnames(filename):
    with open(filename, 'rt') as fp:
        names = [ x.strip() for x in fp ]

    return set(names)


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('gather_csv')
    args = p.parse_args()

    print(f'reading gather results from {args.gather_csv}')
    rows = []
    with open(args.gather_csv, 'rt') as fp:
        r = csv.DictReader(fp)
        for row in r:
            rows.append(row)
    print(f'...loaded {len(rows)} results total.')

    ignore_reads = set()
    for row in rows:
        num = row['name'].split('.')[0]
        filename = f'outputs/minimap/SRR606249.x.{num}.mapped.fq.gz'
        outfile = f'outputs/minimap/SRR606249.x.{num}.leftover.fq.gz'
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

        print(f'wrote {n_wrote} records for {num};')
        print(f'{len(ignore_reads)} total reads to ignore moving forward.')

    return 0


if __name__ == '__main__':
    sys.exit(main())
