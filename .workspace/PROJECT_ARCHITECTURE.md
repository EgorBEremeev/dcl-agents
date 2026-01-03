# Project Architecture: DCL Agent

**Version:** 1.0  
**Created:** 2025-12-06  
**Last Updated:** 2025-12-18

---

## Архитектурная стратегия и паттерны

Архитектура DCL Agent построена на принципе **модульной архитектуры (Modular Architecture)** с четким разделением ответственности между компонентами. Система спроектирована как **stateless orchestrator**, обеспечивающий трансляцию высокоуровневых DCL-инструкций в вызовы LLM API.

**Ключевой принцип:**
> **Strict Separation of Concerns** — каждый компонент отвечает за одну четко определенную задачу. Изменения в одном компоненте (например, замена парсера или добавление нового адаптера LLM) не требуют изменений в других компонентах.

**Основные паттерны:**
- **Strategy Pattern:** Для сборки контекста (различные стратегии для разных LLM-провайдеров)
- **Adapter Pattern:** Для абстрагирования от специфики LLM API
- **Registry Pattern:** Для управления загруженными промпт-модулями

---

## Контекст проектирования

**Целевые сценарии использования (текущая итерация):**
1. Исполнение DCL-инструкций с загрузкой множественных бандлов (dcl-core + domain bundles)
2. Разрешение алиасов для операторов и ресурсов
3. Сборка мультимодального контекста для Gemini API (текст + файлы)
4. Оффлайн-тестирование через Mock Adapter

**Не входит в scope:**
- Управление сессионным контекстом (историей диалога)
- Планирование многошаговых действий
- Персистентность состояния

---

## Структура системы

### Модульная архитектура

| Компонент | Ответственность |
|-----------|-----------------|
| **DCL Agent (Facade)** | Единая точка входа, оркестрирует работу всех компонентов. Предоставляет метод `execute(instruction)`. |
| **Loader and Registry** | Сканирует файловую систему, загружает промпт-модули из бандлов, разрешает алиасы из `index.yaml`. |
| **Parser** | Парсит DCL-инструкции в промежуточное представление (`Instruction`). Использует Lark для разбора грамматики. |
| **Strategy Module** | Реализует сборку `InvocationContext` через паттерн Стратегия (Concatenation, GeminiNative и др.). |
| **Adapter Module** | Инкапсулирует работу с LLM API (Gemini, Mock). Преобразует `InvocationContext` в формат конкретного провайдера. |

---

## Детали компонентов

### DCL Agent (Facade)

**Роль:** Фасад, объединяющий все компоненты в единый интерфейс.

**Ответственность:**
- Инициализация всех компонентов при старте (загрузка бандлов)
- Координация процесса исполнения инструкции: парсинг → сборка контекста → вызов адаптера
- Предоставление метода `reload()` для горячей перезагрузки бандлов

**Ключевой интерфейс:**
```python
class DCLAgent:
    def __init__(self, bundles: List[Union[str, Path]]):
        """Инициализирует агент, загружая prompt modules из списка бандлов."""
        pass
    
    def execute(self, instruction: str, strategy: str = "gemini_native") -> Any:
        """Исполняет DCL-инструкцию и возвращает ответ LLM."""
        pass
    
    def reload(self):
        """Перезагружает бандлы с диска (hot reload)."""
        pass
```

---

### Loader \u0026 Registry

**Роль:** Управление загрузкой и хранением промпт-модулей.

**Ответственность:**
- **Loader:** Рекурсивное сканирование папок бандлов, парсинг YAML-файлов, загрузка `index.yaml`
- **Registry:** Хранение модулей по ID, разрешение алиасов, валидация (обнаружение конфликтов)

**Ключевые интерфейсы:**
```python
class PromptModuleRegistry:
    def register_module(self, module: PromptModule):
        """Регистрирует модуль (First-Wins для дубликатов)."""
        pass
    
    def register_alias(self, alias: str, target_id: str):
        """Регистрирует алиас (First-Wins для дубликатов)."""
        pass
    
    def resolve(self, identifier: str) -> PromptModule:
        """Разрешает алиас или ID в модуль."""
        pass
    
    def validate_aliases(self):
        """Валидирует все алиасы (проверяет существование целей)."""
        pass

class Loader:
    def load_bundles(self, bundle_paths: List[Path], registry: PromptModuleRegistry):
        """Загружает бандлы и регистрирует модули + алиасы."""
        pass
```

---

### Parser

**Роль:** Синтаксический анализ DCL-инструкций.

**Ответственность:**
- Парсинг строки инструкции согласно DCL Grammar v2.3
- Преобразование в промежуточное представление `Instruction`
- **Агностичность:** Не интерпретирует семантику типов, только синтаксис

**Технология:** Lark (EBNF parser generator)

