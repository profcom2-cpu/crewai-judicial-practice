"""Переключить LLM: cloud (DashScope Qwen) или ollama (локальный qwen2.5:1.5b)."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"

DEFAULTS = {
    "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
    "OLLAMA_MODEL": "qwen2.5:1.5b",
    "OLLAMA_API_KEY": "ollama",
}
_MODE_ALIASES = {"allama": "ollama", "аллама": "ollama", "аалама": "ollama", "qwen": "cloud"}


def _upsert(text: str, key: str, value: str) -> str:
    lines = text.splitlines()
    prefix = key + "="
    found = False
    out: list[str] = []
    for line in lines:
        if line.startswith(prefix) or line.startswith("# " + prefix):
            if not found:
                out.append(f"{key}={value}")
                found = True
            continue
        out.append(line)
    if not found:
        if out and out[-1].strip():
            out.append("")
        out.append(f"{key}={value}")
    return "\n".join(out) + ("\n" if text.endswith("\n") or not text else "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Переключить LLM для practice_crew")
    parser.add_argument("mode", choices=("cloud", "ollama", "allama", "qwen"))
    args = parser.parse_args()
    mode = _MODE_ALIASES.get(args.mode, args.mode)
    raw = ENV_PATH.read_text(encoding="utf-8") if ENV_PATH.is_file() else ""
    raw = _upsert(raw, "LLM_MODE", mode)
    for key, value in DEFAULTS.items():
        if f"{key}=" not in raw:
            raw = _upsert(raw, key, value)
    ENV_PATH.write_text(raw, encoding="utf-8")
    print(f"{ENV_PATH}: LLM_MODE={mode}")
    if mode == "ollama":
        print("Нужен запущенный Ollama: D:\\Ollama\\ollama.exe serve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
