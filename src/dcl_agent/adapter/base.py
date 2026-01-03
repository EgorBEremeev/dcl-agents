from abc import ABC, abstractmethod
from typing import Any
from ..model import InvocationContext

class ILLMAdapter(ABC):
    """
    Interface for LLM Adapters.
    Adapts the generic InvocationContext to the specific LLM API.
    """
    @abstractmethod
    def invoke(self, context: InvocationContext) -> str:
        """
        Invokes the LLM with the given context and returns the response string.
        """
        pass
