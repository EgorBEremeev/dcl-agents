import pytest
from dcl_agent.loader.loader import Loader
from dcl_agent.loader.registry import PromptModuleRegistry

@pytest.fixture
def loader():
    registry = PromptModuleRegistry()
    return Loader(registry)

def test_load_raw_resource(loader, tmp_path):
    # Create a bundle with a raw text file
    bundle_root = tmp_path / "my_bundle"
    bundle_root.mkdir()
    
    # Raw file
    raw_file = bundle_root / "data" / "note.txt"
    raw_file.parent.mkdir()
    raw_file.write_text("Just some text", encoding="utf-8")
    
    loader.load_bundles([str(bundle_root)])
    
    # Expected ID: my_bundle/data/note.txt
    expected_id = "my_bundle/data/note.txt"
    module = loader.registry.get(expected_id)
    
    assert module is not None
    assert module.type == "RESOURCE"
    assert module.content == "Just some text"
    assert module.version == "1.0"
    
def test_load_unknown_extension(loader, tmp_path):
    # Verify permissive loading
    bundle_root = tmp_path / "permissive"
    bundle_root.mkdir()
    
    (bundle_root / "script.lua").write_text("print('lua')", encoding="utf-8")
    
    loader.load_bundles([str(bundle_root)])
    
    module = loader.registry.get("permissive/script.lua")
    assert module is not None
    assert "lua" in module.content

def test_alias_to_raw_resource(loader, tmp_path):
    # Test index.yaml mapping to a raw resource ID
    bundle = tmp_path / "b_alias"
    bundle.mkdir()
    
    import yaml
    (bundle / "index.yaml").write_text(yaml.dump({
        "aliases": {
            "MY_NOTE": "b_alias/note.txt"
        }
    }), encoding="utf-8")
    
    (bundle / "note.txt").write_text("Aliased Content", encoding="utf-8")
    
    loader.load_bundles([str(bundle)])
    
    # Check Alias Resolution
    resolved = loader.registry.get("MY_NOTE")
    assert resolved is not None
    assert resolved.content == "Aliased Content"
    assert resolved.id == "b_alias/note.txt"
