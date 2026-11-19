from pathlib import Path

from app import filter_supported_files, format_result_line
from converter.models import ConversionResult


def test_filters_files_case_insensitively_and_removes_duplicates():
    files = [Path("A.TXT"), Path("book.docx"), Path("skip.png"), Path("A.TXT")]
    assert filter_supported_files(files) == [Path("A.TXT"), Path("book.docx")]


def test_result_line_shows_actual_renamed_destination():
    result = ConversionResult(Path("notes.txt"), Path("notes (1).pdf"), True, "转换成功")
    assert format_result_line(result) == "✓ notes.txt  →  notes (1).pdf"

