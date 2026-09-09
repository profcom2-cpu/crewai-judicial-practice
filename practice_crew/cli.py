"""CLI пилота: python -m practice_crew --file ... | --topic ..."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from practice_crew.logging_setup import setup_logging
from practice_crew.run import run_practice_job


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CrewAI-пилот: судебная практика")
    parser.add_argument("--file", type=Path, help="Локальный txt/md/docx оппонента")
    parser.add_argument("--topic", type=str, default="", help="Тема, если файла нет")
    parser.add_argument("--web", action="store_true", help="Открыть десктоп-приложение")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    if args.web:
        from practice_crew.webapp import main as web_main

        return web_main()

    log = setup_logging()
    if not args.file and not args.topic.strip():
        log.error("Нужен --file или --topic (или --web)")
        return 2
    try:
        out = run_practice_job(topic=args.topic, file_path=args.file)
    except Exception:
        log.exception("Прогон экипажа не удался")
        return 1
    print(out["md_path"])
    return 0
