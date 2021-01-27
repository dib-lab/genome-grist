"Enable python -m genome_grist.click"
import sys
import os
import subprocess

import click


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
@click.argument("snakemake_args", nargs=-1)
def run(configfile, snakemake_args, no_use_conda, verbose, outdir):
    "execute genome-grist workflow (using snakemake underneath)"
    run_snakemake(
        configfile,
        snakefile_name="Snakefile",
        no_use_conda=no_use_conda,
        verbose=verbose,
        extra_args=snakemake_args,
        outdir=outdir,
    )


# create a do subcommand that passes most of its arguments
# on to snakemake (after setting Snakefile and config)
@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("sample")
@click.option("--no-use-conda", is_flag=True, default=False)
@click.option("--verbose", is_flag=True)
@click.option("--outdir", nargs=1)
@click.argument("snakemake_args", nargs=-1)
def process(sample, snakemake_args, no_use_conda, verbose, outdir):
    "execute genome-grist workflow (using snakemake underneath)"
    snakemake_args = list(snakemake_args)
    snakemake_args += ["--config", f"sample={sample}"]
    run_snakemake(
        None,
        snakefile_name="Snakefile",
        no_use_conda=no_use_conda,
        verbose=verbose,
        extra_args=snakemake_args,
        outdir=outdir,
    )


# 'check' command
@click.command()
@click.argument("configfile")
def check(configfile):
    "check configuration"
    run_snakemake(configfile, extra_args=["check"])


# 'showconf' command
@click.command()
@click.argument("configfile")
def showconf(configfile):
    "show full configuration"
    run_snakemake(configfile, extra_args=["showconf"])


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
cli.add_command(process)
cli.add_command(check)
cli.add_command(showconf)
cli.add_command(info)


def main():
    cli()


if __name__ == "__main__":
    main()
