from importlib.metadata import version as package_version

from typer.testing import CliRunner

from prs_utils.cli import cli

runner = CliRunner()


def test_version_prints_the_bare_version_string():
    """The Nextflow modules snapshot this output, so it must be the version and nothing else."""
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert result.output == f"{package_version('prs-utils')}\n"


def test_all_subcommands_are_registered():
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    for subcommand in ("pgs-to-vcf", "merge-prs-mqc", "normalise-counts", "sample-qc", "get-snp-list"):
        assert subcommand in result.output


def test_passthrough_forwards_help_to_the_original_parser():
    """--help after a passthrough subcommand must reach argparse, not Click."""
    result = runner.invoke(cli, ["normalise-counts", "--help"])

    assert result.exit_code == 0
    # argparse spells these exactly as the standalone script did.
    assert "--PRS" in result.output
    assert "--SD" in result.output


def test_passthrough_forwards_arguments(tmp_path):
    scores = tmp_path / "scores.tsv"
    scores.write_text("IID\tSCORE1_SUM\nsampleA\t1.5\n")
    output = tmp_path / "out.tsv"

    result = runner.invoke(
        cli,
        ["normalise-counts", "--PRS", str(scores), "--mu", "0.5", "--SD", "0.5", "-o", str(output)],
    )

    assert result.exit_code == 0
    assert output.read_text().splitlines()[1].endswith("2.0")
