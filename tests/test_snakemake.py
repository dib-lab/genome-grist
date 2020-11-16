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


@pytest.mark.dependency(depends=["test_smash_sig"])
def test_map_reads():
    global _tempdir

    test_data = utils.relative_file("tests/test-data")

    cplist = ("HSMA33MX-subset.genomes.accs.txt",
              "HSMA33MX-subset.genomes.info.csv",
              "HSMA33MX-subset.x.genbank.gather.csv",
              "HSMA33MX-subset.x.genbank.gather.out",
              "HSMA33MX-subset.x.genbank.matches.sig")

    genbank_dir = os.path.join(_tempdir, 'genbank')
    os.mkdir(genbank_dir)

    for src in cplist:
        shutil.copyfile(os.path.join(test_data, src),
                        os.path.join(genbank_dir, src))
    

    cplist = (("HSMA33MX-GCA_001881345.1.fna.gz", "GCA_001881345.1.fna.gz"),
              ("HSMA33MX-GCA_009494275.1.fna.gz", "GCA_009494275.1.fna.gz"),)

    genomes_dir = os.path.join(_tempdir, 'genomes')
    os.mkdir(genomes_dir)

    for src, dest in cplist:
        shutil.copyfile(os.path.join(test_data, src),
                        os.path.join(genomes_dir, dest))
    
    
    config_params = ["sample=HSMA33MX-subset"]
    extra_args = ["map_reads", "-j", "4"]
    status = run_snakemake(
        'conf.yml', verbose=True, outdir=_tempdir, extra_args=extra_args,
        config_params=config_params
     )
    assert status == 0
