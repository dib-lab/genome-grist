#! /usr/bin/env python
"""
Scan a list of genome files and create individual "info file" CSVs
for genome-grist to use for private genomes.
"""
import sys
import argparse
import screed
import csv
import os
import shutil


def main():
    p = argparse.ArgumentParser()
    p.add_argument('info_csv')
    args = p.parse_args()

    info_d = {}
    with open(args.info_csv, 'r', newline="") as fp:
        r = csv.DictReader(fp)
        for row in r:
            ident = row['ident']
            info_d[ident] = row

    print(f"loaded {len(info_d)} info files from '{args.info_csv}'")

    n = 0
    for ident, item_d in info_d.items():
        # write .info.csv.
        dirname = os.path.dirname(item_d['genome_filename'])
        info_filename = os.path.join(dirname, f"{ident}.info.csv")
        name = item_d['display_name']

        with open(info_filename, 'wt') as fp:
            w2 = csv.DictWriter(fp, fieldnames=['ident',
                                                'display_name'])
            w2.writeheader()
            w2.writerow(dict(ident=ident, display_name=name))
        print(f"Created info CSV '{info_filename}'")

        n += 1

    print(f"wrote {n} info files.")

    return 0

if __name__ == '__main__':
    sys.exit(main())
