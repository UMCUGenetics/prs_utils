import pandas as pd

from prs_utils import merge_prs_mqc

HEADER = "Sample\tModel\tSCORE1_SUM\tSUM_Z\tQC status\tQC Comment\tModel Alpha\n"


def write_qc_tsv(tmp_path, name, rows):
    path = tmp_path / name
    path.write_text(HEADER + "".join(rows))
    return str(path)


def test_main_merges_sorts_and_writes_multiqc_table(tmp_path, monkeypatch):
    files = [
        write_qc_tsv(tmp_path, "b.tsv", ["sampleB\tmodel1\t1.0\t0.5\tPASS\tok\t1.0\n"]),
        write_qc_tsv(tmp_path, "a.tsv", ["sampleA\tmodel2\t2.0\t1.5\tFAIL\tbad\t0.5\n"]),
        write_qc_tsv(tmp_path, "c.tsv", ["sampleA\tmodel1\t3.0\t2.5\tPASS\tok\t0.1\n"]),
    ]
    monkeypatch.chdir(tmp_path)

    merge_prs_mqc.main(files)

    output = tmp_path / "prs_scores_mqc.tsv"
    text = output.read_text()

    # MultiQC configuration is emitted as a comment block ahead of the table.
    assert text.startswith("# id: 'prs-scores'\n")
    assert "#     Z-score:\n" in text
    assert "#             'sampleA__model1': '#e8f0fe'\n" in text
    assert "#             'sampleB': '#ffffff'\n" in text

    df = pd.read_csv(output, sep="\t", comment="#")
    assert list(df.columns) == [
        "Sample_Model",
        "Sample",
        "Model",
        "Z-score",
        "QC Status",
        "QC Comment",
        "Model Alpha",
    ]
    # Sorted by Sample then Model; SCORE1_SUM is dropped.
    assert list(df["Sample_Model"]) == ["sampleA__model1", "sampleA__model2", "sampleB__model1"]
    assert list(df["Z-score"]) == [2.5, 1.5, 0.5]


def test_main_assigns_a_distinct_colour_per_model(tmp_path, monkeypatch):
    files = [
        write_qc_tsv(
            tmp_path,
            "all.tsv",
            [
                "sampleA\tmodel1\t1.0\t0.5\tPASS\tok\t1.0\n",
                "sampleA\tmodel2\t1.0\t0.5\tPASS\tok\t1.0\n",
            ],
        )
    ]
    monkeypatch.chdir(tmp_path)

    merge_prs_mqc.main(files)

    text = (tmp_path / "prs_scores_mqc.tsv").read_text()
    assert "#             'model1': '#ffd9b3'\n" in text
    assert "#             'model2': '#b3d9f0'\n" in text
