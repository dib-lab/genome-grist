"Enable python -m genome_grist.click"
import sys
import os
import subprocess

import click

from genome_grist.version import version

def get_snakefile_path(name):
    thisdir = os.path.dirname(__file__)
    snakefile = os.path.join(thisdir, "conf", name)
    return snakefile


def get_package_configfile(filename):
    thisdir = os.path.dirname(__file__)
    configfile = os.path.join(thisdir, "conf", filename)
    return configfile


def run_snakemake(
    configfile,
    no_use_conda=False,
    verbose=False,
    snakefile_name="Snakefile",
    outdir=None,
    config_params=[],
    extra_args=[],
):
    # find the Snakefile relative to package path
    snakefile = get_snakefile_path(snakefile_name)

    # basic command
    cmd = ["snakemake", "-s", snakefile]

    # snakemake sometimes seems to want a default -j; set it to 1 for now.
    # can overridden later on command line.
    cmd += ["-j", "1"]

    # add --use-conda
    if not no_use_conda:
        cmd += ["--use-conda"]

    # add rest of snakemake arguments
    cmd += list(extra_args)

    # add config params, and --outdir
    if outdir:
        config_params = list(config_params)
        config_params.append(f"outdir={outdir}")

    if config_params:
        cmd += ["--config", *config_params]

    # add configfile - try looking for it a few different ways.
    configfiles = [
        get_package_configfile("defaults.conf"),
        get_package_configfile("system.conf"),
    ]
    if configfile:
        if os.path.isfile(configfile):
            configfiles.append(configfile)
        elif os.path.isfile(get_package_configfile(configfile)):
            configfiles.append(get_package_configfile(configfile))
        else:
            for suffix in ".yaml", ".conf":
                tryfile = configfile + suffix
                if os.path.isfile(tryfile):
                    configfiles.append(tryfile)
                    break

                tryfile = get_package_configfile(tryfile)
                if os.path.isfile(tryfile):
                    configfiles.append(tryfile)
                    break

        if len(configfiles) == 2:
            raise ValueError(f"cannot find config file '{configfile}'")

    cmd += ["--configfile"] + configfiles

    if verbose:
        print("final command:", cmd)

    # runme
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f"Error in snakemake invocation: {e}", file=sys.stderr)
        return e.returncode

    return 0


#
# actual command line functions
#


@click.group()
def cli():
    pass


# create a run subcommand that by default passes all of its arguments
# on to snakemake (after setting Snakefile and config)
@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("configfile")
@click.option("--no-use-conda", is_flag=True, default=False)
@click.option("--verbose", is_flag=True)
@click.option("--outdir", nargs=1)
@click.option("-h", "--help", nargs=0)
@click.argument("snakemake_args", nargs=-1)
def run(configfile, snakemake_args, no_use_conda, verbose, outdir, help):
    "execute genome-grist workflow (using snakemake underneath)"
    targets = [ arg for arg in snakemake_args if not arg.startswith('-') ]
    if help or not targets:
        #CTB: note, this should match what's in README, please :)
        print(f"""
This is genome-grist v{version}.

Usage:

   genome-grist run <conf file> <target> [ <target 2>... ] [ <snakemake args> ]

Recommended targets:

 * summarize_gather - produce summary reports on metagenome composition
 * summarize_tax - produce summary reports on taxonomic composition
 * summarize_mapping - produce summary reports on k-mer and read mapping

Note, 'summarize_mapping' includes 'summarize_gather'; reports will be
in {{outdir}}/reports, where 'outdir' is specified in the config file.

Additional intermediate targets:

 * download_reads - download SRA metagenomes specified in conf file
 * trim_reads - do basic read trimming/adapter removal for metagenome reads
 * smash_reads - create sourmash signatures from metagenome reads
 * summarize_sample_info - build a info.yaml summary file for each metagenome
 * gather_reads - run 'sourmash gather' on metagenomes against Genbank
 * download_genbank_genomes - download all matching Genbank genomes
 * map_reads - map all metagenome reads to Genbank genomes
 * make_sgc_conf - make a spacegraphcats config file

Please see https://github.com/dib-lab/genome-grist for quickstart docs.

Please post questions at https://github.com/dib-lab/genome-grist/issues!
""")
        sys.exit(0)

    ret = run_snakemake(
        configfile,
        snakefile_name="Snakefile",
        no_use_conda=no_use_conda,
        verbose=verbose,
        extra_args=snakemake_args,
        outdir=outdir,
    )
    sys.exit(ret)


# 'check' command
@click.command()
@click.argument("configfile")
def check(configfile):
    "check configuration"
    sys.exit(run_snakemake(configfile, extra_args=["check"]))


# 'showconf' command
@click.command()
@click.argument("configfile")
def showconf(configfile):
    "show full configuration"
    sys.exit(run_snakemake(configfile, extra_args=["showconf"]))


# 'info' command
@click.command()
def info():
    "provide basic install/config file info"
    from .version import version

    print(
        f"""
This is genome-grist version v{version}

Package install path: {os.path.dirname(__file__)}
snakemake Snakefile: {get_snakefile_path('Snakefile')}
"""
    )


cli.add_command(run)
cli.add_command(check)
cli.add_command(showconf)
cli.add_command(info)


def main():
    cli()


if __name__ == "__main__":
    main()
