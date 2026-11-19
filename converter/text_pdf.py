from html import escape
from pathlib import Path
import os

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

FONT_NAME = "LocalChineseFont"


def _register_font() -> str:
    fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    for filename in ("msyh.ttc", "msyh.ttf", "simsun.ttc", "simhei.ttf", "Deng.ttf"):
        candidate = fonts / filename
        if candidate.exists():
            pdfmetrics.registerFont(TTFont(FONT_NAME, str(candidate)))
            return FONT_NAME
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    return "STSong-Light"


def read_text(source: Path) -> str:
    data = source.read_bytes()
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def convert_text(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    font_name = _register_font()
    style = ParagraphStyle(
        "TextFile",
        fontName=font_name,
        fontSize=12,
        leading=18,
        alignment=TA_LEFT,
        wordWrap="CJK",
        spaceAfter=0,
    )
    document = SimpleDocTemplate(
        str(destination),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=source.name,
    )
    story = []
    for line in read_text(source).splitlines():
        if line.strip() == "\f":
            story.append(PageBreak())
        elif line:
            story.append(Paragraph(escape(line).replace("\t", "　　"), style))
        else:
            story.append(Spacer(1, style.leading))
    if not story:
        story.append(Paragraph(" ", style))
    document.build(story)

