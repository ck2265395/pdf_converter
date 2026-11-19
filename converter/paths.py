from pathlib import Path
import os


def unique_pdf_path(source: Path, output_dir: Path | None) -> Path:
    directory = output_dir or source.parent
    candidate = directory / f"{source.stem}.pdf"
    index = 1
    while candidate.exists():
        candidate = directory / f"{source.stem} ({index}).pdf"
        index += 1
    return candidate


def reserve_pdf_path(source: Path, output_dir: Path | None) -> Path:
    directory = output_dir or source.parent
    directory.mkdir(parents=True, exist_ok=True)
    index = 0
    while True:
        suffix = "" if index == 0 else f" ({index})"
        candidate = directory / f"{source.stem}{suffix}.pdf"
        try:
            descriptor = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(descriptor)
            return candidate
        except FileExistsError:
            index += 1

