"""LLM для CrewAI: облачный Qwen или локальный Ollama."""

from __future__ import annotations

from crewai import LLM

from practice_crew.config import LLM_MODE_OLLAMA, llm_connection


def build_llm(mode: str | None = None) -> LLM:
    resolved, key, base_url, model = llm_connection(mode)
    if resolved == LLM_MODE_OLLAMA:
        return LLM(
            model=f"ollama/{model}",
            api_key=key,
            base_url=base_url,
            temperature=0.2,
        )
    return LLM(
        model=f"openai/{model}",
        api_key=key,
        base_url=base_url,
        temperature=0.2,
    )


def build_qwen_llm() -> LLM:
    return build_llm(mode="cloud")


def build_ollama_llm() -> LLM:
    return build_llm(mode="ollama")
