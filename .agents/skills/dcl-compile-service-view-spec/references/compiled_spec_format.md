# Формат compiled spec (`service-views/<service>/specs/<operation>.yaml`)

Compiled spec — это детерминированный контракт инвокации LLM для конкретного сервиса runtime (версия `llm-invocation-spec.v2`, Gemini Interactions API `v1` GA).

## Структура файла

```yaml
schema_version: llm-invocation-spec.v2
service_id: <service_id>         # Например: inventory-srv
workflow_id: <workflow_id>       # Например: inventory_management
operation_id: <operation_id>     # Строго совпадает с manifest.yaml сервиса
dcl_bundle: <bundle_name>        # Например: adpilot-core
dcl_instruction: |               # Буквальная DCL-инструкция, компилируемая в контекст
  EXTRACT Entity('Attribute_Schema')
  FROM Entity('Draft_Record')

invocation:
  model_id: gemini-3.5-flash-lite
  thinking_level: minimal        # minimal | low | medium | high | xhigh (клампится по модели)
  store: false                   # Stateless вызов без хранения истории на сервере
  fallback_models:               # Опционально; runtime ограничивает до max 3 попыток всего
    - model_id: gemini-3.6-flash
      thinking_level: minimal
    - model_id: gemini-4-hydrogen
      thinking_level: low
  system_instruction: |          # Скомпилированные Frames (вывод dcl-agent compile)
    # Frame 1:
    ...
  input_placeholders:            # Имена входных XML-тегов, маппятся на invoke_operation(**inputs)
    - source_text
  output:
    mode: dynamic_structured     # text | static_structured | dynamic_structured
    schema_format: json_schema.v1 # Обязательно для structured-режимов
    # response_schema: {...}    # Заполняется ТОЛЬКО в режиме static_structured
```

## Синтаксис `dcl_instruction`

Грамматика:
```dcl
ОПЕРАТОР Entity('Операнд') [FROM Entity('Источник')] [USING Ресурс1, Ресурс2] [OPTIMIZING_FOR Цель]
```
- Оператор из начала инструкции **не должен** дублироваться в `USING`.
- `dcl_instruction` в заголовке спеки и в манифесте сервиса — это DSL-команда, а не текстовое пояснение.

## Профиль `json_schema.v1`

Для режимов `static_structured` и `dynamic_structured` выходная схема передаётся в `response_format` (`type: "text"`, `mime_type: "application/json"`, `schema: ...`) Interactions API и следует стандарту JSON Schema:
- Корневой объект: `type: object`;
- Нативно поддерживаются `type: ["string", "null"]` (nullable поля), `additionalProperties: false`, `$defs` / `$ref` (включая вложенность и рекурсию), `anyOf`, `prefixItems`, `enum`, `required`;
- Vendor extensions `x-*` запрещены как ключевые слова на узле схемы, однако допустимы как бизнес-ключи внутри `properties` (например, `properties["x-dcl-meta"]`);
- В режиме `dynamic_structured` поле `response_schema` в спеке отсутствует (схема передается runtime-клиентом через `.with_schema(...)`).
