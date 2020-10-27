#! /usr/bin/env python
"""
TODO:
* only get filenames for accs that are not already in output
"""
import sys
import argparse
import urllib.request

def url_for_accession(accession):
    db, acc = accession.strip().split("_")
    number, version = acc.split(".")
    number = "/".join([number[pos:pos + 3] for pos in range(0, len(number), 3)])
    url = f"ftp://ftp.ncbi.nlm.nih.gov/genomes/all/{db}/{number}"

    with urllib.request.urlopen(url) as response:
        all_names = response.read()

    all_names = all_names.decode('utf-8')

    full_name = None
    for line in all_names.splitlines():
        name = line.split()[-1]
        db_, acc_, *_ = name.split("_")
        if db_ == db and acc == acc_:
            full_name = name
            break

    if full_name is None:
        return None
    else:
        url = "https" + url[3:]
        return f"{url}/{full_name}/{full_name}_genomic.fna.gz"


def main():
    p = argparse.ArgumentParser()
    p.add_argument('accession_file')
    args = p.parse_args()

    for n, acc in enumerate(open(args.accession_file, 'rt')):
        url = url_for_accession(acc)
        print(f'{acc.rstrip()},{url}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
