---
description: SPI-003
---

# SCOPE-003: Доработка стратегий сборки Invocation Context

**Sprint:** SP-003  
**Created:** 2025-12-18  
**Status:** Draft

---

## Task Description

Доработать стратегии сборки контекста (`GeminiNativeStrategy`, `ConcatenationStrategy`) для автоматического оборачивания содержимого фреймов типа `RESOURCE` в markdown-блоки кода. Цель — улучшить визуальную сепарацию ресурсов в контексте LLM.

---

## Task Type

- [ ] **New Development**
- [x] **Enhancement**

---

## Base Artifacts

| Artifact | ID | Version | Location |
|----------|------|---------|----------|
| Requirements | REQ-001 | v1.0 | `.workspace/SP-001_dcl_agent_implementation/REQ-001_DCL Agent.md` |
| Technical Design | TSD-001 | v1.0 | `.workspace/SP-001_dcl_agent_implementation/TSD-001_DCL_Agent.md` |

---

## Affected Components

- **Strategies:** `src/dcl_agent/strategies/gemini.py`, `src/dcl_agent/strategies/concat.py`.
- **Base:** `src/dcl_agent/strategies/base.py`.

---

## Output Artifacts

| Artifact | ID | Action | Description |
|----------|------|--------|-------------|
| Requirements | REQ-003 | New | Спецификация форматирования ресурсов. |
| Technical Design | TSD-003 | New | Дизайн логики в стратегиях. |
| Implementation Plan | IMP-003 | New | Бэклог задач реализации. |

---

## Regression Risks

- **Integration Tests:** Визуальная проверка через `verify_agent_real.py`.
- **LLM Context:** Анализ влияния добавленной разметки на корректность интерпретации контекста моделью.

---

## Open Questions

None

---

## Approval

- [ ] User has reviewed and approved this scope
- [ ] Agent can proceed to Stage 1: Requirements Elaboration
