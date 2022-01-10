#! /usr/bin/env python
"""
Scan a list of genome files and prepare a draft "info file" for genome-grist
to use as a private database info file.
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

    try:
        os.mkdir(args.output_directory)
    except FileExistsError:
        pass

    output_fp = open(args.output_csv, 'wt')
    w = csv.DictWriter(output_fp, fieldnames=['acc',
                                              'ncbi_tax_name',
                                              'filename',
                                              'info_filename'])

    w.writeheader()

    for filename in args.genome_files:
        print(f"reading from '{filename}'", file=sys.stderr)

        for record in screed.open(filename):
            record_name = record.name
            break

        record_name = record_name.split(' ', 1)
        acc, remainder = record_name

        destfile = os.path.join(args.output_directory,
                                f"{acc}_genomic.fna.gz")
        shutil.copyfile(filename, destfile)
        print(f"copying to '{destfile}'")

        # write .info.csv too - this should probably be separated out to
        # run separately, and have it be based on this output CSVs info!
        info_filename = os.path.join(args.output_directory,
                                     f"{acc}.info.csv")
        with open(info_filename, 'wt') as fp:
            w2 = csv.DictWriter(fp, fieldnames=['acc',
                                               'ncbi_tax_name'])
            w2.writeheader()
            w2.writerow(dict(acc=acc, ncbi_tax_name=remainder))

        w.writerow(dict(acc=acc, ncbi_tax_name=remainder,
                        filename=destfile,
                        info_filename=info_filename))

    output_fp.close()

    return 0

if __name__ == '__main__':
    sys.exit(main())
