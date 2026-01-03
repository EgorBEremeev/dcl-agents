import pytest
from dcl_agent.loader.registry import PromptModuleRegistry
from dcl_agent.model import PromptModule
from dcl_agent.exceptions import (
    AliasAlreadyExistsWarning,
    DuplicateIdWarning,
    InvalidAliasError,
    DCLConfigurationError
)

def test_register_alias_success():
    registry = PromptModuleRegistry()
    registry.register_alias("WRITE", "sys/ops/write/1.0")
    # Access private member to verify storage (white-box test for storage)
    assert registry._aliases["WRITE"] == "sys/ops/write/1.0"

def test_register_alias_duplicate_warning():
    registry = PromptModuleRegistry()
    registry.register_alias("WRITE", "first/target")
    
    with pytest.warns(AliasAlreadyExistsWarning):
        registry.register_alias("WRITE", "second/target")
    
    # Verify first one remains
    assert registry._aliases["WRITE"] == "first/target"

def test_register_module_success():
    registry = PromptModuleRegistry()
    module = PromptModule(id="mod/1", type="test", content="c", version="1.0")
    registry.register(module)
    assert registry.get("mod/1") == module

def test_register_module_duplicate_warning():
    registry = PromptModuleRegistry()
    m1 = PromptModule(id="mod/1", type="test", content="content1", version="1.0")
    m2 = PromptModule(id="mod/1", type="test", content="content2", version="1.0")
    
    registry.register(m1)
    
    with pytest.warns(DuplicateIdWarning):
        registry.register(m2)
    
    # Verify first one remains
    assert registry.get("mod/1").content == "content1"

def test_get_resolves_alias():
    registry = PromptModuleRegistry()
    module = PromptModule(id="real/id", type="test", content="c", version="1.0")
    registry.register(module)
    registry.register_alias("MY_ALIAS", "real/id")
    
    result = registry.get("MY_ALIAS")
    assert result == module

def test_validate_aliases_success():
    registry = PromptModuleRegistry()
    registry.register(PromptModule(id="exist", type="t", content="c", version="1"))
    registry.register_alias("A", "exist")
    # Should not raise
    registry.validate_aliases()

def test_validate_aliases_failure():
    registry = PromptModuleRegistry()
    registry.register_alias("A", "missing_id")
    
    with pytest.raises(InvalidAliasError):
        registry.validate_aliases()
