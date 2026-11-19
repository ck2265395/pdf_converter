from collections.abc import Callable, Iterable
from pathlib import Path

from .models import ConversionResult
from .paths import reserve_pdf_path
from .text_pdf import convert_text
from .word_pdf import convert_word, find_word_backend

ProgressCallback = Callable[[int, int, ConversionResult], None]


def convert_files(
    sources: Iterable[Path],
    output_dir: Path | None = None,
    progress: ProgressCallback | None = None,
) -> list[ConversionResult]:
    files = [Path(item) for item in sources]
    results: list[ConversionResult] = []
    backend = None
    backend_checked = False
    for index, source in enumerate(files, start=1):
        destination: Path | None = None
        try:
            destination = reserve_pdf_path(source, output_dir)
            suffix = source.suffix.lower()
            if suffix == ".txt":
                convert_text(source, destination)
            elif suffix in {".doc", ".docx"}:
                if not backend_checked:
                    backend = find_word_backend()
                    backend_checked = True
                convert_word(source, destination, backend)
            else:
                raise ValueError(f"暂不支持 {source.suffix or '无扩展名'} 文件")
            result = ConversionResult(source, destination, True, "转换成功")
        except Exception as exc:
            if destination and destination.exists():
                destination.unlink(missing_ok=True)
            result = ConversionResult(source, None, False, str(exc))
        results.append(result)
        if progress:
            progress(index, len(files), result)
    return results

