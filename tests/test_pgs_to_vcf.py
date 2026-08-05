import io

from prs_utils import pgs_to_vcf

SCORING_FILE = """\
### PGS CATALOG SCORING FILE
#pgs_id=PGS000001
#genome_build=GRCh38
rsID\teffect_allele\tother_allele\teffect_weight\thm_chr\thm_pos\thm_rsID
rs1\tA\tG\t0.1\t1\t1000\trs1
rs2\tT\tC\t0.2\t2\t2000\trs2
"""


def test_read_meta_splits_metadata_header_and_body():
    meta, header, body = pgs_to_vcf.read_meta(io.StringIO(SCORING_FILE))

    assert meta == {"pgs_id": "PGS000001", "genome_build": "GRCh38"}
    assert header.startswith("rsID\teffect_allele")
    assert len(body) == 2


def test_build_info_fields_includes_numeric_values():
    row = {
        "effect_weight": "0.1",
        "allelefrequency_effect": "0.25",
        "hm_source": "ENSEMBL Variation",
        "hm_match_chr": "True",
        "hm_match_pos": "True",
    }

    info = pgs_to_vcf.build_info_fields(row, "PGS000001")

    assert info == ("PGSID=PGS000001;EFFECT_WEIGHT=0.1;EAF=0.25;HM_SOURCE=ENSEMBL_Variation;HM_MATCH=chr:True|pos:True")


def test_build_info_fields_skips_non_numeric_and_missing_values():
    row = {"effect_weight": "NA", "allelefrequency_effect": "", "hm_source": ""}

    assert pgs_to_vcf.build_info_fields(row, "PGS000001") == "PGSID=PGS000001"


def test_main_writes_vcf_with_chr_prefixed_contigs(tmp_path):
    scoring_file = tmp_path / "scoring.txt"
    scoring_file.write_text(SCORING_FILE)
    output = tmp_path / "out.vcf"

    pgs_to_vcf.main([str(scoring_file), str(output)])

    lines = output.read_text().splitlines()
    assert lines[0] == "##fileformat=VCFv4.2"
    assert "##pgs_id=PGS000001" in lines
    # genome_build GRCh38 comes from the metadata, so contigs gain a chr prefix.
    assert "##contig=<ID=chr1>" in lines
    assert lines[-2] == "chr1\t1000\trs1\tG\tA\t.\tPASS\tPGSID=PGS000001;EFFECT_WEIGHT=0.1"
    assert lines[-1] == "chr2\t2000\trs2\tC\tT\t.\tPASS\tPGSID=PGS000001;EFFECT_WEIGHT=0.2"


def test_main_skips_rows_with_equal_or_missing_alleles(tmp_path):
    scoring_file = tmp_path / "scoring.txt"
    scoring_file.write_text(
        "#pgs_id=PGS000002\n"
        "rsID\teffect_allele\tother_allele\thm_chr\thm_pos\n"
        "rs1\tA\tA\t1\t1000\n"  # REF == ALT
        "rs2\tA\t\t1\t2000\n"  # missing other_allele
        "rs3\tA\tG\t1\t\n"  # missing position
        "rs4\tA\tG\t1\t4000\n"
    )
    output = tmp_path / "out.vcf"

    pgs_to_vcf.main([str(scoring_file), str(output)])

    records = [line for line in output.read_text().splitlines() if not line.startswith("#")]
    assert len(records) == 1
    assert records[0].startswith("1\t4000\trs4\tG\tA")
