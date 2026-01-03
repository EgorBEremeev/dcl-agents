import pytest
from unittest.mock import MagicMock
from dcl_agent.strategies.concat import ConcatenationStrategy
from dcl_agent.model import Instruction, Entity, PromptModule, InvocationContext, TextFrame
from dcl_agent.loader.registry import PromptModuleRegistry

def test_concat_strategy_resource_formatting():
    """ConcatenationStrategy should wrap RESOURCE modules in markdown."""
    strategy = ConcatenationStrategy()
    
    # 1. Mock Registry
    registry = MagicMock(spec=PromptModuleRegistry)
    
    # Create a resource module
    res_id = "sys/lenses/formatting"
    res_module = PromptModule(
        id=res_id,
        version="1.0",
        type="RESOURCE",
        content="formatting rules content"
    )
    registry.get.side_effect = lambda mod_id: res_module if mod_id == res_id else None
    
    # 2. Create Instruction with this resource as a modifier
    instruction = Instruction(
        action="WRITE",
        operand=Entity(type="ANY", value="Target"),
        sources=[],
        modifiers=[MagicMock(id=res_id)],
        goals=[],
        original_dcl_instruction=f"WRITE Target USING {res_id}"
    )
    
    # 3. Assemble
    context = strategy.assemble(instruction, registry)
    
    # 4. Assert
    # ConcatenationStrategy returns a single TextFrame.
    assert len(context.frames) == 1
    full_text = context.frames[0].content
    
    expected_part = f"```{res_id}\nformatting rules content\n```"
    assert expected_part in full_text, f"Formatted resource part not found in concatenated text. Full text: {full_text}"
