"""Tools for normalising polygenic risk scores."""

import argparse

import pandas as pd


def get_args(argv=None):
    """Define and parse command-line options.

    Args:
        argv: Optional command-line arguments.

    Returns:
        Parsed command-line options.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--PRS", help="Table with PRS scores")
    parser.add_argument("--mu", help="Population average for calculating Z-scores", required=True, type=float)
    parser.add_argument("--SD", help="Population standard deviation for calculating Z-scores", required=True, type=float)
    parser.add_argument("-o", "--output", help="Output file", required=True)

    return parser.parse_args(argv)


def score_to_z_score(scores, mu, sd):
    """Convert scores to population z-scores.

    Args:
        scores: Score values to normalise.
        mu: Population mean.
        sd: Population standard deviation.

    Returns:
        Z-scores corresponding to the input values.
    """
    z_scores = (scores - mu) / sd

    return z_scores


def main(argv=None):
    """Normalise scores from an input table and write the result.

    Args:
        argv: Optional command-line arguments.
    """
    args = get_args(argv)

    df = pd.read_csv(args.PRS, sep="\t")

    df["SUM_Z"] = score_to_z_score(df["SCORE1_SUM"], mu=args.mu, sd=args.SD)

    df.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
