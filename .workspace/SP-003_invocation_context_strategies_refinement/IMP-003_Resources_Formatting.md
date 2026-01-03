# Implementation Plan: Resources Formatting

**Version:** 1.0  
**Created:** 2025-12-19  
**Sprint:** SP-003  
**Base:** [TSD-003_Resources_Formatting.md](file:///c:/git/dcl/.workspace/SP-003_invocation_context_strategies_refinement/TSD-003_Resources_Formatting.md)

---

## 1. Implementation Strategy

Реализация строится на базе **Test-Driven Development (TDD)**. Для каждого компонента (утилита форматирования, конкретные стратегии) сначала пишутся тесты, проверяющие ожидаемое поведение, после чего вносится код. 
- **Milestone 1:** Атомарный уровень (Formatter Utils).
- **Milestone 2 & 3:** Уровень стратегий (GeminiNative, Concatenation). Проверка верной интеграции форматтера в процесс сборки контекста.
- **Milestone 4:** Финальная оффлайн-верификация на базе реальных бандлов (`dcl-core`, `dcl-god-mode`) без использования LLM.

---

## 2. Milestones and Tasks

### Milestone 1: Core Formatter Logic (TDD)

**Goal:** Реализовать статическую утилиту форматирования в базовом классе.

#### Task 1.1: Юнит-тесты для метода `_format_resource_as_markdown`

**Action:**
- Создать `tests/test_formatter_utils.py`.
- Реализовать тесты, проверяющие:
    - Модуль `type == 'RESOURCE'` оборачивается в ```[id]\n[content]\n```.
    - Другие типы (`OPERATOR`, `MODIFIER`) остаются в исходном виде.
    - Краевые кейсы: пустой контент, длинные ID.

**Files:**
- [NEW] `tests/test_formatter_utils.py`

**Verification:**
- Запустить `pytest tests/test_formatter_utils.py`. Ожидаемый результат: **FAIL** (метод еще не существует).

#### Task 1.2: Реализация метода в `IContextAssemblyStrategy`

**Action:**
- В `src/dcl_agent/strategies/base.py` добавить статический метод `_format_resource_as_markdown(module: PromptModule) -> str`.
- Добавить аннотации типов (Python 3.12+) и Docstring.

**Files:**
- [MODIFY] `src/dcl_agent/strategies/base.py`

**Verification:**
- Запустить `pytest tests/test_formatter_utils.py`. Ожидаемый результат: **SUCCESS**.

---

### Milestone 2: GeminiNativeStrategy Integration (TDD)

**Goal:** Обеспечить пофреймовое форматирование ресурсов в `GeminiNativeStrategy`.

#### Task 2.1: Юнит-тесты стратегии `GeminiNativeStrategy`

**Action:**
- Создать `tests/test_gemini_strategy_formatting.py`.
- Реализовать тест, который:
    1. Создает мок `PromptModuleRegistry` с одним ресурсом.
    2. Вызывает `assemble()`.
    3. Проверяет через `assert`, что в `InvocationContext.frames` фрейм, соответствующий ресурсу, содержит markdown-разметку с его ID.

**Files:**
- [NEW] `tests/test_gemini_strategy_formatting.py`

**Verification:**
- Запустить `pytest tests/test_gemini_strategy_formatting.py`. Ожидаемый результат: **FAIL** (ресурс еще не оборачивается).

#### Task 2.2: Модификация `GeminiNativeStrategy.assemble`

**Action:**
- Вызвать `self._format_resource_as_markdown(module)` при формировании фреймов для `modifiers`, `goals` и `sources`.

**Files:**
- [MODIFY] `src/dcl_agent/strategies/gemini.py`

**Verification:**
- Запустить `pytest tests/test_gemini_strategy_formatting.py`. Ожидаемый результат: **SUCCESS**.

---

### Milestone 3: ConcatenationStrategy Integration (TDD)

**Goal:** Обеспечить форматирование ресурсов в `ConcatenationStrategy`.

#### Task 3.1: Юнит-тесты стратегии `ConcatenationStrategy`

**Action:**
- Создать `tests/test_concat_strategy_formatting.py`.
- Проверить, что итоговый (единственный) `TextFrame` содержит контент ресурсов в markdown-блоках.

**Files:**
- [NEW] `tests/test_concat_strategy_formatting.py`

**Verification:**
- Запустить `pytest tests/test_concat_strategy_formatting.py`. Ожидаемый результат: **FAIL**.

#### Task 3.2: Модификация `ConcatenationStrategy._format_module`

**Action:**
- Внедрить вызов `self._format_resource_as_markdown(module)` в логику форматирования модуля.

**Files:**
- [MODIFY] `src/dcl_agent/strategies/concat.py`

**Verification:**
- Запустить `pytest tests/test_concat_strategy_formatting.py`. Ожидаемый результат: **SUCCESS**.

---

### Milestone 4: Offline Functional Verification

**Goal:** Финальная проверка на реальном DCL-кейсе без LLM.

#### Task 4.1: Реализация скрипта `verify_formatting.py`

**Action:**
- Создать скрипт на базе `verify_agent_real.py` (копирование логики загрузки бандлов `dcl-core` и `dcl-god-mode`).
- **Использовать точную команду:**
  ```
  WRITE PromptModule('dcl-god-mode/modifiers/poetry.yaml')
  USING knowledges/framework/dcl_god_mode/0.2, GRAMMAR, SCHEMA, dclc, ctx, 'dclgm'
  ```
- Скрипт должен загружать бандлы, парсить команду и выводить содержимое `InvocationContext` в консоль.

**Files:**
- [NEW] `verify_formatting.py`

**Verification:**
- Скрипт доступен для ручного запуска пользователем.

---

## 3. Regression Test Plan

### Existing Tests
- `pytest tests/test_strategies.py`: Проверка того, что изменения в `base.py` не сломали существующую логику сборки контекста (порядок фреймов, базовое содержимое).

### New Tests (Backlog)
- `tests/test_formatter_utils.py`
- `tests/test_gemini_strategy_formatting.py`
- `tests/test_concat_strategy_formatting.py`
- `verify_formatting.py`

---

## 4. Definition of Done

1. **Python Standards:**
   - Код написан на Python 3.12+ с использованием Type Hints.
   - Все функции и методы снабжены Docstrings (формат: описание параметров, возвращаемых значений и исключений).
2. **Testing Coverage:**
   - Юнит-тесты покрывают логику форматтера (100% покрытие веток).
   - Интеграция в обе стратегии проверена специализированными тестами.
3. **Verification:**
   - Скрипт `verify_formatting.py` проходит успешно на оригинальных бандлах проекта.
   - **Запрещено использование реальных вызовов LLM для верификации.**

---

## 5. Unchanged Components

- **Loader & Registry:** Логика поиска и загрузки модулей из бандлов.
- **DCL Parser:** Грамматика разбора DCL-инструкций.
- **LLM Adapters:** Код взаимодействия с внешними API.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-19 | Iteration 5: Absolute precision in DCL commands, explicit TDD sequence, fixed DoD. |
