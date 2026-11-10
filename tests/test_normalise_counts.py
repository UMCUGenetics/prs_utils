import pandas as pd

from prs_utils import normalise_counts


def test_score_to_z_score():
    scores = pd.Series([1.0, 2.0, 3.0])

    z_scores = normalise_counts.score_to_z_score(scores, mu=2.0, sd=0.5)

    assert list(z_scores) == [-2.0, 0.0, 2.0]


def test_main_writes_sum_z_column(tmp_path):
    prs = tmp_path / "scores.tsv"
    prs.write_text("IID\tSCORE1_SUM\nsampleA\t1.0\nsampleB\t3.0\n")
    output = tmp_path / "normalised.tsv"

    normalise_counts.main(["--PRS", str(prs), "--mu", "2.0", "--SD", "0.5", "-o", str(output)])

    df = pd.read_csv(output, sep="\t")
    assert list(df.columns) == ["IID", "SCORE1_SUM", "SUM_Z"]
    assert list(df["SUM_Z"]) == [-2.0, 2.0]
