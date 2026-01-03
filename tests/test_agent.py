import pytest
from dcl_agent.agent import DCLAgent
from dcl_agent.adapter.mock import MockLLMAdapter

@pytest.fixture
def mock_path(tmp_path):
    # Create a dummy operator and lens in tmp_path
    op = tmp_path / "op.yaml"
    op.write_text("id: write\nversion: 1.0\ntype: OPERATOR\ncontent: You write things.", encoding="utf-8")
    
    lens = tmp_path / "lens.yaml"
    lens.write_text("id: lens\nversion: 1.0\ntype: MODIFIER\ncontent: Be brief.", encoding="utf-8")
    return str(tmp_path)

def test_agent_integration(mock_path):
    adapter = MockLLMAdapter(fixed_response="Generated Content")
    agent = DCLAgent(bundles=mock_path, adapter=adapter)
    
    # Verify loading happened
    assert agent.get_registry().get("write/1.0") is not None
    
    # Execute
    result = agent.execute("write/1.0 'Topic' USING lens/1.0")
    
    assert result == "Generated Content"
    
    # Verify Context passed toAdapter
    ctx = adapter.last_context
    assert ctx is not None
    # Check if context contains operator and lens content
    texts = [f.content for f in ctx.frames]
    assert any("You write things" in t for t in texts)
    assert any("Be brief" in t for t in texts)
    assert any("Topic" in t for t in texts)
