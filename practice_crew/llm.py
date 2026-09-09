"""Qwen как LLM для CrewAI (OpenAI-совместимый endpoint)."""

from __future__ import annotations

from crewai import LLM

from practice_crew.config import QWEN_BASE_URL, QWEN_MODEL, require_qwen_key


def build_qwen_llm() -> LLM:
    key = require_qwen_key()
    # LiteLLM: префикс openai/ для произвольного OpenAI-compatible URL.
    return LLM(
        model=f"openai/{QWEN_MODEL}",
        api_key=key,
        base_url=QWEN_BASE_URL,
        temperature=0.2,
    )
