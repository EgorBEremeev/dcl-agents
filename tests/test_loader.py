import pytest
import os
from dcl_agent.model import PromptModule
from dcl_agent.loader.registry import PromptModuleRegistry
from dcl_agent.loader.loader import Loader

@pytest.fixture
def registry():
    return PromptModuleRegistry()

@pytest.fixture
def loader(registry):
    return Loader(registry)

def test_registry_register_and_get(registry):
    module = PromptModule(id="test/mod1/1.0", version="1.0", type="TEST", content="foo")
    registry.register(module)
    
    # Get by full ID
    assert registry.get("test/mod1/1.0") == module
    # Get by alias (simple logic: last part? No, alias is fragile with versioning. 
    # Current registry alias logic splits by '/'. If ID is a/b/1.0, last part is 1.0. 
    # We might need to rethink aliases if we rely on them. 
    # But for now let's strict check full ID.)
    # assert registry.get("mod1") == module # Registry logic likely needs update if we want smart aliasing
    
    assert registry.get("nonexistent") is None

def test_loader_load_directory(registry, loader, tmp_path):
    # Create dummy files
    p1 = tmp_path / "mod1.yaml"
    p1.write_text("id: sys/ops/write\nversion: 1.0\ntype: OPERATOR\ncontent: abc", encoding="utf-8")
    
    p2 = tmp_path / "sub"
    p2.mkdir()
    p3 = p2 / "mod2.yaml"
    p3.write_text("id: domain/lens/tone\nversion: 2.1\ntype: MODIFIER\ncontent: xyz", encoding="utf-8")
    
    # Hidden file - should be ignored
    p4 = tmp_path / ".hidden.yaml"
    p4.write_text("id: hidden\ntype: TEST", encoding="utf-8")

    loader.load_from_directory(str(tmp_path))
    
    assert len(registry.list_modules()) == 2
    assert registry.get("sys/ops/write/1.0") is not None
    assert registry.get("domain/lens/tone/2.1") is not None

    # assert registry.get("write") is not None # Alias check removed as we use strict IDs now
    assert registry.get("hidden") is None

def test_loader_no_explicit_id(registry, loader, tmp_path):
    # File without ID in yaml
    p = tmp_path / "noid.txt"
    p.write_text("type: TEST\ncontent: foo", encoding="utf-8")
    
    loader.load_from_directory(str(tmp_path))
    
    # Should use filename stem "noid"
    # Loader generates ID as {bundle_name}/{rel_path}
    # Loader generates ID as {bundle_name}/{rel_path}
    bundle_name = tmp_path.name
    expected_id = f"{bundle_name}/noid.txt"
    assert registry.get(expected_id) is not None
