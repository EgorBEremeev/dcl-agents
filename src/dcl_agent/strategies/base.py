from abc import ABC, abstractmethod
from ..model import Instruction, InvocationContext, TextFrame, PromptModule
from ..loader.registry import PromptModuleRegistry

class IContextAssemblyStrategy(ABC):
    """
    Interface for context assembly strategies.
    Converts a DCL Instruction and available Modules into an InvocationContext.
    """
    @abstractmethod
    def assemble(self, instruction: Instruction, registry: PromptModuleRegistry) -> InvocationContext:
        """
        Converts a DCL Instruction and available Modules into an InvocationContext.
        """
        pass

    @staticmethod
    def _format_resource_as_markdown(module: PromptModule) -> str:
        """
        Wraps module content in markdown if module.type == 'RESOURCE'.
        Otherwise returns raw content.

        Args:
            module: The PromptModule to format.

        Returns:
            The formatted content string.
        """
        if module.type == 'RESOURCE':
            return f"```{module.id}\n{module.content}\n```"
        return module.content



zero_frame_text = """
    # AGENT ANSWER FORMAT and EXAMPLE
    
    human:
    ```
    WRITE PromptModule('sys/goals/completeness_consistency.yaml')
    FROM 'sowftware engineering best practices'
    USING Lens(sys/lenses/component_arch_v2', 'sys/frameworks/dcl_core/v22.2')
    ```

    agent:
    Принято. Выполнение операции `WRITE` для сущности 'PROMPT_MODULE'.

    **Исполнитель:** Агент-Методолог (использующий логику `sys/ops/write_v4.md`).
    **Интенция:** Создать модуль Цели (`GOAL`), который заставит Оператора приоритезировать полноту и непротиворечивость данных.
    **Линзы:** DCL Domain Ontology and Specification, Компонентная Архитектура v2.0.

    ---

    ### Артефакт: `sys/goals/completeness_consistency.yaml`

    ```sys/goals/completeness_consistency.yaml
    ...  результат генерации
    ```
    """

zero_context_frame = TextFrame(content=zero_frame_text)