# Формат compiled spec (`service-views/<service>/specs/<operation>.yaml`)

Compiled spec — это детерминированный контракт инвокации LLM для конкретного сервиса runtime.

## Структура файла

```yaml
schema_version: llm-invocation-spec.v1
service_id: <service_id>         # Например: inventory-srv
workflow_id: <workflow_id>       # Например: inventory_management
operation_id: <operation_id>     # Строго совпадает с manifest.yaml сервиса
dcl_bundle: <bundle_name>        # Например: adpilot-core
dcl_instruction: |               # Буквальная DCL-инструкция, компилируемая в контекст
  EXTRACT Entity('Attribute_Data')
  FROM Entity('Raw_Description')

invocation:
  model_id: gemini-2.5-flash-lite
  thinking_budget: 0             # 0 — отключено, -1 — авто
  system_instruction: |          # Скомпилированные Frames (вывод dcl-agent compile)
    # Frame 1:
    ...
  input_placeholders:            # Имена входных XML-тегов, маппятся на _invoke(**inputs)
    - source_text
  output:
    mode: dynamic_structured     # text | static_structured | dynamic_structured
    schema_format: gemini_openapi_dict.v1 # Обязательно для structured-режимов
    # response_schema: {...}    # Заполняется ТОЛЬКО в режиме static_structured
```

## Синтаксис `dcl_instruction`

Грамматика:
```dcl
ОПЕРАТОР Entity('Операнд') [FROM Entity('Источник')] [USING Ресурс1, Ресурс2] [OPTIMIZING_FOR Цель]
```
- Оператор из начала инструкции **не должен** дублироваться в `USING`.
- `dcl_instruction` в заголовке спеки и в манифесте сервиса — это DSL-команда, а не текстовое пояснение.

## Профиль `gemini_openapi_dict.v1`

Для режимов `static_structured` и `dynamic_structured` выходная схема обязана следовать профилю runtime:
- Корневой объект: `type: object`;
- Допустимые ключи узла: `type`, `title`, `description`, `properties`, `required`, `items`, `enum`;
- Допустимые скалярные типы: `string`, `integer`, `number`, `boolean`;
- Допустимые составные типы: `object`, `array`;
- **Явно запрещены:** `$schema`, `$id`, `$defs`, `definitions`, `$ref`, `oneOf`, `anyOf`, `allOf`, `if/then/else`, `patternProperties`, `unevaluatedProperties`, любые расширения `x-*`;
- В режиме `dynamic_structured` поле `response_schema` в спеке отсутствует (схема передается runtime-клиентом через `.with_schema(...)`).
