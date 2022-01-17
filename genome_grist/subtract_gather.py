#! /usr/bin/env python
import screed
import argparse
import sys
import gzip
import csv
import os


def read_readnames(filename):
    with open(filename, "rt") as fp:
        names = [x.strip() for x in fp]

    return set(names)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("sample_id")
    p.add_argument("gather_csv")
    p.add_argument("--outdir", default="outputs")
    args = p.parse_args()

    sample_id = args.sample_id
    outdir = args.outdir.rstrip("/")

    print(f"reading gather results from {args.gather_csv}")
    rows = []
    with open(args.gather_csv, "rt") as fp:
        r = csv.DictReader(fp)
        for row in r:
            rows.append(row)
    print(f"...loaded {len(rows)} results total.")

    print("checking input/output pairs:")
    pairs = []
    fail = False
    for row in rows:
        acc = row["name"].split(" ")[0]

        filename = f"{outdir}/mapping/{sample_id}.x.{acc}.mapped.fq.gz"
        overlapping = f"{outdir}/mapping/{sample_id}.x.{acc}.overlap.fq.gz"
        leftover = f"{outdir}/mapping/{sample_id}.x.{acc}.leftover.fq.gz"

        if not os.path.exists(filename):
            print(f"ERROR: input filename {filename} does not exist. Will exit.")
            fail = True

        pairs.append((acc, filename, overlapping, leftover))

    if fail:
        print("Some required input files not found - exiting.")
        sys.exit(-1)

    ignore_reads = set()
    for n, (acc, filename, overlapping, leftover) in enumerate(pairs):
        overlap_fp = gzip.open(overlapping, "wt")
        leftover_fp = gzip.open(leftover, "wt")

        print('-'*30)
        print(f"reading sequences from {filename};")
        print(f"writing overlapping to {overlapping}")
        print(f"writing remaining to {leftover}")

        n_wrote = 0
        screed_fp = screed.open(filename)
        for record in screed_fp:
            fq = f"@{record.name}\n{record.sequence}\n+\n{record.quality}\n"
            if record.name in ignore_reads:
                overlap_fp.write(fq)
            else:
                ignore_reads.add(record.name)
                leftover_fp.write(fq)
            n_wrote += 1
        screed_fp.close()

        print(f"wrote {n_wrote} leftover records for {sample_id}.x.{acc};")
        print(f"{len(ignore_reads)} total reads to ignore moving forward.")
        print(f"file {n+1} of {len(pairs)} total")

        overlap_fp.close()
        leftover_fp.close()

    # <-- here is where we can go through the input reads and output unmapped.
    # (OR, save 'ignore_reads' and let another script handle it.)

    return 0


if __name__ == "__main__":
    sys.exit(main())
