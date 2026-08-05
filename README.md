# prs_utils

![test](https://github.com/UMCUGenetics/prs_utils/actions/workflows/test.yml/badge.svg)
![lint](https://github.com/UMCUGenetics/prs_utils/actions/workflows/lint.yml/badge.svg)

Utility commands for the PRS pipeline, bundled as a single installable package.

These utilities previously lived as standalone [PEP 723](https://peps.python.org/pep-0723/)
scripts inside the `prsutils` Nextflow modules
(`NF-Modules/modules/UMCUGenetics/prsutils/*/resources/usr/bin/`), each with its own
`uv run --script` header and lock file. They are now one package with shared dependency
resolution, linting and tests. The behaviour of every command is unchanged.

## Commands

Everything is reachable through the `prs-utils` entry point:

| Subcommand | Original script | NF module |
| --- | --- | --- |
| `prs-utils pgs-to-vcf` | `pgs_to_vcf.py` | `prsutils/getvcf` |
| `prs-utils merge-prs-mqc` | `merge_prs_mqc.py` | `prsutils/mergeprsmqc` |
| `prs-utils normalise-counts` | `normalise_counts.py` | `prsutils/norm` |
| `prs-utils sample-qc` | `sample_qc.py` | `prsutils/sampleqc` |
| `prs-utils get-snp-list` | `get_snp_list.py` | `prsutils/snplist` |

Each subcommand keeps the argument parser it was written with, so the flags are identical to
the standalone scripts. Use `prs-utils <subcommand> --help` for the per-command options.

```sh
uv run prs-utils --help
uv run prs-utils normalise-counts --PRS scores.tsv --mu 0.5 --SD 0.1 -o normalised.tsv
uv run prs-utils get-snp-list --scoring_file PGS000004.txt --prefix PGS000004 --flank 100
```

Note that `merge-prs-mqc` takes its inputs as bare positional paths and always writes
`prs_scores_mqc.tsv` in the working directory.

## Container image

Each release publishes a multi-arch image to
`ghcr.io/umcugenetics/prs-utils:<version>`, built from `uv.lock` so the dependency set is exactly
the one the tests ran against. This is what the `prsutils` Nextflow modules pin their `container`
directive to.

```sh
docker run --rm -v "$PWD:/data" -w /data ghcr.io/umcugenetics/prs-utils:1.0.0 \
    prs-utils normalise-counts --PRS scores.tsv --mu 0.5 --SD 0.1 -o normalised.tsv
```

Singularity pulls the same image directly:

```sh
singularity exec docker://ghcr.io/umcugenetics/prs-utils:1.0.0 prs-utils --version
```

Build it locally without publishing:

```sh
docker build -t prs-utils:dev .
```

## Releasing

`prs-utils --version` prints the bare version from `pyproject.toml`, and the Nextflow modules
capture that output into their `versions` topic and snapshot it. Keep the two repositories in step:

1. Bump `version` in `pyproject.toml`.
2. Run `uv lock` and commit the updated `uv.lock`.
3. Tag and publish a GitHub release. The `publish.yml` workflow builds and pushes the image, then
   fails the release if the image does not report the tagged version.
4. Confirm the new tag appears under the repository's Packages.
5. Bump the `container` tag in the five `prsutils` modules in
   [UMCUGenetics/NF-Modules](https://github.com/UMCUGenetics/NF-Modules) and re-run their nf-tests.

The first published version needs one manual step: set the GHCR package visibility to **public**
(Package settings → Change visibility). Otherwise every `singularity pull` in CI and on the HPC
needs registry credentials.

## Development

Setup and run the test suite:

```sh
uv sync
uv run pytest tests
```

Linting and formatting use [Ruff](https://docs.astral.sh/ruff/):

```sh
uv run ruff check src tests
uv run ruff format src tests
```

## GitHub Actions

This repository contains two GitHub actions workflows (`.github/workflows/`): `lint.yml` and
`test.yml`. The lint workflow uses the [ruff-action](https://github.com/astral-sh/ruff-action)
action to run ruff. The test workflow uses the
[setup-uv action](https://github.com/astral-sh/setup-uv) to setup uv, install dependencies and
run tests. Both actions are configured to run on each pull request and push to main and develop.

## pre-commit

Git pre-commit hooks enable you to run certain commands before each commit and can be used to
check code style before committing. The file `.pre-commit-config.yaml` contains the
[Ruff](https://docs.astral.sh/ruff/) [pre-commit](https://pre-commit.com) hook, which will
automatically run Ruff before each commit. Run the following command to install the git commit
hook: `uvx pre-commit install`.
