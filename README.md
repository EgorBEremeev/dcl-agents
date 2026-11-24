# DCL Agents Framework

**DCL Agents Framework** — методология и инструменты для конструирования контекста LLM-вызова в заданной предметной области.

## Модель контекста

Фреймворк оперирует двумя ключевыми понятиями:

- **Context Frame** — семантически завершённый, переиспользуемый элемент инструкции или данных.
- **Invocation Context** — полная совокупность данных для одного вызова LLM API. Формируется динамически из Context Frames.

## Domain Context Language (DCL)

Предметная область и когнитивные способности конкретного DCL-агента определяются и описываются на языке **Domain Context Language (DCL)**. DCL — это саморасширяемое семейство языков, артефакты которого (грамматика, сущности, операции) служат инструментами для спецификации и сборки контекста.

Единицей языка DCL является **Промпт-модуль** (`dclgm:PromptModule`) — дизайн-тайм артефакт, инкапсулирующий определения:
- какие **операции** агент умеет выполнять (глаголы: WRITE, ANALYZE, TRANSLATE...)
- над какими **сущностями предметной области** он работает (существительные: PromptModule, Schema...)
- какие **модификаторы** влияют на его поведение (линзы, ограничения, стили)
- какие **знания** агент использует (онтологии, примеры, справочники)

Промпт-модуль (YAML-файл) имеет структуру, определяемую [схемой](dcl-core/modifiers/dcl_specification_v2.yaml), которая обеспечивает предсказуемую трансляцию в **Context Frame** во время исполнения.

Спецификация DCL включает [грамматику](dcl-core/knowledges/framework/dcl_grammar.yaml) для написания инструкций, определяющих логику сборки Invocation Context в ран-тайме.

Общая структура инструкции:
```
OPERATION [OPERAND] FROM [SOURCE] USING [METHOD/LENS] OPTIMIZING_FOR [GOAL]
```

## DCL-агент

DCL-агент транслирует инструкции на языке DCL в **Invocation Context**. DCL-инструкция **компилируется** в Invocation Context: агент разбирает команду, загружает нужные промпт-модули и собирает их в единый контекст для отправки в LLM.

DCL Agent является **stateless** компонентом — он не хранит состояние сессии (историю диалога, переменные среды). Управление сессионным контекстом находится **за пределами его ответственности** и реализуется внешним **Agentic Runtime** (например, Session Manager или Conversation Controller).

**Основная ценность:** декларативное управление контекстом LLM — вы описываете *намерение* на DCL, а агент сам собирает нужный промпт из библиотеки модулей, отделяя бизнес-логику («что делать») от технической реализации («как собирать промпты и вызывать API»).

📖 **Подробное объяснение концепций:**
- [Концепция проекта](.workspace/PROJECT_CONCEPT.md) — принципы, ключевые решения, бизнес-ценность
- [Архитектура](.workspace/PROJECT_ARCHITECTURE.md) — компоненты, паттерны, технологический стек
- [Текущее состояние проекта](.workspace/PROJECT_REQUIREMENTS.md) — реестр всех REQ/TSD по спринтам
- [Онтология DCL Core](dcl-core/knowledges/ontology/dcl-core.ttl) — формализация концепции DCL (OWL)
- [Онтология DCL God Mode](dcl-god-mode/knowledges/ontology/dcl-god-mode.ttl) — определения мета-агента (OWL)

---

# Как это работает

DCL Agents Framework включает три составляющие:

1. **Формализацию концепции DCL** в форме [OWL-онтологии](dcl-core/knowledges/ontology/dcl-core.ttl), определяющей базовые понятия: Language Entity (операнд), Language Operation (глагол), Language Modifier (линза/ограничение), Instruction (команда).

2. **Конкретную реализацию DCL для задач Context Engineering** — язык, в котором единственной сущностью является Prompt Module — минимальная единица контекста. Это тьюринг-полная система, где Контекст — центральная сущность домена.

3. **Python-библиотеку «оркестратор»** (`src/dcl_agent`) для исполнения DCL-инструкций.

Поскольку DCL Agent Framework является **self-hosting системой**, компоненты 1 и 2 сами организованы в наборы артефактов (бандлы), которые обрабатываются оркестратором:

*   **`dcl-core`** — базовый бандл: формальная грамматика DCL, спецификация структуры модулей, OWL-онтологии контекста.

*   **`dcl-god-mode`** — бандл с языком для Context Engineering, включающий операции мета-программирования: WRITE, REFINE, DECOMPOSE.

**Комбинация `dcl-core` + `dcl-god-mode` определяет мета-агента** — агента, который умеет писать промпт-модули для любых других DCL-агентов, включая самого себя.

