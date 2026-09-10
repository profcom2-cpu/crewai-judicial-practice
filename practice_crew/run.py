"""Общий запуск экипажа для CLI и десктоп-приложения."""

from __future__ import annotations

import logging
from pathlib import Path

from practice_crew.crew import build_crew
from practice_crew.diary import save_diary
from practice_crew.extract import extract_text

log = logging.getLogger("practice_crew")


def build_source_note(file_path: Path | None, topic: str) -> str:
    parts: list[str] = []
    if topic.strip():
        parts.append(f"Тема пользователя: {topic.strip()}")
    if file_path:
        resolved = file_path.resolve()
        log.info("Читаю файл: %s", resolved)
        preview = extract_text(resolved)
        parts.append(f"Путь к файлу: {resolved}")
        parts.append("Текст файла:\n" + preview)
    return "\n\n".join(parts)


def run_practice_job(
    *,
    topic: str = "",
    file_path: Path | None = None,
    llm_mode: str | None = None,
) -> dict[str, str]:
    if file_path is None and not topic.strip():
        raise ValueError("Нужны тема или файл оппонента")
    source_note = build_source_note(file_path, topic)
    label = topic.strip() or (file_path.name if file_path else "без темы")
    log.info("Старт экипажа. Тема: %s режим=%s", label, llm_mode or "env")
    crew = build_crew(source_note=source_note, llm_mode=llm_mode)
    result = crew.kickoff(inputs={"source_note": source_note})
    text = str(result)
    md_path, json_path = save_diary(text, topic=label)
    log.info("Дневник: %s", md_path)
    log.info("JSON: %s", json_path)
    return {
        "topic": label,
        "diary_md": text,
        "md_path": str(md_path),
        "json_path": str(json_path),
    }
