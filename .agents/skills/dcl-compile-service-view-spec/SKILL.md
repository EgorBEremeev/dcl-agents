---
name: dcl-compile-service-view-spec
description: >-
  Используй, когда нужно скомпилировать или перекомпилировать compiled spec сервиса
  (service-views/<service>/specs/<operation>.yaml) из готового DCL prompt module через
  CLI dcl-agent. Не используй для сочинения или содержательной правки prompt module.
---

# Компиляция service-view spec из prompt module

Скилл выполняет **только компиляцию**. Содержание prompt module (роль, логика, шаги, ограничения)
не придумывается и не переписывается: это отдельная задача автора модуля.
`system_instruction` никогда не пишется вручную — это скомпилированный вывод `dcl-agent`.

Требуется установленный `dcl-agent` (`uv tool install --editable <путь к src/dcl_agent>`).
Бандлы передаются через `--bundles` (ядро dcl-core + бандл домена с модулями и `index.yaml`).

## Шаги

1. **Привести модуль к формату (только формат + минорная версия).**
   Проверить модуль по [prompt_module_format.md](./references/prompt_module_format.md).
   Допустимо лишь: исправить YAML/структуру секций (например, перевести `steps` на `steps: |`)
   и поднять версию на минорную (например, 1.2 → 1.3), если файл физически изменялся.
   Смысловые формулировки не трогать; если требуется содержательная переработка —
   остановиться и вернуть задачу автору модуля.
   Обновить алиас оператора в `index.yaml` на новую версию.
2. **Проверить реестр:**
   ```bash
   dcl-agent registry --bundles <path_to_dcl_core>,<path_to_domain_bundle>
   ```
   Убедиться, что алиас разрешается и нет предупреждений о невалидном YAML.
3. **Составить DCL-инструкцию** вида:
   ```dcl
   ОПЕРАТОР Entity('Целевой_Объект') FROM Entity('Источник') [USING Модификаторы]
   ```
   (см. [compiled_spec_format.md](./references/compiled_spec_format.md)).
   **Важно:** сам вызываемый оператор не повторять в клаузе `USING`.
4. **Скомпилировать:**
   ```bash
   dcl-agent compile --bundles <b1>,<b2> --instruction "<DCL_ИНСТРУКЦИЯ>" --output frames
   ```
   (стратегия компиляции по умолчанию — `GeminiNativeStrategy`).
5. **Собрать `system_instruction`** из полученных Frames в виде fenced-блоков по образцу
   [example_compiled_spec.yaml](./references/example_compiled_spec.yaml):
   - Frame 1: raw DCL-инструкция (блок `md`);
   - Frame 2: prompt-модуль оператора (блок `yaml`);
   - Frame 3+: операнд / сущности.
   Дамп `index.yaml` и `zero_context_frame` в compiled spec не включаются (они использовались только для симуляции в AI Studio).
6. **Заполнить заголовок и параметры инвокации** по [compiled_spec_format.md](./references/compiled_spec_format.md):
   - `dcl_instruction` — ровно тот же DCL-текст, что компилировался в шаге 3;
   - `invocation.model_id` и `invocation.thinking_budget`;
   - `output`: для структурированных ответов зафиксировать `schema_format: gemini_openapi_dict.v1`.
7. **Верифицировать результат:**
   - YAML парсится без ошибок;
   - `operation_id` строго совпадает с записью в `manifest.yaml` сервиса;
   - `input_placeholders` совпадают с именами параметров в коде вызова `_invoke(spec, **inputs)`;
   - Для structured-режима проверено соответствие профилю схемы без запрещенных мета-ключей.

## Типичные ошибки
- Конструкции шагов с двоеточиями ломают YAML-парсер — используй блок `steps: |`.
- Алиас в `index.yaml` не обновлен на новую версию модуля → `InvalidAliasError`.
- Оператор продублирован в `USING` → модуль оператора попадает в `system_instruction` дважды.
