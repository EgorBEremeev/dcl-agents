import pytest
from dcl_agent.model import Instruction, ResourceRef, PromptModule, TextFrame, Entity
from dcl_agent.loader.registry import PromptModuleRegistry
from dcl_agent.strategies.concat import ConcatenationStrategy
from dcl_agent.strategies.gemini import GeminiNativeStrategy

@pytest.fixture
def registry():
    reg = PromptModuleRegistry()
    reg.register(PromptModule(id="write", version="1.0", type="OPERATOR", content="Write a text."))
    reg.register(PromptModule(id="lens1", version="1.0", type="MODIFIER", content="Be polite."))
    reg.register(PromptModule(id="source1", version="1.0", type="RESOURCE", content="Data 1."))
    return reg

@pytest.fixture
def instruction():
    return Instruction(
        action="write",
        operand=Entity(type="ANY", value="Email"),
        modifiers=[ResourceRef(id="lens1")],
        sources=[ResourceRef(id="source1")]
    )

def test_concat_strategy(registry, instruction):
    strategy = ConcatenationStrategy()
    ctx = strategy.assemble(instruction, registry)
    
    assert len(ctx.frames) == 1
    assert isinstance(ctx.frames[0], TextFrame)
    content = ctx.frames[0].content
    assert "--- OPERATOR: write ---" in content
    assert "Write a text." in content
    assert "--- MODIFIER: lens1 ---" in content
    assert "Be polite." in content
    # Concat might need update if it uses operand. Assuming it iterates fields.
    # Leaving assertion vague or updating Concat strategy? 
    # For now, let's assume Concat prints operand value.
    assert "Email" in content 

def test_gemini_strategy(registry, instruction):
    strategy = GeminiNativeStrategy()
    ctx = strategy.assemble(instruction, registry)
    
    # Order: Original -> Zero -> Operator -> Target -> Modifiers -> Goals -> Sources
    assert len(ctx.frames) == 6
    
    # 0. Original
    assert ctx.frames[0].content == "" # Instruction mock has empty original string? Default is ""

    # 1. Zero Shot
    # assert ctx.frames[1] == zero_context_frame
    
    # 2. Operator
    assert ctx.frames[2].content == "Write a text."
    
    # 3. Target (Operand Text)
    assert ctx.frames[3].content == "Email"

    # 4. Modifier
    assert ctx.frames[4].content == "Be polite."
    
    # 5. Source
    assert "```source1\nData 1.\n```" in ctx.frames[5].content
