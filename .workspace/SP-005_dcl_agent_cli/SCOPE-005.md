# SCOPE-005: DCL Agent CLI

## Тип задачи
Enhancement (Инфраструктура проекта)

## Базовые артефакты
- REQ-004 (Notebook Support / Packaging) — базовая структура `pyproject.toml`
- SP-004: `src/dcl_agent/pyproject.toml`
- SP-003: `GeminiNativeStrategy` (`src/dcl_agent/strategies/gemini.py`, реализует `IContextAssemblyStrategy`) — стратегия компиляции DCL-инструкции в InvocationContext; используется CLI без изменений

## Контекст

До SP-005 dcl-agent существовал исключительно как Python-библиотека.
Единственным способом скомпилировать InvocationContext для конкретной
DCL-инструкции была запуск Python-ноутбука с `MockLLMAdapter`.

Это создавало практический разрыв: **authored compiled specs** в
`service-views/<service>/specs/*.yaml` содержали `system_instruction`,
написанный вручную — с неизбежными расхождениями с актуальным состоянием
prompt-модулей и без возможности воспроизводимой перекомпиляции.

## Цель спринта

1. Добавить точку входа `dcl-agent` CLI в пакет.
2. Обеспечить установку пакета как глобального `uv tool` в editable-режиме
   (автоматическое обновление из исходников без переустановки).
3. Дать возможность компилировать `system_instruction` для compiled spec
   через команду `dcl-agent compile`, воспроизводя логику notebook-симуляции.
   **Стратегия компиляции:** `GeminiNativeStrategy`
   (`dcl_agent.strategies.gemini.GeminiNativeStrategy`) — стратегия по умолчанию
   у `DCLAgent`; CLI не выбирает и не переопределяет стратегию.

## Затронутые компоненты

- `src/dcl_agent/pyproject.toml` — добавление `[project.scripts]`
- `src/dcl_agent/cli.py` — новый модуль (CLI точка входа)
- Документация: `README.md`, `PROJECT_ARCHITECTURE.md`, `PROJECT_REQUIREMENTS.md`

## Выходные артефакты

- `src/dcl_agent/cli.py` — CLI-модуль
- Обновленный `src/dcl_agent/pyproject.toml`
- Скомпилированная `service-views/inventory-srv/specs/extract_item_data.yaml` (внешний проект)
- SCOPE-005, REQ-005, TSD-005

## Риски регрессии

- Минимальны: добавляется новый модуль `cli.py` и точка входа, существующий
  публичный API `DCLAgent` не изменяется.
- `pyproject.toml` получает новую секцию `[project.scripts]` — не влияет
  на поведение библиотеки.

## Открытые вопросы

- Нет.
