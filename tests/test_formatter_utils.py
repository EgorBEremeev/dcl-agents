import pytest
from dcl_agent.strategies.base import IContextAssemblyStrategy
from dcl_agent.model import PromptModule

def test_format_resource_as_markdown_with_resource():
    """RESOURCE type should be wrapped in markdown with ID as language tag."""
    module = PromptModule(
        id="sys/lenses/test",
        version="1.0",
        type="RESOURCE",
        content="test content"
    )
    # Note: Using class name since it will be a static method
    formatted = IContextAssemblyStrategy._format_resource_as_markdown(module)
    assert formatted == "```sys/lenses/test\ntest content\n```"

def test_format_resource_as_markdown_with_operator():
    """OPERATOR type (or any non-RESOURCE) should return raw content."""
    module = PromptModule(
        id="sys/ops/write",
        version="1.0",
        type="OPERATOR",
        content="operator content"
    )
    formatted = IContextAssemblyStrategy._format_resource_as_markdown(module)
    assert formatted == "operator content"

def test_format_resource_as_markdown_empty_content():
    """Should handle empty content correctly for RESOURCE."""
    module = PromptModule(
        id="empty/res",
        version="1.0",
        type="RESOURCE",
        content=""
    )
    formatted = IContextAssemblyStrategy._format_resource_as_markdown(module)
    assert formatted == "```empty/res\n\n```"
