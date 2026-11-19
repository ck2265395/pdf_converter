from pathlib import Path

from converter.service import convert_files


def test_continues_after_unsupported_file(tmp_path: Path):
    bad = tmp_path / "bad.xyz"
    good = tmp_path / "good.txt"
    bad.write_text("x", encoding="utf-8")
    good.write_text("hello", encoding="utf-8")
    results = convert_files([bad, good], tmp_path)
    assert [result.success for result in results] == [False, True]
    assert results[1].destination.exists()

