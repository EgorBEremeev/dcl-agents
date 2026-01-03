from typing import Optional, Dict
from .model import InvocationContext, Instruction
from .loader.registry import PromptModuleRegistry
from .loader.loader import Loader
from .parser.parser import DCLParser
from .strategies.base import IContextAssemblyStrategy
from .strategies.gemini import GeminiNativeStrategy
from .adapter.base import ILLMAdapter
from .adapter.gemini import GeminiAdapter

class DCLAgent:
    """
    Main Agent Orchestrator.
    Configures and executes DCL pipelines.
    """
    def __init__(
        self, 
        bundles: list[str] | str,
        adapter: ILLMAdapter = None,
        strategy: IContextAssemblyStrategy = None
    ):
        """
        Args:
            bundles: List of root paths to load DCL artifacts from (or single path string).
            adapter: LLM Adapter to use (defaults to GeminiAdapter).
            strategy: Assembly Strategy to use (defaults to GeminiNativeStrategy).
        """
        self.registry = PromptModuleRegistry()
        self.loader = Loader(self.registry)
        
        # Normalize to list
        if isinstance(bundles, str):
            bundle_paths = [bundles]
        else:
            bundle_paths = bundles

        # Load artifacts immediately
        self.loader.load_bundles(bundle_paths)
        
        self.parser = DCLParser()
        self.adapter = adapter if adapter else GeminiAdapter()
        self.strategy = strategy if strategy else GeminiNativeStrategy()
        
        # Simple Cache: Instruction Hash -> InvocationContext
        # (Not implemented fully in v1, but placeholder)
        self._context_cache: Dict[str, InvocationContext] = {}

    def execute(self, instruction_text: str) -> str:
        """
        Executes a DCL instruction text.
        Returns the LLM response.
        """
        # 1. Parse
        instruction = self.parser.parse(instruction_text)
        
        # 2. Assemble Context
        context = self.strategy.assemble(instruction, self.registry)
        
        # 3. Invoke LLM
        return self.adapter.invoke(context)
        
    def get_registry(self) -> PromptModuleRegistry:
        return self.registry
