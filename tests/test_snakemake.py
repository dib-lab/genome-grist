"Tests snakemake execution via click CLI module."
import pytest
import tempfile
import shutil
import os

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

    abundtrim_dir = os.path.join(_tempdir, 'abundtrim')
    os.mkdir(abundtrim_dir)

    src = utils.relative_file('tests/test-data/HSMA33MX-subset.abundtrim.fq.gz')
    shutil.copy(src, abundtrim_dir)

    config_params = ["sample=HSMA33MX-subset"]
    extra_args = ["smash_reads"]
    status = run_snakemake(
        'conf.yml', verbose=True, outdir=_tempdir, extra_args=extra_args,
        config_params=config_params
     )
    assert status == 0

    assert os.path.exists(f"{_tempdir}/sigs/HSMA33MX-subset.abundtrim.sig")
