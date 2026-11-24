# TSD-005: DCL Agent CLI

**Версия:** 1.0
**Спринт:** SP-005
**Дата:** 2026-11-24

---

## 1. Контекст и область действия

Описывает техническую реализацию CLI-инструмента `dcl-agent`, добавляемого
к существующему Python-пакету `src/dcl_agent`.

**Задача:** обеспечить воспроизводимую компиляцию `system_instruction` для
authored compiled specs (формат `llm-invocation-spec.v1`) без запуска
Jupyter-ноутбука.

---

## 2. Архитектурные решения

### 2.1 Точка входа — `cli.py`

Новый модуль `src/dcl_agent/cli.py` реализует две подкоманды через `argparse`
с `add_subparsers`. Регистрируется как console script в `pyproject.toml`:

```toml
[project.scripts]
dcl-agent = "dcl_agent.cli:main"
```

Решение добавить именно console script (а не запуск через `python -m`):
- Соответствует стандарту `uv tool`, который требует наличия `[project.scripts]`.
- Создаёт нативный исполняемый файл (`dcl-agent.exe` / `dcl-agent`),
  не зависящий от активного окружения venv.

### 2.2 Установка через `uv tool --editable`

Выбранный механизм установки: `uv tool install --editable <path>`.

**Почему editable, а не обычная установка:**
- Исходники `src/dcl_agent/` активно дорабатываются (prompt-модули, стратегии).
- Editable-режим: `uv` создаёт `.pth`-файл, указывающий на исходную директорию.
  Любые изменения в `*.py` применяются немедленно без переустановки.
- В отличие от `pip install -e` в venv — `uv tool` устанавливает в
  изолированное окружение, но оставляет исполняемый файл глобально доступным.

### 2.3 Стратегия компиляции: `GeminiNativeStrategy` + `MockLLMAdapter`

**Стратегия компиляции:** `dcl_agent.strategies.gemini.GeminiNativeStrategy`
(`src/dcl_agent/strategies/gemini.py`), реализация `IContextAssemblyStrategy`
из `strategies/base.py`. Метод `assemble(instruction, registry)` формирует
Frame-ы в порядке: raw DCL-инструкция → `zero_context_frame` → оператор →
операнд → modifiers → goals → sources.

CLI не реализует собственную стратегию и не имеет флага её выбора:
он использует `agent.strategy`, т.е. значение по умолчанию `DCLAgent`
(`GeminiNativeStrategy()`). Смена стратегии — только через конструктор
`DCLAgent(strategy=...)` в коде (вне scope SP-005).

CLI инстанциирует `DCLAgent` с `MockLLMAdapter()` (вызов LLM не выполняется;
адаптер нужен лишь для конструктора). Это гарантирует:
- Идентичность результата CLI и notebook-симуляции.
- Автоматическое наследование изменений стратегии из `strategies/gemini.py`.

```python
def _build_agent(bundles_arg: str):
    from dcl_agent.agent import DCLAgent
    from dcl_agent.adapter.mock import MockLLMAdapter
    bundle_paths = [p.strip() for p in bundles_arg.split(",") if p.strip()]
    return DCLAgent(bundles=bundle_paths, adapter=MockLLMAdapter())
```

### 2.4 Поведение `--output concat` и authored compiled spec

Режим `concat` конкатенирует содержимое всех `TextFrame`-ов через `\n\n`.
Результат предназначен для прямой вставки в `system_instruction` compiled spec.

**Исключения из конкатенации:** Frame-ы без атрибута `content` (например,
`BlobFrame`) пропускаются молча — CLI ориентирован на текстовые бандлы.

---

## 3. Детализация компонентов

### 3.1 `src/dcl_agent/cli.py`

**Структура:**

```
cli.py
├── _build_agent(bundles_arg: str) -> DCLAgent
├── cmd_compile(args: Namespace) -> None
├── cmd_registry(args: Namespace) -> None
└── main() -> None          # точка входа console script
```

**`cmd_compile` — алгоритм:**

1. Создать `DCLAgent` с `MockLLMAdapter` и указанными бандлами.
2. Получить текст инструкции из `--instruction` или `--instruction-file`.
3. `instruction = agent.parser.parse(instruction_text)`
4. `context = agent.strategy.assemble(instruction, agent.registry)`
5. Итерация по `context.frames`:
   - `frames` mode: вывод заголовка + `frame.content`.
   - `concat` mode: сбор в список, итоговый `"\n\n".join(...)`.

**`cmd_registry` — алгоритм:**

1. Создать `DCLAgent`.
2. `registry = agent.get_registry()`
3. Вывести `json.dumps(registry._aliases, indent=2, ensure_ascii=False)`.
4. Вывести `module.id` для каждого модуля из `registry.list_modules()`.

### 3.2 Обновление `pyproject.toml`

Добавлена секция `[project.scripts]`:

```toml
[project.scripts]
dcl-agent = "dcl_agent.cli:main"
```

Версия пакета остаётся `0.1.0` — изменение аддитивное, совместимое.

---

## 4. Сценарий использования: компиляция `system_instruction`

Задача: скомпилировать `system_instruction` для операции `extract_item_data`
в `service-views/inventory-srv/specs/extract_item_data.yaml`.

**DCL-инструкция для операции:**

```
EXTRACT Entity('Attribute_Data')
FROM Entity('Raw_Description')
```

**Команда:**

```powershell
$bundles = "C:\git\dcl-agents\dcl-core,C:\git\dcl-adpilot\adpilot-core"
dcl-agent compile `
  --bundles $bundles `
  --instruction "EXTRACT Entity('Attribute_Data') FROM Entity('Raw_Description')" `
  --output concat
```

**Структура получаемого InvocationContext (Frames):**

| Frame | Содержание | Источник |
|---|---|---|
| 0 | Raw DCL-инструкция | `instruction.original_dcl_instruction` (`GeminiNativeStrategy.assemble`) |
| 1 | `zero_context_frame` (пример формата ответа) | `strategies/base.py` |
| 2 | OPERATOR prompt-module `extract_v1.3` целиком (YAML) | Registry → `ad-pilot/operations/extract/1.3` |
| 3 | Operand: `Entity('Attribute_Data')` | `instruction.operand` |

Порядок и состав Frame-ов задаёт `GeminiNativeStrategy.assemble`. В
`system_instruction` compiled spec `extract_item_data.yaml` включены raw DCL-инструкция,
модуль оператора и операнд (fenced-блоки по образцу `reconstruct_market_fingerprint.yaml`);
`zero_context_frame` и дамп `index.yaml` (симуляция AI Studio) опущены как избыточные.

---

## 5. API-контракты

Публичный API `DCLAgent` (`execute`, `get_registry`) не изменяется.
`cli.py` использует только публичные методы агента.

---

## 6. Верификация

| Проверка | Команда |
|---|---|
| CLI доступен | `dcl-agent --help` |
| Реестр корректен | `dcl-agent registry --bundles <bundles>` — алиас `EXTRACT` → `1.3` |
| Компиляция идентична ноутбуку | Сравнить output `--output frames` с notebook cell [21] |
| Editable update | Изменить `cli.py`, вызвать `dcl-agent` — изменение отразится без переустановки |

---

## 7. Открытые вопросы

Нет.