**Ключевой интерфейс:**
```python
class DCLParser:
    def parse(self, instruction_text: str) -> Instruction:
        """Парсит DCL-инструкцию в объект Instruction."""
        pass

@dataclass
class Instruction:
    operator: Entity            # OPERATOR
    operand: Entity             # OPERAND
    sources: List[Entity]       # FROM clause
    modifiers: List[Entity]     # USING clause
    optimizations: List[Entity] # OPTIMIZING_FOR clause
```

---

### Strategy Module

**Роль:** Сборка `InvocationContext` из `Instruction`.

**Ответственность:**
- Интерпретация типов сущностей (PromptModule, Lens, Source и др.)
- Загрузка контента из Registry
- Формирование платформо-независимого контекста

**Реализованные стратегии:**
1. **ConcatenationStrategy:** Линейное объединение контента модулей (для отладки)
2. **GeminiNativeStrategy:** Структурированная сборка с разделением на части (для мультимодальных запросов)

**Ключевой интерфейс:**
```python
class IContextAssemblyStrategy(ABC):
    @abstractmethod
    def assemble(self, instruction: Instruction, registry: PromptModuleRegistry) -> InvocationContext:
        """Собирает InvocationContext из инструкции."""
        pass

@dataclass
class InvocationContext:
    frames: List[ContextFrame]  # Части контекста (текст, файлы, изображения)
    tools: List[Any]            # Инструменты для LLM (опционально)
```

---

### Adapter Module

**Роль:** Абстрагирование от специфики LLM API.

**Ответственность:**
- Преобразование платформо-независимого `InvocationContext` в формат конкретного провайдера
- Выполнение сетевого запроса к LLM API
- Обработка ответа и возврат стандартизированного результата

**Реализованные адаптеры:**
1. **GeminiAdapter:** Интеграция с Google Gemini через `google-genai`
2. **MockLLMAdapter:** Оффлайн-мок для тестирования (возвращает эхо-ответ)

**Ключевой интерфейс:**
```python
class ILLMAdapter(ABC):
    @abstractmethod
    def invoke(self, context: InvocationContext) -> str:
        """Отправляет контекст в LLM и возвращает ответ."""
        pass
```

---

## Технологический стек

- **Runtime:** Python 3.12+
- **Parsing:** `lark` (EBNF parser generator)
- **LLM Integration:** `google-genai` (Official SDK)
- **Testing:** `pytest`
- **Data Validation:** Dataclasses (встроенная библиотека Python)
- **Configuration:** PyYAML

---

## Последовательность выполнения (Sequence Flow)

**Сценарий:** Пользователь вызывает `agent.execute("WRITE PromptModule('NewOp') USING Lens('ArchStyle')")`

1. **[DCLAgent]** Передает строку в `DCLParser`
2. **[DCLParser]** Возвращает объект `Instruction` с разобранной структурой
3. **[DCLAgent]** Получает экземпляр стратегии из `StrategyFactory`
4. **[Strategy]** Вызывает `assemble(instruction, registry)`:
   - Интерпретирует типы (`PromptModule`, `Lens`)
   - Загружает модули из Registry по ID или алиасу
   - Формирует список `ContextFrame` (текстовые блоки, файлы)
   - Возвращает наполненный `InvocationContext`
5. **[DCLAgent]** Передает контекст в `LLMAdapter`
6. **[Adapter]** Конвертирует `ContextFrame` в формат провайдера (например, `genai.types.Part`)
7. **[Adapter]** Выполняет API-запрос к LLM
8. **[Adapter]** Возвращает результат
9. **[DCLAgent]** Возвращает результат пользователю

---

## Масштабируемость и будущие расширения

**Возможности расширения:**
- **Новые стратегии сборки:** Добавление стратегий для OpenAI, Claude и других моделей
- **Новые адаптеры:** Поддержка дополнительных LLM-провайдеров
- **Persistence Layer:** Добавление слоя для кеширования результатов и управления версиями бандлов
- **Agent Layer:** Добавление слоя для multi-step планирования и автономных агентов

**Архитектурный фундамент:** Текущая модульная структура обеспечивает простоту добавления новых компонентов без изменения существующих.

---

## Детали реализации

**Физическая организация бандлов:**
- Корневая директория бандла содержит `index.yaml` (мапинг алиасов)
- Модули организованы в категории: `operations/`, `entities/`, `frameworks/`, `knowledges/`
- Каждый YAML-файл модуля содержит метаданные: `id`, `type`, `version`, `content`
- Ресурсы в `knowledges/` идентифицируются по пути (для non-YAML файлов)

**Стратегия разрешения конфликтов:**
- **First-Wins:** При дубликатах ID или алиасов используется первый загруженный, остальные логируются как Warnings
- **Валидация:** После загрузки всех бандлов проверяется корректность всех алиасов (существование целевых модулей)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-06 | Создание архитектуры на основе артефактов SP-001 и SP-002 |
