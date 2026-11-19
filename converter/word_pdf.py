from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

WORD_SCRIPT = (
    "$ErrorActionPreference='Stop'; $word=$null; $doc=$null; "
    "try { $word=New-Object -ComObject Word.Application; $word.Visible=$false; "
    "$word.DisplayAlerts=0; $word.AutomationSecurity=3; "
    "$word.Options.UpdateLinksAtOpen=$false; "
    "$doc=$word.Documents.Open($env:LOCAL_PDF_SOURCE,$false,$true,$false); "
    "$doc.ExportAsFixedFormat($env:LOCAL_PDF_DESTINATION,17); "
    "} finally { if($doc){$doc.Close($false)}; if($word){$word.Quit()} }"
)


class WordBackendUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class WordBackend:
    kind: str
    executable: Path | None = None


def find_word_backend() -> WordBackend | None:
    command = shutil.which("soffice")
    candidates = [
        Path(command) if command else None,
        Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
        Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return WordBackend("libreoffice", candidate)
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"Word.Application\CLSID"):
            return WordBackend("word")
    except (ImportError, FileNotFoundError, OSError):
        return None


def _convert_with_libreoffice(source: Path, destination: Path, executable: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="local_pdf_") as temp_dir:
        profile = Path(temp_dir) / "profile"
        completed = subprocess.run(
            [str(executable), f"-env:UserInstallation={profile.as_uri()}", "--headless", "--convert-to", "pdf", "--outdir", temp_dir, str(source)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        generated = Path(temp_dir) / f"{source.stem}.pdf"
        if completed.returncode != 0 or not generated.exists():
            detail = (completed.stderr or completed.stdout).strip()
            raise RuntimeError(f"LibreOffice 转换失败：{detail or '未生成 PDF'}")
        shutil.move(str(generated), str(destination))


def word_environment(source: Path, destination: Path) -> dict[str, str]:
    environment = os.environ.copy()
    environment["LOCAL_PDF_SOURCE"] = str(source.resolve())
    environment["LOCAL_PDF_DESTINATION"] = str(destination.resolve())
    return environment


def _convert_with_word(source: Path, destination: Path) -> None:
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", WORD_SCRIPT],
        env=word_environment(source, destination),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if completed.returncode != 0 or not destination.exists():
        detail = (completed.stderr or completed.stdout).strip()
        raise WordBackendUnavailable(
            "无法转换 Word 文件。请安装免费的 LibreOffice，或确认 Microsoft Word 已正确安装。"
            + (f"\n详细信息：{detail}" if detail else "")
        )


def convert_word(source: Path, destination: Path, backend: WordBackend | None = None) -> None:
    if backend is None:
        raise WordBackendUnavailable("未找到转换组件，请安装免费的 LibreOffice 或 Microsoft Word。")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if backend.kind == "libreoffice" and backend.executable:
        _convert_with_libreoffice(source, destination, backend.executable)
    elif backend.kind == "word":
        _convert_with_word(source, destination)
    else:
        raise WordBackendUnavailable("未找到转换组件，请安装免费的 LibreOffice 或 Microsoft Word。")

