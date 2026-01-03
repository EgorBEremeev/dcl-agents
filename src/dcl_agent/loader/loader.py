import os
import yaml
import warnings
from typing import List
from pathlib import Path
from ..model import PromptModule
from ..exceptions import (
    AliasAlreadyExistsWarning, 
    DuplicateIdWarning,
    DCLConfigurationError
)
from .registry import PromptModuleRegistry

class Loader:
    """
    Scans directories and loads Prompt Modules into the Registry.
    Supports multi-bundle loading and index.yaml parsing.
    """
    def __init__(self, registry: PromptModuleRegistry):
        self.registry = registry

    def load_bundles(self, bundle_paths: List[str]):
        """
        Loads a list of bundles sequentially.
        """
        for path in bundle_paths:
            self._load_bundle(path)
        
        # After all loading, validate alias integrity
        self.registry.validate_aliases()

    def _load_bundle(self, path: str):
        """
        Loads a single bundle (Index + Scan).
        """
        root_path = Path(path)
        if not root_path.exists():
            print(f"Warning: Path {path} does not exist.")
            return

        # 1. Index Phase
        index_path = root_path / "index.yaml"
        if index_path.exists():
            try:
                content = yaml.safe_load(index_path.read_text(encoding="utf-8"))
                aliases = content.get("aliases", {})
                
                # Flatten alias structure if nested (entities/operations) or just dict
                # The example index.yaml has nested keys: entities: { ... }, operations: { ... }
                # We need to traverse them.
                # REQ says: "Maps simple Alias ... to Target Key".
                # TSD says: "Parse index.yaml ... Call registry.register_alias".
                # Let's assume recursion or flattened iteration. 
                # For `dcl-god-mode` it is categorized.
                self._register_aliases_recursive(aliases)

            except Exception as e:
                print(f"Error loading index.yaml in {path}: {e}")

        # 2. Scan Phase
        self.load_from_directory(str(root_path))

    def _register_aliases_recursive(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    # It's an alias mapping: Alias -> Target
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("error", category=AliasAlreadyExistsWarning)
                            self.registry.register_alias(key, value)
                    except AliasAlreadyExistsWarning:
                        # First-Wins: Ignore duplicates from subsequent bundles/files
                        pass 
                elif isinstance(value, dict):
                    self._register_aliases_recursive(value)

    def load_from_directory(self, path: str):
        """
        Recursively loads files from the given directory (Bundle Root).
        """
        root_path = Path(path)
        if not root_path.exists():
            print(f"Warning: Path {path} does not exist.")
            return

        # Scan for all files.
        # User requirement: No arbitrary restrictions. Load everything.
        for file_path in root_path.rglob("*"):
             if not file_path.is_file():
                 continue
             
             # Ignored patterns: Hidden files and the index itself.
             if file_path.name.startswith("."):
                 continue
             if file_path.name == "index.yaml":
                 continue

             self._load_file(file_path, root_path)

    def _load_file(self, file_path: Path, bundle_root: Path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. Try generic ID extraction (YAML/Header)
            module_id = None
            module_type = "RESOURCE" # Default type for raw
            version = "1.0"          # Default version for raw
            metadata = {}

            is_yaml = file_path.suffix in ['.yaml', '.yml']
            
            if is_yaml:
                try:
                    data = yaml.safe_load(content)
                    if isinstance(data, dict):
                        _id = data.get("id")
                        module_type = data.get("type", module_type)
                        version = data.get("version", version)
                        module_id = f"{_id}/{version}"
                        metadata = data
                except Exception:
                    # Not valid YAML, treat as raw text
                    pass
            
            # 2. Fallback ID Generation (Path-Based)
            # If no ID in content, use: {bundle_name}/{relative_path_from_bundle}
            if not module_id:
                bundle_name = bundle_root.name
                rel_path = file_path.relative_to(bundle_root).as_posix() # Forward slashes
                # Example: dcl-core/knowledges/ontology/dcl-core.ttl
                module_id = f"{bundle_name}/{rel_path}"
           
            module = PromptModule(
                id=str(module_id),
                version=str(version),
                type=str(module_type),
                content=content,
                metadata=metadata,
                path=str(file_path)
            )
                
            with warnings.catch_warnings():
                warnings.simplefilter("error", category=DuplicateIdWarning)
                self.registry.register(module)
            
        except DuplicateIdWarning:
            # First-Wins: Ignore
            pass
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
