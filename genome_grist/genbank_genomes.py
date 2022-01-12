#! /usr/bin/env python
"""
Retrieve genome information for genbank genomes.
"""
import sys
import argparse
import urllib.request
import csv

from lxml import etree


def url_for_accession(accession):
    accsplit = accession.strip().split("_")
    assert len(accsplit) == 2, f"ERROR: '{accession}' should have precisely one underscore!"

    db, acc = accsplit
    if '.' in acc:
        number, version = acc.split(".")
    else:
        number, version = acc, '1'
    number = "/".join([number[p : p + 3] for p in range(0, len(number), 3)])
    url = f"https://ftp.ncbi.nlm.nih.gov/genomes/all/{db}/{number}"
    print(f"opening directory: {url}", file=sys.stderr)

    with urllib.request.urlopen(url) as response:
        all_names = response.read()

    print("done!", file=sys.stderr)

    all_names = all_names.decode("utf-8")

    full_name = None
    for line in all_names.splitlines():
        if line.startswith(f'<a href='):
            name=line.split('"')[1][:-1]
            db_, acc_, *_ = name.split("_")
            if db_ == db and acc_.startswith(acc):
                full_name = name
                break

    if full_name is None:
        return None
    else:
        url = "htt" + url[3:]
        return (
            f"{url}/{full_name}/{full_name}_genomic.fna.gz",
            f"{url}/{full_name}/{full_name}_assembly_report.txt",
        )


def get_taxid_from_assembly_report(url):
    print(f"opening assembly report: {url}", file=sys.stderr)
    with urllib.request.urlopen(url) as response:
        content = response.read()
    print("done!", file=sys.stderr)

    content = content.decode("utf-8").splitlines()
    for line in content:
        if "Taxid:" in line:
            line = line.strip()
            pos = line.find("Taxid:")
            assert pos >= 0
            pos += len("Taxid:")
            taxid = line[pos:]
            taxid = taxid.strip()
            return taxid

    assert 0


def get_tax_name_for_taxid(taxid):
    tax_url = (
        f"https://www.ncbi.nlm.nih.gov/taxonomy/?term={taxid}&report=taxon&format=text"
    )
    print(f"opening tax url: {tax_url}", file=sys.stderr)
    with urllib.request.urlopen(tax_url) as response:
        content = response.read()

    print("done!", file=sys.stderr)

    root = etree.fromstring(content)
    notags = etree.tostring(root).decode("utf-8")
    if notags.startswith("<pre>"):
        notags = notags[5:]
    if notags.endswith("</pre>"):
        notags = notags[:-6]
    notags = notags.strip()

    return notags


def main():
    p = argparse.ArgumentParser()
    p.add_argument("accession")
    p.add_argument("-o", "--output")
    args = p.parse_args()

    fieldnames = ["ident", "genome_url", "assembly_report_url", "display_name"]
    fp = None
    if args.output:
        fp = open(args.output, "wt")
        w = csv.DictWriter(fp, fieldnames=fieldnames)
    else:
        w = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    w.writeheader()

    ident = args.accession

    genome_url, assembly_report_url = url_for_accession(ident)
    taxid = get_taxid_from_assembly_report(assembly_report_url)
    tax_name = get_tax_name_for_taxid(taxid)

    d = dict(
        ident=ident,
        genome_url=genome_url,
        assembly_report_url=assembly_report_url,
        display_name=tax_name,
    )

    w.writerow(d)
    print(f"retrieved for {ident} - {tax_name}", file=sys.stderr)

    if fp:
        fp.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
