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
    p.add_argument('query_sig')
    p.add_argument('known_sig')
    p.add_argument('unknown_sig')

    p.add_argument("-k", "--ksize", type=int, default=31, help="ksize for analysis")
    p.add_argument("--moltype", default="DNA", help="molecule type for analysis")
    p.add_argument("--scaled", default=None, help="sourmash scaled value for analysis")
    p.add_argument("--report", help="output signature breakdown information in CSV")
    args = p.parse_args()

    ksize = args.ksize
    moltype = args.moltype

    query_sig = sourmash.load_one_signature(args.query_sig,
                                            ksize=ksize,
                                            select_moltype=moltype)
    known_sig = sourmash.load_one_signature(args.known_sig)
    unknown_sig = sourmash.load_one_signature(args.unknown_sig)

    query_mh = query_sig.minhash
    known_mh = known_sig.minhash
    unknown_mh = unknown_sig.minhash

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
