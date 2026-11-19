from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConversionResult:
    source: Path
    destination: Path | None
    success: bool
    message: str

