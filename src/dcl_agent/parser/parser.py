from lark import Lark, Transformer
from pathlib import Path
from ..model import Instruction, ResourceRef, Entity

class DCLTransformer(Transformer):
    def instruction(self, items):
        action = items[0]
        sources = []
        modifiers = []
        goals = []
        
        for item in items[1:]:
            if isinstance(item, dict):
                if item['type'] == 'source':
                    sources = item['resources']
                elif item['type'] == 'modifier':
                    modifiers = item['resources']
                elif item['type'] == 'goal':
                    goals = item['resources']
                    
        return Instruction(
            action=action['operator'],
            operand=action['operand'],
            sources=sources,
            modifiers=modifiers,
            goals=goals
        )

    def action_clause(self, items):
        return {
            'operator': items[0],
            'operand': items[1]
        }
    
    def operand(self, items):
        # items[0] is either an Entity (from entity_expression or object_expression)
        return items[0]

    def entity_expression(self, items):
        # items: [IDENTIFIER, arguments]
        return Entity(type=str(items[0]), value=items[1])

    def arguments(self, items):
        # items[0] is the regex match object or string
        # We strip external quotes if it looks like a single string argument
        val = str(items[0]).strip()
        if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
             return val[1:-1]
        return val

    def object_expression(self, items):
        # Wraps simple string/id in Entity(type='ANY')
        return Entity(type='ANY', value=str(items[0]).strip("'\""))

    def source_clause(self, items):
        return {'type': 'source', 'resources': items[0]}
    
    def modifier_clause(self, items):
        return {'type': 'modifier', 'resources': items[0]}
    
    def goal_clause(self, items):
        return {'type': 'goal', 'resources': items[0]}

    def resource_list(self, items):
        return items

    def resource_expression(self, items):
        if len(items) == 2:
            return ResourceRef(id=items[1], type=items[0])
        else:
            return ResourceRef(id=items[0])

    def operator_id(self, items):
        return str(items[0])

    def resource_type(self, items):
        return str(items[0])

    def resource_id(self, items):
        return str(items[0]).strip("'\"")

class DCLParser:
    def __init__(self):
        grammar_path = Path(__file__).parent.parent / "dcl.lark"
        with open(grammar_path, 'r') as f:
            grammar = f.read()
        self.parser = Lark(grammar, start='instruction', parser='lalr')
        self.transformer = DCLTransformer()

    def parse(self, text: str) -> Instruction:
        tree = self.parser.parse(text)
        instruction = self.transformer.transform(tree)
        instruction.original_dcl_instruction = text
        return instruction
