"""Инструменты агентов: только локальное чтение уже извлечённого текста."""

from __future__ import annotations

from pathlib import Path

from crewai.tools import tool

from practice_crew.extract import extract_text


@tool("read_local_legal_file")
def read_local_legal_file(path: str) -> str:
    """Прочитать локальный txt/md/docx. Путь должен существовать на диске."""
    p = Path(path)
    if not p.is_file():
        return f"Файл не найден: {path}"
    try:
        text = extract_text(p)
    except ValueError as exc:
        return str(exc)
    if len(text) > 20_000:
        return text[:20_000] + "\n\n[обрезано до 20000 символов]"
    return text or "Файл пустой."
