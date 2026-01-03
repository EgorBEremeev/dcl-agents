---
trigger: always_on
description: Требует трекинг времени для каждой стадии в Task List
---

# Rule: Time Tracking

**Scope:** Applies to all stages defined in currently applied workflow.

---

## Rationale (Обоснование)

Активная память агента сохраняет историю диалога и метаданные сообщений (`ADDITIONAL_METADATA.local_time`) только до момента чекпоинтов или исчерпания окна контекста. Для предотвращения потери данных о трудозатратах, метрики должны рассчитываться и фиксироваться в персистентном файле (Task List) немедленно по завершении каждой стадии.

---

## Metrics to Track

Для каждой стадии рассчитываются следующие показатели:

1. **Duration (Общая длительность):** Разница во времени между первым сообщением пользователя в рамках стадии и моментом завершения последнего шага (Step) этой стадии.

2. **Agent Efforts (Затраты агента):** Сумма интервалов времени работы инструментов (выполнения Steps) внутри стадии.

3. **Human Efforts (Затраты человека):** `Duration` минус `Agent Efforts`. Это время, затраченное пользователем на чтение, размышления, написание ответов и ревью.

4. **Period (Период):** Время начала и окончания стадии в формате `HH:MM-HH:MM`.

5. **Iterations:** Количество циклов ревью пользователем результатов (артефактов) агента.

---

## Integration with Task List

When creating Task List (at the start of assignment), add time tracking as **boundary tasks** for EACH stage:

### At the Beginning of Each Stage:
```markdown
- [ ] Record start time for Stage X (format: HH:MM)
```

### At the End of Each Stage (before moving to next stage):
```markdown
- [ ] Calculate and record metrics for Stage X:
  - Duration (HH:MM-HH:MM)
  - Agent efforts (Xm)
  - Human efforts (Xm)
  - Iteration count
- [ ] Update Task List with: [x] Stage X (Period: HH:MM-HH:MM, Agent: Xm, Human: Xm, N iterations)
```

**Important:** Time tracking tasks are **boundary tasks** (start/end of stages), NOT intermediate tasks within the stage.

---

## Example Task List Integration

```markdown
## Stage 1: Requirements Elaboration

- [x] Record start time for Stage 1 (12:30)
- [x] Read base REQ-001 identified in SCOPE
- [x] Analyze requirements for completeness
- [x] Create REQ-003_alias_support.md using template
- [x] Submit for review
- [x] Process feedback (iteration 1)
- [x] Process feedback (iteration 2)
- [x] Publish approved REQ to .workspace/
- [x] Calculate and record Stage 1 metrics (Period: 12:30-13:15, Agent: 8m, Human: 37m, 2 iterations)
```

---

## Finalization (Stage 5)

При создании `walkthrough.md` собрать все записи из Task List и сформировать итоговую таблицу «Time Statistics»:

```markdown
## Time Statistics

| Stage | Period | Duration | Agent Efforts | Human Efforts | Iterations |
|-------|--------|----------|---------------|---------------|------------|
| Stage 0: Impact Analysis | 11:45-12:15 | 30m | 5m | 25m | 1 |
| Stage 1: Requirements | 12:30-13:15 | 45m | 8m | 37m | 2 |
| Stage 2: Tech Design | 13:20-14:10 | 50m | 12m | 38m | 3 |
| Stage 3: Implementation Plan | 14:15-14:35 | 20m | 6m | 14m | 1 |
| Stage 4: Implementation | 14:40-16:20 | 100m | 85m | 15m | 0 |
| Stage 5: Verification | 16:25-17:00 | 35m | 20m | 15m | 1 |
| **Total** | **11:45-17:00** | **280m** | **136m** | **144m** | **8** |
```

---

## Why This Matters

- **Transparency:** User can see where time is spent (design vs implementation vs reviews).
- **Process Improvement:** Identify bottlenecks (e.g., too many review iterations indicate unclear requirements).
- **Retrospectives:** Historical data for estimating future sprints.
