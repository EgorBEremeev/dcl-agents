from .base import ILLMAdapter
from ..model import InvocationContext

class MockLLMAdapter(ILLMAdapter):
    """
    Mock adapter for offline testing.
    Returns a predefined response or an echo of the context.
    """
    def __init__(self, fixed_response: str = None):
        self.fixed_response = fixed_response
        self.last_context = None

    def invoke(self, context: InvocationContext) -> str:
        self.last_context = context
        if self.fixed_response:
            return self.fixed_response
        
        # Echo summary
        return f"Mock Response. Received {len(context.frames)} frames."
