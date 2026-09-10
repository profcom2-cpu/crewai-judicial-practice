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

LLM_MODE_CLOUD = "cloud"
LLM_MODE_OLLAMA = "ollama"
VALID_LLM_MODES = (LLM_MODE_CLOUD, LLM_MODE_OLLAMA)
_LLM_MODE_ALIASES = {
    "dashscope": LLM_MODE_CLOUD,
    "qwen": LLM_MODE_CLOUD,
    "local": LLM_MODE_OLLAMA,
    "ollama-qwen": LLM_MODE_OLLAMA,
    "allama": LLM_MODE_OLLAMA,
    "аллама": LLM_MODE_OLLAMA,
    "аалама": LLM_MODE_OLLAMA,
}

OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").strip()
OLLAMA_MODEL = (os.getenv("OLLAMA_MODEL") or "qwen2.5:1.5b").strip()
OLLAMA_API_KEY = (os.getenv("OLLAMA_API_KEY") or "ollama").strip()
OLLAMA_EXE = Path(os.getenv("OLLAMA_EXE") or r"D:\Ollama\ollama.exe")

LOG_DIR = PROJECT_ROOT / "logs"
OUTPUT_DIR = PROJECT_ROOT / "output"


def normalize_llm_mode(raw: str | None = None) -> str:
    val = (raw if raw is not None else os.getenv("LLM_MODE") or LLM_MODE_CLOUD).strip().lower()
    val = _LLM_MODE_ALIASES.get(val, val)
    if val not in VALID_LLM_MODES:
        raise ValueError(
            f"Неизвестный LLM_MODE={val!r}. Ожидается cloud или ollama."
        )
    return val


def ollama_native_base_url(url: str | None = None) -> str:
    raw = (url or OLLAMA_BASE_URL).strip().rstrip("/")
    if raw.endswith("/v1"):
        raw = raw[:-3].rstrip("/")
    return raw or "http://127.0.0.1:11434"


def probe_ollama(timeout: float = 3.0) -> tuple[bool, str]:
    import json
    import urllib.error
    import urllib.request

    base = ollama_native_base_url()
    try:
        with urllib.request.urlopen(f"{base}/api/tags", timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        hint = f" Запустите: {OLLAMA_EXE} serve" if OLLAMA_EXE.is_file() else ""
        return False, f"Ollama не отвечает на {base}: {exc}.{hint}"
    names = [str(item.get("name") or item.get("model") or "") for item in data.get("models") or []]
    wanted = OLLAMA_MODEL
    if wanted and not any(name == wanted or name.startswith(f"{wanted}:") for name in names):
        have = ", ".join(names) if names else "пусто"
        return False, f"В Ollama нет модели {wanted}. Есть: {have}."
    return True, "ok"


def require_ollama() -> str:
    ok, msg = probe_ollama()
    if not ok:
        raise RuntimeError(msg)
    return OLLAMA_MODEL


def llm_connection(mode: str | None = None) -> tuple[str, str, str, str]:
    """mode, api_key, base_url, model."""
    resolved = normalize_llm_mode(mode)
    if resolved == LLM_MODE_OLLAMA:
        require_ollama()
        return resolved, OLLAMA_API_KEY or "ollama", ollama_native_base_url(), OLLAMA_MODEL
    return resolved, require_qwen_key(), QWEN_BASE_URL, QWEN_MODEL


def require_qwen_key() -> str:
    if not QWEN_API_KEY:
        raise RuntimeError(
            "Не задан QWEN_API_KEY (или DOC_ANALYZER_QWEN_API_KEY). "
            "Скопируйте .env.example в .env и вставьте ключ."
        )
    return QWEN_API_KEY
