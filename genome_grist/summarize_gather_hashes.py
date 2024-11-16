#! /usr/bin/env python
"""
For a signature split into known/unknown, print out / save stats.
"""
import sys
import argparse
import copy
import csv

import sourmash
from sourmash import sourmash_args
from sourmash.logging import notify


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--query-sig', required=True)
    p.add_argument('--picklist', required=True)
    p.add_argument('--db', required=True)

    p.add_argument("-k", "--ksize", type=int, default=31, help="ksize for analysis")
    p.add_argument("--moltype", default="DNA", help="molecule type for analysis")
    p.add_argument("--scaled", default=None, help="sourmash scaled value for analysis")
    p.add_argument("--report", help="output signature breakdown information in CSV")
    args = p.parse_args()

    ksize = args.ksize
    moltype = args.moltype

    query_sig = sourmash.load_file_as_signatures(args.query_sig,
                                                 ksize=ksize,
                                                 select_moltype=moltype)
    query_sig = list(query_sig)
    assert len(query_sig) == 1
    query_sig = query_sig[0]

    db = sourmash.load_file_as_index(args.db)

    picklist = sourmash_args.load_picklist(args)
    db = db.select(ksize=ksize, moltype=moltype, picklist=picklist)

    query_mh = query_sig.minhash

    # iterate over matches and merge into one sketch
    known_mh = query_mh.copy_and_clear()
    print(f"merging {len(db)} signatures")
    for sig in db.signatures():
        known_mh += sig.minhash

    known_mh = query_mh.flatten().intersection(known_mh.flatten())
    #known_mh = known_mh.inflate(query_mh)
    unknown_mh = query_mh.flatten().copy().to_mutable()
    unknown_mh.remove_many(known_mh)
    #unknown_mh = unknown_mh.inflate(query_mh)

    assert query_mh.ksize == known_mh.ksize
    assert query_mh.moltype == known_mh.moltype
    assert known_mh.scaled == unknown_mh.scaled

    query_mh = query_mh.downsample(scaled=known_mh.scaled)

    assert len(query_mh) == len(known_mh) + len(unknown_mh)

    p_known = len(known_mh) / len(query_mh) * 100
    print(f"{len(known_mh)} known hashes of {len(query_mh)} total ({p_known:.1f}% known, {100-p_known:.1f}% unknown).")

    if args.report:
        print(f"reporting stats to '{args.report}'")
        with open(args.report, 'wt') as fp:
            w = csv.writer(fp)
            w.writerow(["total_hashes", "known_hashes", "unknown_hashes",
                        "scaled", "moltype", "ksize"])
            w.writerow([len(query_mh),
                        len(known_mh),
                        len(unknown_mh),
                        query_mh.scaled,
                        query_mh.moltype,
                        query_mh.ksize
                        ])

    return 0


if __name__ == "__main__":
    sys.exit(main())
