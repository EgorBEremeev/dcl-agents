import pytest
from lark.exceptions import UnexpectedToken
from dcl_agent.parser.parser import DCLParser
from dcl_agent.model import Instruction

@pytest.fixture
def parser():
    return DCLParser()

def test_parse_simple_action(parser):
    text = "WRITE 'System Architecture'"
    instr = parser.parse(text)
    assert instr.action == "WRITE"
    assert instr.operand.value == "System Architecture"
    assert instr.operand.type == "ANY"
    assert len(instr.sources) == 0

def test_parse_typed_operand(parser):
    text = "WRITE PromptModule('sys/goals/g1')"
    instr = parser.parse(text)
    assert instr.action == "WRITE"
    assert instr.operand.type == "PromptModule"
    assert instr.operand.value == "sys/goals/g1"

def test_parse_full_instruction(parser):
    text = "WRITE 'Code' FROM Spec('s1') USING Lens('l1'), Lens('l2') OPTIMIZING_FOR Goal('g1')"
    instr = parser.parse(text)
    
    assert instr.action == "WRITE"
    assert instr.operand.value == "Code"
    assert instr.operand.type == "ANY"
    
    assert len(instr.sources) == 1
    assert instr.sources[0].id == "s1"
    assert instr.sources[0].type == "Spec"
    
    assert len(instr.modifiers) == 2
    assert instr.modifiers[0].id == "l1"
    assert instr.modifiers[0].type == "Lens"
    
    assert len(instr.goals) == 1
    assert instr.goals[0].id == "g1"

def test_parse_namespace_id(parser):
    text = "sys/ops/write 'Target' FROM sys/res/spec"
    instr = parser.parse(text)
    assert instr.action == "sys/ops/write"
    assert instr.sources[0].id == "sys/res/spec"

def test_invalid_syntax(parser):
    text = "INVALID SYNTAX HERE"
    with pytest.raises(UnexpectedToken):
        parser.parse(text)
