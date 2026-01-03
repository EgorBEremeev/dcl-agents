from .base import IContextAssemblyStrategy, zero_context_frame
from ..model import Instruction, InvocationContext, TextFrame, ContextFrame
from ..loader.registry import PromptModuleRegistry

class GeminiNativeStrategy(IContextAssemblyStrategy):
    """
    Structure-Aware Strategy.
    Keeps distinct parts of the DCL instruction as separate Context Frames.
    This allows the LLM Adapter to map them to specific API fields (System Instructions, User Message, etc.)
    although InvocationContext v0.7 removed system_instruction field, we can use metadata or order.
    
    Here we simply produce an ordered list of Frames. 
    The Adapter will likely treat the first few (Operator/Modifiers) as System Instruction 
    and the rest (Target/Sources) as User Message.
    """
    def assemble(self, instruction: Instruction, registry: PromptModuleRegistry) -> InvocationContext:
        frames: list[ContextFrame] = []

        frames.append(TextFrame(content=instruction.original_dcl_instruction))

        frames.append(zero_context_frame)
        
        # 1. Operator
        op_module = registry.get(instruction.action)
        if op_module:
            frames.append(TextFrame(content=op_module.content))

        # 2. Operand (Entity) - Treated as Textual Description of Target
        if instruction.operand.type == 'ANY':
            # Simple string/id
            frames.append(TextFrame(content=instruction.operand.value))
        else:
            # Typed Entity: Preserves the constructor syntax for the LLM
            # e.g. "PromptModule('sys/ops/write')"
            frames.append(TextFrame(content=f"{instruction.operand.type}('{instruction.operand.value}')"))


        # 3. Then Modifiers (Lenses) often define the Role/Constraint.
        for mod_ref in instruction.modifiers:
            mod_module = registry.get(mod_ref.id)
            if mod_module:
                content = self._format_resource_as_markdown(mod_module)
                frames.append(TextFrame(content=content))
        
            
        # 4. Goals (Soft Constraints)
        for goal_ref in instruction.goals:
            goal_module = registry.get(goal_ref.id)
            if goal_module:
                content = self._format_resource_as_markdown(goal_module)
                frames.append(TextFrame(content=content))
        
        # 5. Sources (Context Data)
        for src_ref in instruction.sources:
            src_module = registry.get(src_ref.id)
            if src_module:
                # Todo: Handle Blob Sources if type is Blob
                content = self._format_resource_as_markdown(src_module)
                frames.append(TextFrame(content=content))

        
        return InvocationContext(frames=frames)
