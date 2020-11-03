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
def test_something():
    global _tempdir

    os.mkdir(os.path.join(_tempdir, 'abundtrim'))
    os.mkdir(os.path.join(_tempdir, 'big'))
    
    abundtrim_dir = os.path.join(_tempdir, 'abundtrim')
    shutil.copy(utils.relative_file('tests/test-data/twofoo-head.abundtrim.fq.gz'),
                abundtrim_dir)

    shutil.copy(utils.relative_file('tests/test-data/twofoo-head.x.genbank.gather.csv'),
                os.path.join(_tempdir, 'big/twofoo-head.x.genbank.gather.csv'))

    conf = utils.relative_file("conf-twofoo-head.yml")
    target = "download_matching_genomes"
    status = run_snakemake(
        conf, verbose=True, outdir=_tempdir, extra_args=[target],
        no_use_conda=True,
    )
    assert status == 0
    #assert os.path.exists(os.path.join(_tempdir, target))
