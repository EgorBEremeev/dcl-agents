# Технологическое Решение: DCL Agent

**Версия:** 1.0 (Final)
**Основание:** [REQ-001_DCL_Agent_Requirements.md](file:///c:/git/dcl/.workspace/dcl_agent_implementation/REQ-001_Requirements_Specification.md)

---

## 1. Архитектура Системы

### 1.1 Общие Принципы
*   **Stateless:** Класс `DCLAgent` не хранит состояние сессии.
*   **Separation of Concerns:** Четкое разделение на парсинг, сборку контекста и вызов LLM.

### 1.2 Компоненты
1.  **Loader (Configurator):** Отвечает за сканирование файловой системы и загрузку prompt modules bundles (Core + Domain).
2.  **Compiler (Parser):** Преобразует строковую инструкцию DCL в промежуточное представление (`Instruction`).
3.  **Context Assembler:** Реализует паттерн Стратегия. Принимает `Instruction` и загруженные модули, возвращает `InvocationContext`.
4.  **LLM Adapter:** Обертка над `google.genai` для отправки `InvocationContext`.

---

## 2. Стек Технологий (Technology Stack)
*   **Language:** Python 3.12+
*   **Parsing:** `lark` (EBNF parser generator) — для надежного разбора грамматики v2.2.
*   **LLM Integration:** `google-genai` (Official SDK) — для работы с Gemini API.
*   **Testing:** `pytest` — для модульного и интеграционного тестирования.

## 3. Архитектура и Проектирование Компонентов

### 3.1 Parsing Strategy
*   **Decision:** Использование **Lark**.
*   **Reasoning:** Грамматика v2.2 требует обработки вложенных структур (Functional Style Resources).

### 3.2 Context Assembly Strategy Pattern
*   **Interface:** `IContextAssemblyStrategy`
*   **Unification:** Все стратегии возвращают унифицированный объект `InvocationContext`.
    *   **Abstraction:** `InvocationContext` не зависит от конкретного LLM-провайдера. Он содержит список платформо-независимых частей (`ContextFrame`).
    *   **Adapter Responsibility:** Адаптер (например, для Gemini) отвечает за конвертацию `ContextFrame` в специфичные типы SDK (например, `genai.types.Part`).

### 3.3 Caching & Hot Reloading
*   **Mechanism:** `DCLAgent` загружает артефакты в `PromptModuleRegistry` при инициализации.
*   **Hot Reload:** Метод `reload()` принудительно обновляет реестр с диска.

---

## 4. Детальная последовательность выполнения (Sequence Flow)

**Контекст:** Пользователь (или внешний Runtime) вызывает метод `agent.execute(instruction)`.

1.  **[DCLAgent] Инициализация и Парсинг:**
    *   Агент передает входную строку `instruction_text` в компонент `DCLParser`.
    *   Возвращает структурированный объект `Instruction`, содержащий:
        *   `action`: Идентификатор оператора (например, "WRITE").
        *   `operand`: Объект `Entity(type, value)`, представляющий цель операции (Операнд).
        *   `modifiers`: Список применяемых линз и фреймворков.
        *   `resources`: Список ссылок на источники данных.

2.  **[DCLAgent] Выбор Стратегии:**
    *   Агент обращается к `StrategyFactory` для получения экземпляра стратегии сборки.
    *   Выбор стратегии определяется конфигурацией (по умолчанию `GeminiNativeStrategy`).

3.  **[ContextStrategy] Сборка Контекста (Interpretation & Assembly):**
    *   Агент вызывает метод `assemble(instruction, registry)` у выбранной стратегии.
    *   **Шаг 3.1: Интерпретация Типов.** Стратегия анализирует типы операндов (`type`). Если тип известен стратегии (например, `PromptModule`), она обращается к `PromptModuleRegistry`. Если тип неизвестен, стратегия может обработать его иначе или выбросить ошибку. В этом суть "Universal DCL" — семантика типов определяется Runtime-стратегией, а не Парсером.
    *   **Шаг 3.2: Формирование Частей.**
        *   Стратегия преобразует контент модулей в унифицированные объекты `ContextFrame` (см. API Контракты).
        *   Текстовые модули становятся `TextFrame`.
        *   Файлы или изображения становятся `BlobFrame` (или аналогичными абстракциями).
    *   Стратегия возвращает наполненный объект `InvocationContext`.

4.  **[LLMAdapter] Адаптация и Вызов API:**
    *   Агент передает `InvocationContext` в `LLMAdapter`.
    *   **Шаг 4.1: Конвертация.** Адаптер (специфичный для Gemini) проходит по списку `frames` внутри контекста и преобразует их в формат `google.genai`:
        *   `TextFrame` -> `types.Part.from_text(...)`
        *   `BlobFrame` -> `types.Part.from_bytes(...)` или `types.Part.from_uri(...)`
    *   **Шаг 4.2: Сетевой вызов.** Адаптер выполняет запрос к API (например, `models.generate_content`).
    *   Возвращает стандартизированный ответ (текст или объект ответа) обратно в Агент.

5.  **[DCLAgent] Возврат результата:**
    *   Агент возвращает результат вызова пользователю.

---

## 5. API Контракты (API Contracts)

### 5.1 Domain Objects (Provider-Agnostic)

```python
@dataclass
class ContextFrame:
    """Base class for frames (parts) of the prompt."""
    pass

@dataclass
class TextFrame(ContextFrame):
    content: str  # The actual text content. Could be extended to a dict if metadata is needed.

@dataclass
class BlobFrame(ContextFrame):
    mime_type: str
    data: bytes  # For small binary payloads
    uri: Optional[str] = None # For Cloud Storage URIs

@dataclass
class InvocationContext:
    """
    Holds the assembled context in a generic format.
    """
    frames: List[ContextFrame] = field(default_factory=list)
    """
    List of content frames (Text, Images, etc.) representing the input task/message.
    """

    tools: List[Any] = field(default_factory=list) # Generic tool definitions
```

### 5.2 Interface `IContextAssemblyStrategy`
```python
class IContextAssemblyStrategy(ABC):
    @abstractmethod
    def assemble(self, instruction: Instruction, registry: PromptModuleRegistry) -> InvocationContext:
        """
        Transforms abstract Instruction into a provider-agnostic InvocationContext.
        """
        pass
```

### 5.3 Class `DCLAgent`
```python
class DCLAgent:
    def __init__(self, core_path: Union[str, Path], domain_path: Union[str, Path]):
        """
        Initializes agent, loading dcl-core prompt modules bundle and domain bundle.
        """
        self.registry: PromptModuleRegistry = ...

    def execute(self, instruction: str, strategy: str = "gemini_native") -> Any:
        """
        Executes a DCL instruction.
        
        Example:
            agent.execute(
                "WRITE PromptModule('NewOp') FROM Source('Spec.md') "
                "USING Lens('ArchitecturalStyle'), Framework('DCL_v2') "
                "OPTIMIZING_FOR Goal('Clarity')"
            )
        """
        pass
```
