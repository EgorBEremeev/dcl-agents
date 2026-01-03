from .base import IContextAssemblyStrategy, zero_context_frame
from ..model import Instruction, InvocationContext, TextFrame, PromptModule
from ..loader.registry import PromptModuleRegistry

class ConcatenationStrategy(IContextAssemblyStrategy):
    """
    Simple strategy: concatenates all content into a single TextFrame.
    Useful for dumb LLMs or debugging.
    """
    def assemble(self, instruction: Instruction, registry: PromptModuleRegistry) -> InvocationContext:
        parts = []

        parts.append(instruction.original_dcl_instruction)
        
        parts.append(zero_context_frame.content)
        
        # 1. Resolve Resources (Operator, Sources, Modifiers)
        # Note: Order matters.
        
        # Operator content
        op_module = registry.get(instruction.action)
        if op_module:
             parts.append(self._format_module(op_module))
        else:
             parts.append(f"<!-- Missing Operator: {instruction.action} -->")

        # Modifiers (Context/System Prompt additions)
        for mod_ref in instruction.modifiers:
            mod_module = registry.get(mod_ref.id)
            if mod_module:
                parts.append(self._format_module(mod_module))
            else:
                parts.append(f"<!-- Missing Modifier: {mod_ref.id} -->")

        # Sources (Data/Input)
        for src_ref in instruction.sources:
            src_module = registry.get(src_ref.id)
            if src_module:
                parts.append(self._format_module(src_module))
            else:
                 parts.append(f"<!-- Missing Source: {src_ref.id} -->")

        # Target (The "Object" of the operation)
        # Operand is an Entity(type, value). We treat it as text target.
        if instruction.operand.type == "ANY":
            target_str = instruction.operand.value
        else:
            target_str = f"{instruction.operand.type}('{instruction.operand.value}')"
            
        parts.append(f"Target: {target_str}")
        
        # Goals
        for goal_ref in instruction.goals:
             goal_module = registry.get(goal_ref.id)
             if goal_module:
                 parts.append(f"Goal: {goal_module.content}")

        full_text = "\n\n".join(parts)
        return InvocationContext(frames=[TextFrame(content=full_text)])

    def _format_module(self, module: PromptModule) -> str:
        content = self._format_resource_as_markdown(module)
        return f"--- {module.type}: {module.id} ---\n{content}"
