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
import gzip
import contextlib

def main():
    p = argparse.ArgumentParser()
    p.add_argument('genome_files', nargs='+')
    p.add_argument('-o', '--output-csv', required=True)
    p.add_argument('-d', '--output-directory', required=True)
    p.add_argument('--sym', required=False, action= 'store_true')
    args = p.parse_args()
    
    # Create directory if does not exist
    try:
        os.makedirs(args.output_directory)
    except FileExistsError:
        pass

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

        ident, *remainder = record_name.split(' ', 1)
        if remainder:           # is list, needs to be string
            remainder = remainder[0]
        else:
            remainder = ident

        print(f"read identifer '{ident}' and name '{remainder}'")

        is_gzipped = False
        with contextlib.suppress(OSError):
            with gzip.open(filename) as fp:
                fp.read(1)
                is_gzipped = True

        destfile = os.path.join(args.output_directory, f"{ident}_genomic.fna.gz")
        
        
        if args.sym and not is_gzipped:
            print("--sym option requires the FASTA files to be already gzipped.", file=sys.stderr)
            sys.exit(-1)
        
        if args.sym and is_gzipped:
            print(f"symbolic linking '{filename}' to '{destfile}'")
            _src = os.path.abspath(filename)
            _dst = os.path.abspath(destfile)
            if os.path.islink(_dst):
                print(f"symlink {_dst} already exists, consider removing it first.", file=sys.stderr)
                sys.exit(1)
            os.symlink(_src, _dst)
        elif is_gzipped:
            print(f"copying '{filename}' to '{destfile}'")
            shutil.copyfile(filename, destfile)
        else:
            print(f"compressing '{filename}' into '{destfile}'")
            with open(filename, 'rb') as fp:
                with gzip.open(destfile, 'w') as outfp:
                    outfp.write(fp.read())

        w.writerow(dict(ident=ident, display_name=remainder,
                        genome_filename=destfile))
        n += 1

    output_fp.close()
    print('---')
    print(f"wrote {n} genome entries to '{args.output_csv}'")

    return 0

if __name__ == '__main__':
    sys.exit(main())
