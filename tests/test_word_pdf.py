from pathlib import Path

import pytest

from converter.word_pdf import WORD_SCRIPT, WordBackendUnavailable, convert_word, word_environment


def test_reports_clear_error_when_no_backend(tmp_path: Path):
    source = tmp_path / "a.docx"
    with pytest.raises(WordBackendUnavailable, match="LibreOffice|Microsoft Word"):
        convert_word(source, tmp_path / "a.pdf", backend=None)


def test_word_paths_are_passed_as_data_not_powershell_source(tmp_path: Path):
    source = tmp_path / "报告‘特殊’.doc"
    destination = tmp_path / "报告‘特殊’.pdf"
    environment = word_environment(source, destination)
    assert str(source.resolve()) == environment["LOCAL_PDF_SOURCE"]
    assert str(destination.resolve()) == environment["LOCAL_PDF_DESTINATION"]
    assert "报告" not in WORD_SCRIPT
    assert "AutomationSecurity=3" in WORD_SCRIPT
    assert "UpdateLinksAtOpen=$false" in WORD_SCRIPT

