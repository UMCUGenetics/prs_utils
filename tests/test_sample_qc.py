import pandas as pd
import pytest

from prs_utils import sample_qc


def make_row(pred_group="EUR", knn_conf=0.9):
    return pd.Series({"pred_group": pred_group, "knn_conf": knn_conf})


def test_calc_model_matchrate_sums_only_matched_percentages():
    model_df = pd.DataFrame(
        {
            "match_status": ["matched", "matched", "unmatched"],
            "percent": [60.0, 20.0, 20.0],
        }
    )

    assert sample_qc.calc_model_matchrate(model_df) == pytest.approx(0.8)


def test_qc_check_passes_when_all_thresholds_are_met():
    row = sample_qc.QC_check(make_row(), ["EUR"], 0.6, 0.9, 0.75)

    assert row["QC status"] == "PASS"
    assert row["QC Comment"] == ""
    assert row["Model matchrate"] == 0.9


@pytest.mark.parametrize(
    ("row", "matchrate", "comment"),
    [
        (make_row(pred_group="AFR"), 0.9, "REFERENCE_PANEL_MISMATCH"),
        (make_row(knn_conf=0.1), 0.9, "LOW_REFERENCE_PANEL_CONFIDENCE"),
        (make_row(), 0.1, "INSUFFICIENT_VARIANT_COVERAGE"),
    ],
)
def test_qc_check_reports_each_failure_reason(row, matchrate, comment):
    result = sample_qc.QC_check(row, ["EUR"], 0.6, matchrate, 0.75)

    assert result["QC status"] == "FAIL"
    assert result["QC Comment"] == comment


def test_qc_check_joins_multiple_failure_reasons():
    row = sample_qc.QC_check(make_row(pred_group="AFR", knn_conf=0.1), ["EUR"], 0.6, 0.1, 0.75)

    assert row["QC Comment"] == ("REFERENCE_PANEL_MISMATCH;LOW_REFERENCE_PANEL_CONFIDENCE;INSUFFICIENT_VARIANT_COVERAGE")


def test_main_writes_qc_table(tmp_path):
    scores = tmp_path / "scores.tsv"
    scores.write_text("IID\tSCORE1_SUM\tSUM_Z\nsampleA\t1.5\t0.5\n")
    ancestry = tmp_path / "ancestry.tsv"
    ancestry.write_text("#IID\tpred_group\tknn_conf\nsampleA\tEUR\t0.9\n")
    model_summary = tmp_path / "summary.csv"
    model_summary.write_text("match_status,percent\nmatched,90.0\nunmatched,10.0\n")
    output = tmp_path / "qc.tsv"

    sample_qc.main(
        scores=scores,
        ancestry=ancestry,
        model_summary=model_summary,
        output=output,
        sample="sampleA",
        model="BCAC_313_PRS",
        alpha=1.0,
    )

    df = pd.read_csv(output, sep="\t")
    # "Model Matchrate" is intentionally absent: QC_check writes "Model matchrate" (lowercase m)
    # while the final filter asks for the capitalised name, so pandas drops it. Preserved as-is.
    assert list(df.columns) == [
        "Sample",
        "Model",
        "SCORE1_SUM",
        "SUM_Z",
        "QC status",
        "QC Comment",
        "Model Alpha",
    ]
    assert df.loc[0, "QC status"] == "PASS"
