# IMP-001: План Реализации DCL Agent

**Основание:** [TSD-001_DCL_Agent.md](file:///c:/git/dcl/.workspace/dcl_agent_implementation/TSD-001_DCL_Agent.md)

---

## 1. Стратегия Реализации

Разработка будет вестись итеративно, снизу-вверх (bottom-up), начиная с фундаментальных структур и заканчивая интеграцией.
Разбивка на этапы (Milestones) соответствует логическим слоям архитектуры.

---

## 2. Этапы и Задачи (Backlog)

### Milestone 1: Core Structures & Loader (Скелет)
*   **Цель:** Создать базовую структуру проекта, определить доменные объекты и реализовать загрузку артефактов.
*   **Задачи:**
    *   [ ] **Task 1.1: Project Scaffolding & Test Environment.**
        *   Создать директорию `src/dcl_agent` и `tests`.
        *   Создать `__init__.py` и основные суб-пакеты.
        *   Настроить `pytest.ini` и добавить зависимости для отчетов (`pytest-html` и т.д.).
    *   [ ] **Task 1.2: Domain Objects.**
        *   Реализовать `InvocationContext` (`ContextFrame`, `TextFrame`, `BlobFrame`) в `src/dcl_agent/model.py`.
    *   [ ] **Task 1.3: Loader Strategy & Registry.**
        *   Реализовать `PromptModuleRegistry`.
        *   Реализовать `Loader`, принимающий пути к артефактам через конфигурацию (не хардкод).
    *   [ ] **Task 1.4: Test: Implement & Run Unit Tests.**
        *   Сгенерировать тестовые данные (dummy modules).
        *   Написать и **успешно прогнать** тесты для Loader и Registry.

### Milestone 2: Parser Implementation (Lark)
*   **Цель:** Научить агента понимать синтаксис DCL команды.
*   **Задачи:**
    *   [ ] **Task 2.1: Grammar & Model.**
        *   Перенести грамматику v2.2 в `src/dcl_agent/dcl.lark`.
        *   Определить dataclass `Instruction`.
    *   [ ] **Task 2.2: DCLParser Implementation.**
        *   Реализовать парсинг текста в `Instruction`.
    *   [ ] **Task 2.3: Test: Implement & Run Unit Tests.**
        *   Сгенерировать валидные и невалидные DCL инструкции.
        *   Написать и **успешно прогнать** тесты парсера.

### Milestone 3: Context Assembly (Strategies)
*   **Цель:** Реализовать логику преобразования Инструкции и Реестра в Контекст.
*   **Задачи:**
    *   [ ] **Task 3.1: Strategies Implementation.**
        *   Реализовать `GeminiNativeStrategy` и `ConcatenationStrategy`.
    *   [ ] **Task 3.2: Test: Implement & Run Unit Tests.**
        *   Написать и **успешно прогнать** тесты проверки правильности сборки контекста для разных стратегий.

### Milestone 4: Agent Integration & LLM Adapter
*   **Цель:** Собрать всё воедино и обеспечить возможность оффлайн-запуска.
*   **Задачи:**
    *   [ ] **Task 4.1: LLM Adapters.**
        *   Реализовать `MockLLMAdapter` (заглушка для оффлайн-режима).
        *   Реализовать `GeminiAdapter` (реальный вызов).
    *   [ ] **Task 4.2: DCLAgent Implementation.**
        *   Реализовать класс `DCLAgent`.
    *   [ ] **Task 4.3: Test: Implement & Run Unit Tests.**
        *   Написать и **успешно прогнать** тесты для `DCLAgent` с использованием `MockLLMAdapter`.

### Milestone 5: Verification & Reporting
*   **Цель:** Демонстрация работоспособности и отчетность.
*   **Задачи:**
    *   [ ] **Task 5.1: Verification Script.**
        *   Скрипт `verify_agent.py` с использованием `MockLLMAdapter`.
    *   [ ] **Task 5.2: Reporting Automation.**
        *   Генерация отчета по тестам (pytest report).
        *   Создание `CHANGELOG.md` в корне проекта (по образцу `.antigravity/examples/CHANGELOG.md`).

---

## 3. Критерии Приемки (Definition of Done)
1.  **Code Quality:** Python 3.12+, типизация, отсутствие хардкода.
2.  **Testing:** 
    *   **Unit Tests Passed** для каждого Milestone.
    *   Успешный прогон `verify_agent.py` (offline).
    *   Отчет о тестах (`tests/report.xml` или `report.txt`).
3.  **Documentation:** 
    *   Актуальный `CHANGELOG.md`.
