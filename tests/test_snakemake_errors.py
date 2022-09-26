"Tests snakemake execution via click CLI module."
import pytest
import tempfile
import shutil
import os
import yaml
import sourmash
import contextlib
import io

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

    trim_dir = os.path.join(_tempdir, "trim")
    os.mkdir(trim_dir)

    conf = utils.relative_file('tests/test-data/SRR5950647_subset-nomatches.conf')
    src = utils.relative_file("tests/test-data/SRR5950647_subset.trim.fq.gz")
    shutil.copy(src, trim_dir)

    extra_args = ["smash_reads"]
    pinfo = run_snakemake(
        conf,
        verbose=True,
        outdir=_tempdir,
        extra_args=extra_args,
    )
    assert pinfo.returncode == 0

    output_sig = f"{_tempdir}/sigs/SRR5950647_subset.trim.sig.zip"
    assert os.path.exists(output_sig)
    sigs = list(sourmash.load_file_as_signatures(output_sig))
    assert len(sigs) == 3
    for s in sigs:
        assert s.minhash.track_abundance


@pytest.mark.dependency(depends=["test_smash_sig"])
def test_gather_reads_nomatches():
    # run gather_reads, => no matches - should provide error.
    global _tempdir

    conf = utils.relative_file('tests/test-data/SRR5950647_subset-nomatches.conf')
    extra_args = ["gather_reads"]

    pinfo = run_snakemake(
        conf,
        verbose=True,
        outdir=_tempdir,
        extra_args=extra_args,
        subprocess_args=dict(text=True, capture_output=True)
    )

    assert pinfo.returncode != 0

    print('STDOUT:', pinfo.stdout)
    print('STDERR:', pinfo.stderr)

    assert "DB is tests/test-data/SRR5950647-genomes/acidulo.zip" in pinfo.stdout
    assert "** ERROR: prefetch didn't find anything for sample 'SRR5950647_subset'." in pinfo.stdout
