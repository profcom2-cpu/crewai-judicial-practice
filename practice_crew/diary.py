"""Сохранение карточек дневника (markdown + json)."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from practice_crew.config import OUTPUT_DIR


def save_diary(raw: str, *, topic: str) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = OUTPUT_DIR / f"diary_{stamp}.md"
    json_path = OUTPUT_DIR / f"diary_{stamp}.json"

    header = (
        f"# Дневник судебной практики\n\n"
        f"- Тема: {topic}\n"
        f"- Дата прогона: {datetime.now().isoformat(timespec='seconds')}\n"
        f"- Контур: CrewAI-пилот (не JuristStudio)\n\n"
        "---\n\n"
    )
    md_path.write_text(header + (raw or "").strip() + "\n", encoding="utf-8")

    payload = {
        "topic": topic,
        "created": datetime.now().isoformat(timespec="seconds"),
        "body": raw,
        "cards_guess": _guess_card_count(raw),
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return md_path, json_path


def _guess_card_count(raw: str) -> int:
    return len(re.findall(r"(?im)^(?:карточка|##\s*карточка|\d+\.\s)", raw or ""))
