import pytest
from unittest.mock import MagicMock
from dcl_agent.strategies.gemini import GeminiNativeStrategy
from dcl_agent.model import Instruction, Entity, PromptModule, InvocationContext, TextFrame
from dcl_agent.loader.registry import PromptModuleRegistry

def test_gemini_native_strategy_resource_formatting():
    """GeminiNativeStrategy should wrap RESOURCE sources in markdown."""
    strategy = GeminiNativeStrategy()
    
    # 1. Mock Registry
    registry = MagicMock(spec=PromptModuleRegistry)
    
    # Create a resource module
    res_module = PromptModule(
        id="sys/lenses/formatting",
        version="1.0",
        type="RESOURCE",
        content="formatting rules content"
    )
    registry.get.side_effect = lambda mod_id: res_module if mod_id == "sys/lenses/formatting" else None
    
    # 2. Create Instruction with this resource as a source
    instruction = Instruction(
        action="WRITE",
        operand=Entity(type="ANY", value="Target"),
        sources=[MagicMock(id="sys/lenses/formatting")], # Simplified mock for ResourceRef
        modifiers=[],
        goals=[],
        original_dcl_instruction="WRITE Target FROM sys/lenses/formatting"
    )
    
    # 3. Assemble
    context = strategy.assemble(instruction, registry)
    
    # 4. Assert
    # We expect several frames: original cmd, zero context, etc.
    # We look for a frame containing the formatted resource content.
    found_formatted = False
    expected_content = "```sys/lenses/formatting\nformatting rules content\n```"
    
    for frame in context.frames:
        if isinstance(frame, TextFrame) and expected_content in frame.content:
            found_formatted = True
            break
            
    assert found_formatted, f"Formatted resource content not found in context frames. Frames: {[f.content for f in context.frames]}"
