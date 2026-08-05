from prs_utils import get_snp_list

SCORING_FILE = """\
#pgs_id=PGS000001
hm_chr\thm_pos
1\t1000
chr2\t2000
"""


def write_scoring_file(tmp_path):
    scoring_file = tmp_path / "scoring.txt"
    scoring_file.write_text(SCORING_FILE)
    return scoring_file


def test_positions_to_tsv_applies_flank_and_chr_prefix(tmp_path):
    scoring_file = write_scoring_file(tmp_path)
    prefix = tmp_path / "PGS000001"

    get_snp_list.positions_to_tsv(scoring_file, "hm_chr", "hm_pos", str(prefix), flank=100)

    lines = (tmp_path / "PGS000001_snplist.list").read_text().splitlines()
    # Row 1 gains a "chr" prefix, row 2 already has one and is left alone.
    assert lines == ["chr1:900-1100", "chr2:1900-2100"]


def test_positions_to_tsv_default_flank_is_100(tmp_path):
    scoring_file = write_scoring_file(tmp_path)
    prefix = tmp_path / "default"

    get_snp_list.positions_to_tsv(scoring_file, "hm_chr", "hm_pos", str(prefix))

    assert (tmp_path / "default_snplist.list").read_text().splitlines()[0] == "chr1:900-1100"


def test_main_uses_the_harmonised_columns(tmp_path):
    scoring_file = write_scoring_file(tmp_path)
    prefix = tmp_path / "PGS000001"

    get_snp_list.main(["--scoring_file", str(scoring_file), "--prefix", str(prefix), "--flank", "10"])

    lines = (tmp_path / "PGS000001_snplist.list").read_text().splitlines()
    assert lines == ["chr1:990-1010", "chr2:1990-2010"]
