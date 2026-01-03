from typing import Dict, Optional, List, Union
from pathlib import Path
import warnings
from ..model import PromptModule
from ..exceptions import (
    AliasAlreadyExistsWarning, 
    DuplicateIdWarning, 
    InvalidAliasError
)

class PromptModuleRegistry:
    """
    Stores and manages loaded Prompt Modules and Resources.
    """
    def __init__(self):
        self._modules: Dict[str, PromptModule] = {}
        self._aliases: Dict[str, str] = {} # alias -> target_id

    def register(self, module: PromptModule) -> None:
        """
        Registers a module.
        Raises DuplicateIdWarning if ID exists (First-Wins).
        """
        if module.id in self._modules:
            warnings.warn(
                f"Module ID '{module.id}' already exists. Keeping original.",
                DuplicateIdWarning
            )
            return

        self._modules[module.id] = module

    def register_alias(self, alias: str, target_id: str) -> None:
        """
        Registers an explicit alias.
        Raises AliasAlreadyExistsWarning if alias exists.
        """
        if alias in self._aliases:
            warnings.warn(
                f"Alias '{alias}' already exists (target: {self._aliases[alias]}). "
                f"Ignoring new target: {target_id}",
                AliasAlreadyExistsWarning
            )
            return
            
        self._aliases[alias] = target_id
    
    def validate_aliases(self) -> None:
        """
        Checks integrity of all aliases.
        Raises InvalidAliasError if target is missing.
        """
        for alias, target in self._aliases.items():
            # Check modules (Resource paths checking logic to be added if mixed resources are supported)
            # For now we check _modules. If we had _resources list, we would check there too.
            if target not in self._modules:
                 raise InvalidAliasError(f"Alias '{alias}' points to missing target '{target}'")

    def get(self, key: str) -> Optional[PromptModule]:
        """Retrieves a module by ID or Alias."""
        # 1. Check direct ID
        if key in self._modules:
            return self._modules[key]
        
        # 2. Check Alias
        if key in self._aliases:
            target_id = self._aliases[key]
            return self._modules.get(target_id)
            
        return None

    def list_modules(self) -> List[str]:
        return list(self._modules.keys())

    def clear(self):
        self._modules.clear()
        self._aliases.clear()
