from pathlib import Path

from converter.paths import reserve_pdf_path, unique_pdf_path


def test_uses_source_directory_by_default(tmp_path: Path):
    source = tmp_path / "notes.txt"
    assert unique_pdf_path(source, None) == tmp_path / "notes.pdf"


def test_does_not_overwrite_existing_pdf(tmp_path: Path):
    source = tmp_path / "notes.txt"
    (tmp_path / "notes.pdf").write_bytes(b"old")
    assert unique_pdf_path(source, tmp_path) == tmp_path / "notes (1).pdf"


def test_reservation_prevents_second_instance_from_claiming_same_name(tmp_path: Path):
    source = tmp_path / "notes.txt"
    first = reserve_pdf_path(source, tmp_path)
    second = reserve_pdf_path(source, tmp_path)
    assert first.name == "notes.pdf"
    assert second.name == "notes (1).pdf"

