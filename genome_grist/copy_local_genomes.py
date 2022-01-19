#! /usr/bin/env python
"""
Copy private genomes into a new directory, properly named; create a summary
CSV for genome-grist.
"""
import sys
import argparse
import screed
import csv
import os
import shutil


def main():
    p = argparse.ArgumentParser()
    p.add_argument('genome_files', nargs='+')
    p.add_argument('-o', '--output-csv', required=True)
    p.add_argument('-d', '--output-directory', required=True)
    args = p.parse_args()

    output_fp = open(args.output_csv, 'wt')
    w = csv.DictWriter(output_fp, fieldnames=['ident',
                                              'display_name',
                                              'genome_filename'])
    w.writeheader()

    try:
        os.mkdir(args.output_directory)
        print(f"Created genome directory '{args.output_directory}'")
    except FileExistsError:
        print(f"Genome directory '{args.output_directory}' already exists.")

    print(f"Copying genomes into '{args.output_directory}'")

    n = 0
    for filename in args.genome_files:
        print(f"---")
        print(f"processing genome '{filename}'")

        for record in screed.open(filename):
            record_name = record.name
            break

        record_name = record_name.split(' ', 1)
        ident, remainder = record_name

        print(f"read identifer '{ident}' and name '{remainder}'")

        destfile = os.path.join(args.output_directory, f"{ident}_genomic.fna.gz")
        print(f"copying '{filename}' to '{destfile}'")
        shutil.copyfile(filename, destfile)

        w.writerow(dict(ident=ident, display_name=remainder,
                        genome_filename=destfile))
        n += 1

    output_fp.close()
    print('---')
    print(f"wrote {n} genome entries to '{args.output_csv}'")

    return 0

if __name__ == '__main__':
    sys.exit(main())