## Операции мета-агента

| Операция | Что делает |
|----------|------------|
| **WRITE** | Создаёт новый промпт-модуль по заданной интенции |
| **REFINE** | Улучшает существующий модуль на основе обратной связи |
| **DECOMPOSE** | Разделяет сложный модуль на ортогональные компоненты |

**Пример:** создание нового оператора для аналитического агента:
```
WRITE PromptModule('analytics-bundle/operations/summarize.yaml') USING GRAMMAR, SCHEMA
```

## Создание агентов

Оркестратор позволяет создавать разных агентов путём загрузки разных наборов **бандлов** — папок с промпт-модулями:

```python
# Один и тот же код — разные агенты
agent_writer = DCLAgent(bundles=["./dcl-core", "./dcl-god-mode"], adapter=adapter)
agent_analyst = DCLAgent(bundles=["./dcl-core", "./analytics-bundle"], adapter=adapter)
```

---

## Структура репозитория

| Папка | Назначение |
|-------|------------|
| `src/dcl_agent` | Ядро фреймворка: парсер, загрузчик бандлов, стратегии сборки контекста, адаптеры LLM |
| `dcl-core` | Базовый бандл: грамматика, спецификация модулей, онтологии |
| `dcl-god-mode` | Мета-агент: операции WRITE, REFINE, DECOMPOSE |
| `notebooks` | Jupyter-ноутбук с примерами использования |
| `tests` | Тесты |
| `.workspace` | Проектная документация |

---

# Установка

## Глобальный CLI (рекомендуется для разработки)

Установить `dcl-agent` как глобальный uv tool в editable-режиме:

```bash
uv tool install --editable ./src/dcl_agent
```

После установки `dcl-agent` доступен глобально. В editable-режиме изменения
в `src/dcl_agent/` применяются без переустановки.

## Локальная разработка (библиотека в venv)

```bash
pip install -e ./src/dcl_agent
```

## Google Colab / Jupyter

```python
!git clone https://github.com/EgorBEremeev/dcl-agents.git
!pip install -e dcl/src/dcl_agent
```

---

# CLI: компиляция DCL-инструкций

После установки через `uv tool` доступна команда `dcl-agent`:

```bash
# Состояние реестра: алиасы и загруженные модули
dcl-agent registry --bundles ./dcl-core,../dcl-adpilot/adpilot-core

# Компиляция инструкции в InvocationContext (frames | concat)
dcl-agent compile --bundles ./dcl-core,../dcl-adpilot/adpilot-core \
  --instruction "EXTRACT Entity('Attribute_Data') FROM Entity('Raw_Description')" \
  --output concat
```

Компиляция выполняется стратегией `GeminiNativeStrategy` ([src/dcl_agent/strategies/gemini.py](src/dcl_agent/strategies/gemini.py)) — стратегией `DCLAgent` по умолчанию; выбора другой стратегии в CLI нет. Режим `concat` выдаёт готовый текст для `system_instruction` в compiled spec. Подробнее: [REQ-005](.workspace/SP-005_dcl_agent_cli/REQ-005_dcl_agent_cli.md), [TSD-005](.workspace/SP-005_dcl_agent_cli/TSD-005_dcl_agent_cli.md).

---
# Быстрый старт: мета-агент

```python
from dcl_agent.agent import DCLAgent
from dcl_agent.adapter.gemini import GeminiAdapter

adapter = GeminiAdapter(
    api_key="YOUR_API_KEY",
    model_name="models/gemini-2.0-flash-exp"
)

# Мета-агент: пишет промпт-модули
agent = DCLAgent(
    bundles=["./dcl-core", "./dcl-god-mode"],
    adapter=adapter
)

# Создать новый модификатор
response = agent.execute("""
    WRITE PromptModule('my-bundle/modifiers/formal_style.yaml')
    USING GRAMMAR, SCHEMA
""")
print(response)
```

---

# Создание своего агента

1. Создайте папку-бандл с нужными промпт-модулями (или сгенерируйте их мета-агентом)
2. Загрузите бандл вместе с `dcl-core`
3. Вызывайте операции, определённые в вашем бандле

```python
from dcl_agent.agent import DCLAgent
from dcl_agent.adapter.gemini import GeminiAdapter

adapter = GeminiAdapter(api_key="YOUR_KEY", model_name="models/gemini-2.0-flash-exp")

# Ваш специализированный агент
agent = DCLAgent(
    bundles=["./dcl-core", "./my-domain-bundle"],
    adapter=adapter
)

response = agent.execute("ANALYZE Document('report.pdf') USING BusinessLens")
```
