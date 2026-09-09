"""Настройки пилота. Секреты только из окружения / .env."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

QWEN_API_KEY = (
    os.getenv("QWEN_API_KEY") or os.getenv("DOC_ANALYZER_QWEN_API_KEY") or ""
).strip()
QWEN_BASE_URL = (
    os.getenv("QWEN_BASE_URL")
    or os.getenv("DOC_ANALYZER_QWEN_BASE_URL")
    or "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
).strip()
QWEN_MODEL = (
    os.getenv("QWEN_MODEL") or os.getenv("DOC_ANALYZER_QWEN_MODEL") or "qwen-plus"
).strip()

LOG_DIR = PROJECT_ROOT / "logs"
OUTPUT_DIR = PROJECT_ROOT / "output"


def require_qwen_key() -> str:
    if not QWEN_API_KEY:
        raise RuntimeError(
            "Не задан QWEN_API_KEY (или DOC_ANALYZER_QWEN_API_KEY). "
            "Скопируйте .env.example в .env и вставьте ключ."
        )
    return QWEN_API_KEY
