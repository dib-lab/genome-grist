#! /usr/bin/env python
import argparse
import sys
import csv


def main():
    p = argparse.ArgumentParser()
    p.add_argument('mf_in', help='input manifest')
    p.add_argument('--idents', required=True)
    p.add_argument('-o', '--output', help='output manifest', required=True)
    args = p.parse_args()

    if not args.idents.strip():
        # do nothing
        idents = set()
    else:
        idents = set(args.idents.split(','))
    print(f'remove_idents_from_manifest: loaded: {len(idents)} idents to remove.')
    
    found = set()
    n_read = 0
    n_written = 0

    with open(args.mf_in, 'r', newline='') as fp:
        outfp = open(args.output, 'w', newline='')

        version = fp.readline().strip()
        print(version, file=outfp)

        r = csv.DictReader(fp)
        w = csv.DictWriter(outfp, fieldnames=r.fieldnames)
        w.writeheader()

        for row in r:
            n_read += 1
            name = row['name']
            ident = name.split(' ')[0]

            if n_read == 1:     # on first row...
                print('example ident found in manifest:', ident)

            if ident in idents:
                found.add(ident)
                continue        # skip

            w.writerow(row)
            n_written += 1

    outfp.close()

    print(f'read {n_read} rows')
    print(f'wrote {n_written} rows')
    print(f'found {len(found)} idents of {len(idents)} total.')

    if idents != found:
        missing = idents - found
        print(f'ERROR: missing {len(missing)} idents in IGNORE_IDENTS.',
              file=sys.stderr)
        print('* ', "\n* ".join(missing), file=sys.stderr)
        sys.exit(-1)
    else:
        print('remove_idents_from_manifest: SUCCESS!')


if __name__ == '__main__':
    sys.exit(main())
