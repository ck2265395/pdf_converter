from pathlib import Path

from converter.text_pdf import convert_text, read_text


def test_reads_gbk_text(tmp_path: Path):
    source = tmp_path / "cn.txt"
    source.write_bytes("你好，世界".encode("gbk"))
    assert read_text(source) == "你好，世界"


def test_creates_valid_multipage_pdf_for_long_chinese_text(tmp_path: Path):
    source = tmp_path / "long.txt"
    destination = tmp_path / "long.pdf"
    source.write_text(("这是一段很长的中文内容。" * 20 + "\n") * 200, encoding="utf-8")
    convert_text(source, destination)
    data = destination.read_bytes()
    assert data.startswith(b"%PDF-")
    assert len(data) > 1000
    assert b"/FontFile2" in data

