"""CLI пилота: python -m practice_crew --file ... | --topic ..."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from practice_crew.crew import build_crew
from practice_crew.diary import save_diary
from practice_crew.extract import extract_text
from practice_crew.logging_setup import setup_logging


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CrewAI-пилот: судебная практика")
    parser.add_argument("--file", type=Path, help="Локальный txt/md/docx оппонента")
    parser.add_argument("--topic", type=str, default="", help="Тема, если файла нет")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    log = setup_logging()
    if not args.file and not args.topic.strip():
        log.error("Нужен --file или --topic")
        return 2

    source_note = _build_source_note(args.file, args.topic, log)
    topic = (args.topic or "").strip() or (args.file.name if args.file else "без темы")
    log.info("Старт экипажа. Тема: %s", topic)

    crew = build_crew(source_note=source_note)
    result = crew.kickoff(inputs={"source_note": source_note})
    text = str(result)
    md_path, json_path = save_diary(text, topic=topic)
    log.info("Дневник: %s", md_path)
    log.info("JSON: %s", json_path)
    print(md_path)
    return 0


def _build_source_note(file_path: Path | None, topic: str, log: logging.Logger) -> str:
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
