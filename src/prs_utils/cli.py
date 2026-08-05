"""Single entry point bundling the PRS pipeline utility scripts as subcommands."""

from importlib.metadata import version as package_version
from typing import Annotated

import typer

from prs_utils import get_snp_list, merge_prs_mqc, normalise_counts, pgs_to_vcf, sample_qc

cli = typer.Typer(add_completion=False, help="Utilities for the PRS pipeline.")

# These subcommands own their own argument parsing (argparse / sys.argv), so Click must not
# touch anything after the subcommand name -- not even --help, which is forwarded verbatim.
_PASSTHROUGH = {
    "allow_extra_args": True,
    "ignore_unknown_options": True,
    "help_option_names": [],
}


def _version_callback(show_version: bool) -> None:
    # The Nextflow modules capture this output into their `versions` topic, so it must be the
    # bare version and nothing else.
    if show_version:
        typer.echo(package_version("prs-utils"))
        raise typer.Exit()


@cli.callback()
def _cli_options(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show the package version and exit.",
        ),
    ] = False,
) -> None:
    """Utilities for the PRS pipeline."""


@cli.command(
    "pgs-to-vcf",
    context_settings=_PASSTHROUGH,
    help="Convert a PGS Catalog scoring file to a VCF (REF=other_allele, ALT=effect_allele).",
)
def _pgs_to_vcf(ctx: typer.Context) -> None:
    pgs_to_vcf.main(ctx.args)


@cli.command(
    "merge-prs-mqc",
    context_settings=_PASSTHROUGH,
    help="Merge per-sample QC tables into a MultiQC table (writes prs_scores_mqc.tsv).",
)
def _merge_prs_mqc(ctx: typer.Context) -> None:
    merge_prs_mqc.main(ctx.args)


@cli.command(
    "normalise-counts",
    context_settings=_PASSTHROUGH,
    help="Add a SUM_Z Z-score column to a PRS score table.",
)
def _normalise_counts(ctx: typer.Context) -> None:
    normalise_counts.main(ctx.args)


@cli.command(
    "get-snp-list",
    context_settings=_PASSTHROUGH,
    help="Write a flanked region list from the positions in a scoring file.",
)
def _get_snp_list(ctx: typer.Context) -> None:
    get_snp_list.main(ctx.args)


# sample_qc is already a Typer command function -- reuse it as-is so its options are unchanged.
cli.command(
    "sample-qc",
    help="Flag samples based on PRS Z-score and ancestry thresholds.",
)(sample_qc.main)


if __name__ == "__main__":
    cli()
