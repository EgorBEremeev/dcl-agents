# IMP-002: Aliases in DCL instructions

**Основание:** [TSD-002_Aliases_in_DCL_instructions.md](file:///C:/git/dcl/.workspace/SP-002_Aliases_in_DCL_instructions/TSD-002_Aliases_in_DCL_instructions.md)

---

## 1. Стратегия Реализации

Разработка будет вестись итеративно, начиная с расширения модели исключений и заканчивая интеграцией новой логики загрузки. Все изменения покрываются модульными тестами.

---

## 2. Этапы и Задачи (Backlog)

### Milestone 1: Exceptions Architecture
*   **Цель:** Определить классы исключений для управления потоком конфигурации.
*   **Задачи:**
    *   [ ] **Task 1.1: Exception Classes.**
        *   Создать файл `src/dcl_agent/exceptions.py`.
        *   Реализовать `DCLConfigurationError`, `InvalidAliasError`.
        *   Реализовать `DCLConfigurationWarning`, `AliasAlreadyExistsWarning`, `DuplicateIdWarning`.

### Milestone 2: Registry Logic Update
*   **Цель:** Реализовать логику First-Wins и поддержку алиасов в реестре.
*   **Задачи:**
    *   [ ] **Task 2.1: Registry Storage.**
        *   Добавить support for `_aliases` dict.
    *   [ ] **Task 2.2: Registration Logic.**
        *   Реализовать метод `register_alias` с выбросом warning'а.
        *   Обновить метод `register` с выбросом warning'а для дубликатов.
    *   [ ] **Task 2.3: Validation Logic.**
        *   Реализовать метод `validate_aliases` (Integrity Check).
    *   [ ] **Task 2.4: Test: Registry Unit Tests.**
        *   Написать тесты на `duplicates` и `validation` в `tests/test_registry_aliases.py`.

### Milestone 3: Loader Orchestration
*   **Цель:** Научить Loader работать со списком бандлов и обрабатывать `index.yaml`.
*   **Задачи:**
    *   [ ] **Task 3.1: Index Parsing.**
        *   Реализовать чтение `index.yaml` и вызов `register_alias` с перехватом warning'а.
    *   [ ] **Task 3.2: Multi-Bundle Loop.**
        *   Обновить `load_bundles` для итерации по списку.
        *   Добавить вызов `validate_aliases()` в конце.
    *   [ ] **Task 3.3: Test: Loader Integration Tests.**
        *   Написать тесты с макетами файлов (mock fs) для проверки First-Wins стратегии между бандлами.
    *   [ ] **Task 3.4: Agent Facade Update.**
        *   Обновить `DCLAgent.__init__` для поддержки списка путей (`bundles`).
        *   Использовать `loader.load_bundles()` вместо `load_from_directory`.

### Milestone 4: Verification
*   **Цель:** Проверка на реальных данных.
*   **Задачи:**
    *   [ ] **Task 4.0: Loader Verification Script.**
        *   Создать `verify_aliases_loader.py` для изолированной проверки загрузчика.
        *   Запуск скрипта и проверка алиасов (`WRITE`, `GRAMMAR`).
    *   [ ] **Task 4.1: Agent Verification.**
        *   Обновить `verify_agent.py` для загрузки `dcl-core` и `dcl-god-mode`.
        *   Использовать алиас `WRITE` в проверочной команде.
        *   Запуск скрипта и проверка вывода.
    *   [ ] **Task 4.2: Reporting.**
        *   Генерация отчета `pytest`.

---

## 3. Критерии Приемки (Definition of Done)
1.  **Code Quality:** Python 3.12+, типизация.
2.  **Testing:**
    *   Pass `tests/test_registry_aliases.py`.
    *   Pass `tests/test_loader_aliases.py`.
    *   Нет фатальных ошибок при загрузке `dcl-god-mode`.
3.  **Documentation:**
    *   Обновленная документация API (если применимо).
