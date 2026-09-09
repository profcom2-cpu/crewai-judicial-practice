# CrewAI — поиск судебной практики (пилот)

Отдельный учебный контур **вне JuristStudio**. Задача: по теме или по тексту оппонента собрать практику «за» и «против», сверить цитаты, отсечь выдумки и записать карточки в дневник.

Не собирает судебные DOCX, не индексирует диск и не читает почту.

## Агенты

| Агент | Задача |
|---|---|
| Извлекатель | Тема, тезисы и цитаты из файла или промпта |
| Искатель практики | Акты в поддержку тезисов |
| Оппонент | Противоположная практика |
| Верификатор цитат | Реквизиты и смысл цитаты |
| Антигаллюцинатор | Удаляет всё без источника |
| Систематизатор | Карточки: норма + цитата + позиция + применение |

## Десктоп-приложение

Ярлык на рабочем столе: **CrewAI Practice**.  
Создать / обновить ярлык:

```powershell
powershell -File D:\projects\crewai-judicial-practice\scripts\create_desktop_shortcut.ps1
```

Или без ярлыка:

```powershell
D:\projects\crewai-judicial-practice\scripts\launch_desktop.bat
```

Откроется отдельное окно (Edge/Chrome в режиме приложения). Тема или файл → «Запустить экипаж».

## Запуск из консоли

```powershell
cd D:\projects\crewai-judicial-practice
.\.venv\Scripts\Activate.ps1
copy .env.example .env
# вписать QWEN_API_KEY
python -m practice_crew --file samples\opponent_excerpt.txt
python -m practice_crew --web
```

По теме без файла:

```powershell
python -m practice_crew --topic "недействительность сделки при банкротстве, ст. 61.2 127-ФЗ"
```

Результат: `output/diary_YYYYMMDD_HHMMSS.md` и JSON рядом. Лог: `logs/practice_crew.log`.

## Окружение

Виртуальное окружение лежит **в этом проекте** (`.venv` на диске D:), не в JuristStudio.

Python для venv: **3.12** (`D:\projects\python312`). CrewAI не ставится на 3.14.
