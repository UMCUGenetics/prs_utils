"""Create SNP TSV from a scoring file."""

from argparse import ArgumentParser

import pandas as pd
from pathlib import Path


def positions_to_tsv(scoring_file, chr_colname, pos_colname, prefix, flank=100):
    """Write genomic positions to a TSV file.

    Args:
        scoring_file: Tab-delimited scoring file path.
        chr_colname: Column containing chromosome values.
        pos_colname: Column containing position values.
        prefix: Prefix for the output filename.
        flank: Number of bases to include on either side of each position.
    """
    df = pd.read_csv(scoring_file, sep="\t", comment="#")

    with Path(f"{prefix}_snplist.list").open("w") as outfile:
        for index, row in df.iterrows():
            chrom = row[chr_colname]
            pos = int(row[pos_colname])

            start = pos - flank
            end = pos + flank

            # Skip rows with missing chromosome or position
            if not chrom or not pos:
                continue

            # Ensure chromosome has 'chr' prefix
            chr_prefix = "chr"
            if "chr" in str(chrom):
                chr_prefix = ""

            tsv_line = f"{chr_prefix}{chrom}:{start}-{end}\n"

            outfile.write(tsv_line)


def get_opts(argv=None):
    """Define and parse command-line options.

    Args:
        argv: Optional command-line arguments.

    Returns:
        Parsed command-line options.
    """
    p = ArgumentParser()
    p.add_argument("--scoring_file", help="Custom scoring file, alternative for PGSID", required=True)
    p.add_argument("--flank", help="Flanking region for each position to call variants in.", default=100, type=int)
    p.add_argument("--prefix", help="Prefix for output files", required=True)

    return p.parse_args(argv)


def main(argv=None):
    """Convert genomic positions from list to tsv file.

    Args:
        argv: Optional command-line arguments.
    """
    args = get_opts(argv)

    chr_colname = "hm_chr"
    pos_colname = "hm_pos"

    positions_to_tsv(args.scoring_file, chr_colname, pos_colname, args.prefix, int(args.flank))


if __name__ == "__main__":
    main()
