"""Экипаж: практика по делу."""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task

from practice_crew.llm import build_llm
from practice_crew.tools import read_local_legal_file


def build_crew(*, source_note: str, llm_mode: str | None = None) -> Crew:
    llm = build_llm(llm_mode)

    extractor = Agent(
        role="Извлекатель тезисов и цитат",
        goal="Достать из входа тему, тезисы оппонента и каждую цитату с тем, что указано как источник.",
        backstory=(
            "Процессуалист-делопроизводитель. Не оцениваешь право. "
            "Не выдумываешь номера дел и даты, если их нет во входе."
        ),
        llm=llm,
        tools=[read_local_legal_file],
        verbose=True,
    )
    researcher = Agent(
        role="Искатель судебной практики «за»",
        goal="Подобрать практику, которая может поддержать тезисы оппонента, только с реквизитами.",
        backstory=(
            "Исследователь практики ВС РФ и арбитражных округов. "
            "Если точного акта не помнишь — пишешь UNVERIFIED, не придумываешь номер дела."
        ),
        llm=llm,
        verbose=True,
    )
    adversary = Agent(
        role="Искатель противоположной практики",
        goal="Найти практику и нормы, которые опровергают тезисы оппонента.",
        backstory=(
            "Адвокат другой стороны. Ищешь пределы обычной хозяйственной деятельности, "
            "презумпции вреда, границы кассации по АПК. Без выдуманных реквизитов."
        ),
        llm=llm,
        verbose=True,
    )
    verifier = Agent(
        role="Верификатор цитат",
        goal="Сверить каждую цитату: суд, дата, номер дела, совпадает ли смысл.",
        backstory=(
            "Ревизор цитирования. Если нет номера/даты — статус NO_SOURCE. "
            "Не подтверждай цитату «по памяти» без оговорки."
        ),
        llm=llm,
        verbose=True,
    )
    auditor = Agent(
        role="Антигаллюцинатор",
        goal="Вычеркнуть акты, нормы и цитаты без источника или с конфликтом реквизитов.",
        backstory=(
            "Последний фильтр. Лучше короткий достоверный список, чем длинный красивый. "
            "Помечай DROP у каждой выдумки."
        ),
        llm=llm,
        verbose=True,
    )
    clerk = Agent(
        role="Систематизатор дневника",
        goal="Собрать только прошедшие фильтр карточки дневника.",
        backstory="Ведёшь дневник практики: норма, цитата, позиция, применение к тезису.",
        llm=llm,
        verbose=True,
    )

    t_extract = Task(
        description=(
            "Вход для этого прогона:\n{source_note}\n\n"
            "Если во входе есть путь к файлу — прочитай его инструментом. "
            "Верни структурированный список: тема; тезисы; цитаты "
            "(текст цитаты / что указано как источник / чего не хватает)."
        ),
        expected_output="Маркированный список тезисов и цитат без правовой оценки.",
        agent=extractor,
    )
    t_for = Task(
        description=(
            "По извлечённым тезисам подбери практику «за» позицию оппонента. "
            "Каждый пункт: норма или акт, реквизиты (если знаешь точно), "
            "иначе UNVERIFIED. Не выдумывай номера дел."
        ),
        expected_output="Список практики «за» с пометками UNVERIFIED где нет реквизитов.",
        agent=researcher,
        context=[t_extract],
    )
    t_against = Task(
        description=(
            "По тем же тезисам подбери противоположную практику и нормы "
            "(127-ФЗ, АПК РФ, разъяснения ВС). Реквизиты или UNVERIFIED."
        ),
        expected_output="Список практики «против» с реквизитами или UNVERIFIED.",
        agent=adversary,
        context=[t_extract],
    )
    t_verify = Task(
        description=(
            "Сверь цитаты оппонента и акты из двух списков практики. "
            "Для каждой: OK / NO_SOURCE / MISMATCH. Кратко почему."
        ),
        expected_output="Таблица сверки цитат и актов.",
        agent=verifier,
        context=[t_extract, t_for, t_against],
    )
    t_audit = Task(
        description=(
            "Удали или пометь DROP всё, что NO_SOURCE, MISMATCH или UNVERIFIED "
            "без честного указания пробела. Не добавляй новых актов."
        ),
        expected_output="Очищенный перечень допустимых тезисов и оговорок.",
        agent=auditor,
        context=[t_verify, t_for, t_against],
    )
    t_diary = Task(
        description=(
            "Собери дневник только из очищенного перечня. "
            "Каждая карточка строго в формате:\n"
            "### Карточка N\n"
            "- Норма:\n"
            "- Цитата (если есть, иначе «нет прямой цитаты»):\n"
            "- Позиция (за/против тезиса):\n"
            "- Применение к тезису:\n"
            "- Реквизиты / статус проверки:\n"
            "В конце блок «Отбраковано» со списком DROP."
        ),
        expected_output="Markdown дневника с карточками и блоком отбраковки.",
        agent=clerk,
        context=[t_audit, t_extract],
    )

    return Crew(
        agents=[extractor, researcher, adversary, verifier, auditor, clerk],
        tasks=[t_extract, t_for, t_against, t_verify, t_audit, t_diary],
        process=Process.sequential,
        verbose=True,
    )
