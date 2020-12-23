#! /usr/bin/env python
"""
Prefetch results from a large database, to then run gather on.
"""
import sys
import argparse
import copy

import sourmash
from sourmash import sourmash_args
from sourmash.logging import notify


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--db", nargs="+", action="append", help="one or more databases to use"
    )
    p.add_argument(
        "--query",
        nargs="*",
        default=[],
        action="append",
        help="one or more signature files to use as queries",
    )
    p.add_argument("--save-matches", required=True)
    p.add_argument("--output-unassigned")
    p.add_argument("--threshold-bp", type=float, default=1e5)
    p.add_argument("-k", "--ksize", type=int, default=31)
    p.add_argument("--moltype", default="DNA")
    args = p.parse_args()

    # flatten --db and --query lists
    args.db = [item for sublist in args.db for item in sublist]
    args.query = [item for sublist in args.query for item in sublist]

    ksize = args.ksize
    moltype = args.moltype

    # build one big query:
    query_sigs = []
    for query_file in args.query:
        sigs = sourmash_args.load_file_as_signatures(query_file, ksize=ksize,
                                                     select_moltype=moltype)
        query_sigs.extend(sigs)

    if not len(query_sigs):
        notify("ERROR: no query signatures loaded!?")
        sys.exit(-1)

    mh = query_sigs[0].minhash
    for query_sig in query_sigs[1:]:
        mh += query_sig.minhash

    if not mh.scaled:
        notify("ERROR: must use scaled signatures.")
        sys.exit(-1)

    unident_mh = copy.copy(mh)

    notify(f"Loaded {len(mh.hashes)} hashes from {len(query_sigs)} query signatures.")

    # iterate over signatures in db one at a time, for each db;
    # find those with any kind of containment.
    keep = []
    n = 0
    for db in args.db:
        print('\nloading signatures from db:', db)
        for sig in sourmash_args.load_file_as_signatures(db, ksize=ksize,
                                                      select_moltype=moltype):
            n += 1
            db_mh = sig.minhash.downsample(scaled=mh.scaled)
            common = mh.count_common(db_mh)
            if common:
                # check scaled here?
                if common * mh.scaled >= args.threshold_bp:
                    keep.append(sig)
                    unident_mh.remove_many(db_mh.hashes)

            if n % 10 == 0:
                notify(f"{n} searched, {len(keep)} matches.", end="\r")

    notify(f"{n} searched, {len(keep)} matches.")

    if args.save_matches:
        notify('saving all matches to "{}"', args.save_matches)
        with sourmash_args.FileOutput(args.save_matches, "wt") as fp:
            sourmash.save_signatures(keep, fp)

    if args.output_unassigned:
        notify('saving unidentified hashes to "{}"', args.output_unassigned)
        ss = sourmash.SourmashSignature(unident_mh)
        with open(args.output_unassigned, "wt") as fp:
            sourmash.save_signatures([ss], fp)

    return 0


if __name__ == "__main__":
    sys.exit(main())
