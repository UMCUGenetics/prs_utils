"""Merge polygenic risk score multiqc results."""

import sys

import pandas as pd
from pathlib import Path

sample_palette = ["#e8f0fe", "#ffffff"]  # blue / white — sample stripes

# Pastel palette — distinct color per model so the same model is recognisable
# across all samples. Wraps after 8 models (rare in practice).
model_palette = [
    "#ffd9b3",  # peach
    "#b3d9f0",  # sky blue
    "#fff2a8",  # pale yellow
    "#d4b8e8",  # lavender
    "#a8d8c8",  # mint teal
    "#f5b8c8",  # rose pink
    "#d9c4a3",  # warm sand
    "#e0e0e0",  # soft grey
]


def _emit_bgcols(out, column, mapping):
    """Write MultiQC background-color configuration for a column.

    Args:
        out: Output stream for the configuration text.
        column: MultiQC table column name.
        mapping: Mapping of column values to background colors.
    """
    out.write(f"#     {column}:\n")
    out.write("#         bgcols:\n")
    for key, color in mapping.items():
        out.write(f"#             '{key}': '{color}'\n")


def main(argv=None):
    """Combine PRS multiqc results and write a MultiQC report table.

    Args:
        argv: Optional input paths; defaults to process arguments.
    """
    files = list(sys.argv[1:]) if argv is None else list(argv)

    dfs = []
    for f in files:
        df = pd.read_csv(f, sep="\t")
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    combined = combined.rename(
        columns={
            "SUM_Z": "Z-score",
            "QC status": "QC Status",
        }
    )
    combined = combined[["Sample", "Model", "Z-score", "QC Status", "QC Comment", "Model Alpha"]]
    combined.insert(0, "Sample_Model", combined["Sample"] + "__" + combined["Model"])
    combined = combined.sort_values(["Sample", "Model"]).reset_index(drop=True)

    unique_samples = combined["Sample"].drop_duplicates().tolist()
    sample_bgcols = {s: sample_palette[i % len(sample_palette)] for i, s in enumerate(unique_samples)}

    # Sample_Model rows align 1:1 with Sample rows — reuse the sample palette,
    # keyed on the composite "${Sample}__${Model}" value.
    sample_model_bgcols = {sm: sample_bgcols[s] for sm, s in zip(combined["Sample_Model"], combined["Sample"])}

    unique_models = combined["Model"].drop_duplicates().tolist()
    model_bgcols = {m: model_palette[i % len(model_palette)] for i, m in enumerate(unique_models)}

    with Path("prs_scores_mqc.tsv").open("w") as out:
        out.write("# id: 'prs-scores'\n")
        out.write("# pconfig:\n")
        out.write("#     only_defined_headers: false\n")
        out.write("# headers:\n")
        _emit_bgcols(out, "Sample_Model", sample_model_bgcols)
        _emit_bgcols(out, "Sample", sample_bgcols)
        _emit_bgcols(out, "Model", model_bgcols)
        out.write("#     Z-score:\n")
        out.write("#          title: 'Z-score'\n")
        out.write("#          format: '{:,.3f}'\n")
        out.write("#     Model Alpha:\n")
        out.write("#          title: 'Model Alpha'\n")
        out.write("#          format: '{:,.3f}'\n")
        combined.to_csv(out, sep="\t", index=False)


if __name__ == "__main__":
    main()
