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

#
# NOTE re common output directory - all of these tests run with the same
# output dir.
#

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
    # run 'smash_reads'
    global _tempdir

    abundtrim_dir = os.path.join(_tempdir, "abundtrim")
    os.mkdir(abundtrim_dir)

    conf = utils.relative_file('tests/test-data/SRR5950647_subset.conf')
    src = utils.relative_file("tests/test-data/SRR5950647_subset.abundtrim.fq.gz")
    shutil.copy(src, abundtrim_dir)

    extra_args = ["smash_reads"]
    status = run_snakemake(
        conf,
        verbose=True,
        outdir=_tempdir,
        extra_args=extra_args,
    )
    assert status == 0

    output_sig = f"{_tempdir}/sigs/SRR5950647_subset.abundtrim.sig"
    assert os.path.exists(output_sig)
    sigs = list(sourmash.load_file_as_signatures(output_sig))
    assert len(sigs) == 3
    for s in sigs:
        assert s.minhash.track_abundance


@pytest.mark.dependency(depends=["test_smash_sig"])
def test_summarize_sample_info():
    # run summarize_sample_info
    global _tempdir

    conf = utils.relative_file('tests/test-data/SRR5950647_subset.conf')
    test_data = utils.relative_file("tests/test-data")

    extra_args = ["summarize_sample_info"]
    status = run_snakemake(
        conf,
        verbose=True,
        outdir=_tempdir,
        extra_args=extra_args,
    )
    assert status == 0

    info_file = f"{_tempdir}/SRR5950647_subset.info.yaml"
    assert os.path.exists(info_file)

    with open(info_file, 'rt') as fp:
        info = yaml.safe_load(fp)

    print('XXX', info)
    #{'kmers': 928685, 'known_hashes': 807, 'n_bases': 2276334, 'n_reads': 24663, 'sample': 'HSMA33MX-subset', 'total_hashes': 907, 'unknown_hashes': 100}

    assert info['kmers'] == 928685
    assert info['sample'] == 'SRR5950647_subset'
    assert info['known_hashes'] == 653
    assert info['n_bases'] == 2276334
    assert info['n_reads'] == 24663
    assert info['total_hashes'] == 907
    assert info['unknown_hashes'] == 254


@pytest.mark.dependency(depends=["test_summarize_sample_info"])
def test_map_reads():
    global _tempdir

    conf = utils.relative_file('tests/test-data/SRR5950647_subset.conf')
    test_data = utils.relative_file("tests/test-data")

    genomes_dir = os.path.join(_tempdir, "genomes")
    os.mkdir(genomes_dir)

    extra_args = ["map_reads", "-j", "4"]
    status = run_snakemake(
        conf,
        verbose=True,
        outdir=_tempdir,
        extra_args=extra_args,
    )
    assert status == 0


@pytest.mark.dependency(depends=["test_map_reads"])
def test_gather_to_tax():
    # run gather_to_tax
    global _tempdir

    conf = utils.relative_file('tests/test-data/SRR5950647_subset.conf')
    test_data = utils.relative_file("tests/test-data")

    extra_args = ["gather_to_tax"]
    status = run_snakemake(
        conf,
        verbose=True,
        outdir=_tempdir,
        extra_args=extra_args,
    )
    assert status == 0
    
    tax_output = f"{_tempdir}/gather/SRR5950647_subset.gather.with-lineages.csv"
    assert os.path.exists(tax_output)

    tax_results = list(utils.load_csv(tax_output))
    assert len(tax_results) == 2


@pytest.mark.dependency(depends=["test_smash_sig"])
def test_gather_reads_with_picklist():
    # check gather with picklist
    global _tempdir

    conf = utils.relative_file('tests/test-data/SRR5950647_picklist.conf')
    test_data = utils.relative_file("tests/test-data")

    # note: the prefetch command & CSV are what are actually limited by the
    # passed in picklist.
    prefetch_output = f"{_tempdir}/gather/SRR5950647_subset.prefetch.csv"
    if os.path.exists(prefetch_output):
        os.unlink(prefetch_output)

    gather_output = f"{_tempdir}/gather/SRR5950647_subset.gather.csv"
    if os.path.exists(gather_output):
        os.unlink(gather_output)

    extra_args = ["gather_reads"]
    status = run_snakemake(
        conf,
        verbose=True,
        outdir=_tempdir,
        extra_args=extra_args,
    )
    assert status == 0
    
    assert os.path.exists(gather_output)

    prefetch_results = list(utils.load_csv(prefetch_output))
    assert len(prefetch_results) == 1
    assert prefetch_results[0]['match_name'].startswith('GCF_902167755.1 ')

    gather_results = list(utils.load_csv(gather_output))
    assert len(gather_results) == 1
    assert gather_results[0]['name'].startswith('GCF_902167755.1 ')

    # make sure the picklist version of the CSVs is cleaned up!
    os.unlink(prefetch_output)
    os.unlink(gather_output)


def test_bad_config_1():
    # check for presence of sourmash_database_glob_pattern, old config
    global _tempdir

    conf = utils.relative_file('tests/test-data/bad-1.conf')

    status = run_snakemake(conf, verbose=True, outdir=_tempdir,
                           extra_args=["check"])

    assert status != 0


def test_bad_config_2():
    # check for presence of 'sample' instead of 'samples', old config
    global _tempdir

    conf = utils.relative_file('tests/test-data/bad-2.conf')

    status = run_snakemake(conf, verbose=True, outdir=_tempdir,
                           extra_args=["check"])

    assert status != 0


def test_bad_config_3():
    # check for presence of 'database_taxonomy' instead of 'taxonomies',
    # old config
    global _tempdir

    conf = utils.relative_file('tests/test-data/bad-3.conf')

    status = run_snakemake(conf, verbose=True, outdir=_tempdir,
                           extra_args=["check"])

    assert status != 0


def test_bad_config_4():
    # check for presence of 'taxonomies' as a string, not a list.
    # old config
    global _tempdir

    conf = utils.relative_file('tests/test-data/bad-4.conf')

    status = run_snakemake(conf, verbose=True, outdir=_tempdir,
                           extra_args=["check"])

    assert status != 0
