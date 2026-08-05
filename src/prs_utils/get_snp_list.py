from argparse import ArgumentParser

import pandas as pd


def positions_to_tsv(scoring_file, chr_colname, pos_colname, prefix, flank=100):
    df = pd.read_csv(scoring_file, sep="\t", comment="#")

    with open(f"{prefix}_snplist.list", "w") as outfile:
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

            tsv_line = f"{chr_prefix}{chrom}:{str(start)}-{str(end)}\n"

            outfile.write(tsv_line)


def get_opts(argv=None):
    p = ArgumentParser()
    p.add_argument("--scoring_file", help="Custom scoring file, alternative for PGSID", required=True)
    p.add_argument("--flank", help="Flanking region for each position to call variants in.", default=100, type=int)
    p.add_argument("--prefix", help="Prefix for output files", required=True)

    return p.parse_args(argv)


def main(argv=None):
    args = get_opts(argv)

    chr_colname = "hm_chr"
    pos_colname = "hm_pos"

    positions_to_tsv(args.scoring_file, chr_colname, pos_colname, args.prefix, int(args.flank))


if __name__ == "__main__":
    main()
