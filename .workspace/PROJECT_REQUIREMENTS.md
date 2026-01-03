# Project Requirements Index

**Last Updated:** 2025-12-18

---

## Назначение

Этот документ служит **единым источником истины** для поиска актуальных версий всех артефактов требований (REQ) и технологического решения (TSD) по всем спринтам. Документ автоматически обновляется агентом после утверждения и публикации артефактов каждого спринта.

---

## Активные Требования

| ID | Тема | Затронутые компоненты | Текущая версия | Расположение | Последнее обновление |
|----|------|-----------------------|----------------|--------------|---------------------|
| REQ-001 | DCL Agent MVP | Parser, Loader, Registry, Strategies, Adapters | v1.0 | `.workspace/SP-001_dcl_agent_implementation/REQ-001_DCL Agent.md` | 2025-12-06 |
| REQ-002 | Aliases in DCL instructions | Registry, Loader | v1.0 | `.workspace/SP-002_Aliases_in_DCL_instructions/REQ-002_Aliases_in_DCL_instructions.md` | 2025-12-16 |
| REQ-003 | Resources Formatting | Base Strategy, Gemini Strategy, Concat Strategy | v1.0 | `.workspace/SP-003_invocation_context_strategies_refinement/REQ-003_Resources_Formatting.md` | 2025-12-19 |
| REQ-004 | Notebook Support | Packaging, Notebooks | v1.0 | `.workspace/SP-004_notebook_support/REQ-004_notebook_support.md` | 2025-12-26 |

**Примечания:**
- **ID**: Уникальный идентификатор темы требований (инкрементальный).
- **Тема**: Краткое название функциональности/возможности.
- **Затронутые компоненты**: Список компонентов/подсистем, на которые влияют требования (помогает выявлять конфликты при Impact Analysis).
- **Текущая версия**: Последняя утвержденная версия.
- **Расположение**: Путь к файлу в папке спринта.
- **Последнее обновление**: Дата последней модификации.

---

## Активные Технологические Решения

| ID | Тема | Затронутые компоненты | Текущая версия | Расположение | Последнее обновление |
|----|------|-----------------------|----------------|--------------|---------------------|
| TSD-001 | DCL Agent Architecture | Parser, Loader, Registry, Strategies, Adapters | v1.0 | `.workspace/SP-001_dcl_agent_implementation/TSD-001_DCL_Agent.md` | 2025-12-06 |
| TSD-002 | Alias Resolution Design | Registry, Loader | v1.0 | `.workspace/SP-002_Aliases_in_DCL_instructions/TSD-002_Aliases_in_DCL_instructions.md` | 2025-12-16 |
| TSD-003 | Resources Formatting | Base Strategy, Gemini Strategy, Concat Strategy | v1.0 | `.workspace/SP-003_invocation_context_strategies_refinement/TSD-003_Resources_Formatting.md` | 2025-12-19 |
| TSD-004 | Packaging and Notebook Support | Packaging, Notebooks | v1.0 | `.workspace/SP-004_notebook_support/TSD-004_packaging.md` | 2025-12-26 |

---

## История версий

[Журнал изменений индекса, документирующий, какие спринты добавили или обновили артефакты.]

- **2025-12-26 (SP-004):** Созданы REQ-004 v1.0, TSD-004 v1.0, IMP-004 v1.0 (Notebook Support)
- **2025-12-19 (SP-003):** Созданы REQ-003 v1.0, TSD-003 v1.0 (Resources Formatting)
- **2025-12-18 (Организационная задача):** Создан индекс требований на основе существующих артефактов SP-001 и SP-002
- **2025-12-16 (SP-002):** Созданы REQ-002 v1.0, TSD-002 v1.0
- **2025-12-06 (SP-001):** Созданы REQ-001 v1.0, TSD-001 v1.0

---

## Инструкции по использованию (для агента)

1. **В начале нового спринта (Impact Analysis):**
   - Прочитать этот индекс для определения текущих версий базовых артефактов.
   - Использовать колонку **Затронутые компоненты** для обнаружения потенциальных конфликтов с новой задачей.

2. **После утверждения и публикации артефактов:**
   - Обновить таблицу с новыми/измененными записями артефактов.
   - Добавить новую запись в секцию История версий.
   - Опубликовать обновленный `PROJECT_REQUIREMENTS.md` в `.workspace/` (корневой уровень).
