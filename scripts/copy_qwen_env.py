"""Скопировать ключ Qwen из .env JuristStudio в локальный .env. Не печатает секрет."""

from __future__ import annotations

from pathlib import Path

JS_ENV = Path(
    r"C:\Users\profc\Desktop\Курс нейросети для юристов (материалы)\создание бота-ИИ ассистента\.env"
)
DST = Path(__file__).resolve().parents[1] / ".env"
KEYS = {
    "QWEN_API_KEY",
    "DOC_ANALYZER_QWEN_API_KEY",
    "DOC_ANALYZER_QWEN_BASE_URL",
    "DOC_ANALYZER_QWEN_MODEL",
    "QWEN_BASE_URL",
    "QWEN_MODEL",
}


def main() -> int:
    if not JS_ENV.is_file():
        print("JuristStudio .env не найден")
        return 1
    vals: dict[str, str] = {}
    for line in JS_ENV.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        key, value = s.split("=", 1)
        key = key.strip()
        if key in KEYS and value.strip():
            vals[key] = value.strip().strip('"').strip("'")
    qwen = vals.get("QWEN_API_KEY") or vals.get("DOC_ANALYZER_QWEN_API_KEY") or ""
    base = (
        vals.get("QWEN_BASE_URL")
        or vals.get("DOC_ANALYZER_QWEN_BASE_URL")
        or "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    )
    model = vals.get("QWEN_MODEL") or vals.get("DOC_ANALYZER_QWEN_MODEL") or "qwen-plus"
    DST.write_text(
        f"QWEN_API_KEY={qwen}\nQWEN_BASE_URL={base}\nQWEN_MODEL={model}\n",
        encoding="utf-8",
    )
    print(f"wrote {DST} key={'yes' if bool(qwen) else 'no'} model={model}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
