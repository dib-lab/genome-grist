#! /usr/bin/env python
"""
For a signature and a set of matches from prefetch_gather, split the
signature into a collection of known and unknown hashes.
"""
import sys
import argparse
import copy

import sourmash
from sourmash import sourmash_args
from sourmash.logging import notify


def main():
    p = argparse.ArgumentParser()
    p.add_argument('query_file')
    p.add_argument('matches_db')
    p.add_argument('known_out')
    p.add_argument('unknown_out')

    p.add_argument("-k", "--ksize", type=int, default=31)
    p.add_argument("--moltype", default="DNA")
    p.add_argument("--scaled", default=None)
    args = p.parse_args()

    ksize = args.ksize
    moltype = args.moltype

    # build one big query:
    query_sig = sourmash_args.load_query_signature(args.query_file, ksize,
                                                    moltype)

    query_mh = query_sig.minhash

    if not query_mh.scaled:
        notify("ERROR: must use scaled signatures.")
        sys.exit(-1)

    if args.scaled:
        scaled = int(args.scaled)
        notify(f"Downsampling query from scaled={query_mh.scaled} to {scaled}")
        query_mh = query_mh.downsample(scaled=int(scaled))

    unknown_mh = copy.copy(query_mh)

    notify(f"Loaded {len(query_mh.hashes)} hashes from '{args.query_file}'")

    # iterate over signatures in matches one at a time, for each db;
    # find those with any kind of containment.
    m = 0
    n = 0
    print(f"\nloading signatures from '{args.matches_db}'")

    try:
        for sig in sourmash_args.load_file_as_signatures(args.matches_db,
                                                         ksize=ksize,
                                                         select_moltype=moltype):
            n += 1
            db_mh = sig.minhash.downsample(scaled=query_mh.scaled)
            common = unknown_mh.count_common(db_mh)
            if common:
                m += 1
                unknown_mh.remove_many(db_mh.hashes)

            if n % 100 == 0:
                notify(f"{n} searched, {m} matches.", end="\r")
    except OSError:
        notify("WARNING: no matching signatures to load!")

    notify(f"{n} searched, {m} matches.")

    print('xxx', len(query_mh))
    known_hashes = set(query_mh.hashes)
    print('xyx', len(unknown_mh))
    known_hashes -= set(unknown_mh.hashes)

    known_mh = query_mh.copy_and_clear()
    known_mh.add_many(known_hashes)

    p_known = len(known_mh) / len(query_mh) * 100
    print(f"{len(known_mh)} known hashes of {len(query_mh)} total ({p_known:.1f}% known, {100-p_known:.1f}% unknown).")

    with sourmash_args.FileOutput(args.known_out, 'wt') as fp:
        print(f"saving known hashes to '{args.known_out}'")
        ss = sourmash.SourmashSignature(known_mh)
        sourmash.save_signatures([ss], fp)

    with sourmash_args.FileOutput(args.unknown_out, 'wt') as fp:
        print(f"saving unknown hashes '{args.unknown_out}'")
        ss = sourmash.SourmashSignature(unknown_mh)
        sourmash.save_signatures([ss], fp)

    return 0


if __name__ == "__main__":
    sys.exit(main())
