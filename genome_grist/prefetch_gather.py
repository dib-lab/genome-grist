#! /usr/bin/env python
import sys
import argparse
import copy

import sourmash
from sourmash import sourmash_args
from sourmash.logging import notify, error


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db', nargs='+', action='append',
                   help='one or more databases to use')
    p.add_argument('--query', nargs='*', default=[], action='append',
                   help='one or more signature files to use as queries')
    p.add_argument('--save-matches', required=True)
    p.add_argument('--output-unassigned')
    p.add_argument('--threshold-bp', type=float, default=1e5)
    args = p.parse_args()

    # flatten --db and --query lists
    args.db = [item for sublist in args.db for item in sublist]
    args.query = [item for sublist in args.query for item in sublist]

    # build one big query:
    query_sigs = []
    for query_file in args.query:
        query_sigs.extend(sourmash_args.load_file_as_signatures(query_file,
                                                                ksize=31))

    mh = query_sigs[0].minhash
    for query_sig in query_sigs[1:]:
        mh += query_sig.minhash

    unident_mh = copy.copy(mh)

    notify(f'Loaded {len(mh.hashes)} hashes from {len(query_sigs)} query signatures.')

    # iterate over signatures in one at a time
    keep = []
    n = 0
    for db in args.db:
        for sig in sourmash_args.load_file_as_signatures(db, ksize=31):
            n += 1
            common = mh.count_common(sig.minhash)
            if common:
                # check scaled...
                if common * mh.scaled >= args.threshold_bp:
                    keep.append(sig)
                    unident_mh.remove_many(sig.minhash.hashes)

            if n % 10 == 0:
                notify(f'{n} searched, {len(keep)} matches.', end='\r')

    notify(f'{n} searched, {len(keep)} matches.')

    if keep and args.save_matches:
        notify('saving all matches to "{}"', args.save_matches)
        with sourmash_args.FileOutput(args.save_matches, 'wt') as fp:
            sourmash.save_signatures(keep, fp)

    if args.output_unassigned:
        notify('saving unidentified hashes to "{}"', args.output_unassigned)
        ss = sourmash.SourmashSignature(unident_mh)
        with open(args.output_unassigned, 'wt') as fp:
            sourmash.save_signatures([ ss ], fp)

    return 0


if __name__ == '__main__':
    sys.exit(main())
