"Tests snakemake execution via click CLI module."
import pytest
import tempfile
import shutil
import os
import yaml
import sourmash

from genome_grist.__main__ import run_snakemake
from . import pytest_utils as utils

# NOTE re dependencies (@pytest.mark.dependency):
# - These basically duplicate the snakemake dependencies.
# - they're there for convenience, because...
# - ...if these are wrong, the tests will still succeed, they just may
#   do some extra work in some tests & take longer.


def setup_module(m):
    global _tempdir
    _tempdir = tempfile.mkdtemp(prefix="genome_grist_test")


def teardown_module(m):
    global _tempdir
    try:
        shutil.rmtree(_tempdir, ignore_errors=True)
    except OSError:
        pass


@pytest.mark.dependency()
def test_smash_sig():
    global _tempdir

    abundtrim_dir = os.path.join(_tempdir, "abundtrim")
    os.mkdir(abundtrim_dir)

    conf = utils.relative_file('tests/test-data/SRR5950647.subset.conf')
    src = utils.relative_file("tests/test-data/SRR5950647.subset.abundtrim.fq.gz")
    shutil.copy(src, abundtrim_dir)

    extra_args = ["smash_reads"]
    status = run_snakemake(
        conf,
        verbose=True,
        outdir=_tempdir,
        extra_args=extra_args,
    )
    assert status == 0

    output_sig = f"{_tempdir}/sigs/SRR5950647.subset.abundtrim.sig"
    assert os.path.exists(output_sig)
    sigs = list(sourmash.load_file_as_signatures(output_sig))
    assert len(sigs) == 3
    for s in sigs:
        assert s.minhash.track_abundance


@pytest.mark.dependency(depends=["test_smash_sig"])
def test_summarize_sample_info():
    global _tempdir

    conf = utils.relative_file('tests/test-data/SRR5950647.subset.conf')
    test_data = utils.relative_file("tests/test-data")

    extra_args = ["summarize_sample_info"]
    status = run_snakemake(
        conf,
        verbose=True,
        outdir=_tempdir,
        extra_args=extra_args,
    )
    assert status == 0

    info_file = f"{_tempdir}/SRR5950647.subset.info.yaml"
    assert os.path.exists(info_file)

    with open(info_file, 'rt') as fp:
        info = yaml.safe_load(fp)

    print('XXX', info)
    #{'kmers': 928685, 'known_hashes': 807, 'n_bases': 2276334, 'n_reads': 24663, 'sample': 'HSMA33MX-subset', 'total_hashes': 907, 'unknown_hashes': 100}

    assert info['kmers'] == 928685
    assert info['sample'] == 'SRR5950647.subset'
    assert info['known_hashes'] == 653
    assert info['n_bases'] == 2276334
    assert info['n_reads'] == 24663
    assert info['total_hashes'] == 907
    assert info['unknown_hashes'] == 254


@pytest.mark.dependency(depends=["test_summarize_sample_info"])
def test_map_reads():
    global _tempdir

    conf = utils.relative_file('tests/test-data/SRR5950647.subset.conf')
    test_data = utils.relative_file("tests/test-data")

    genomes_dir = os.path.join(_tempdir, "genomes")
    os.mkdir(genomes_dir)

    cplist = (
        ("SRR5950647-GCF_003697165.2_genomic.fna.gz", "GCF_003697165.2_genomic.fna.gz"),
        ("SRR5950647-GCF_902167755.1_genomic.fna.gz", "GCF_902167755.1_genomic.fna.gz"),
    )
    cplist = ()

    for src, dest in cplist:
        frompath = os.path.join(test_data, src)
        topath = os.path.join(genomes_dir, dest)
        shutil.copyfile(frompath, topath)

    extra_args = ["map_reads", "-j", "4"]
    status = run_snakemake(
        conf,
        verbose=True,
        outdir=_tempdir,
        extra_args=extra_args,
    )
    assert status == 0
