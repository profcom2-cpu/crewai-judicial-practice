"""Локальное извлечение текста. Без OCR и без зависимостей JuristStudio."""

from __future__ import annotations

from pathlib import Path


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")
    if suffix == ".docx":
        from docx import Document

        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    raise ValueError(f"Пилот читает .txt/.md/.docx, получен: {path.suffix}")
