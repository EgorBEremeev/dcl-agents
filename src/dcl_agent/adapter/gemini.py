import os
from .base import ILLMAdapter
from ..model import InvocationContext, TextFrame, BlobFrame
# google-genai SDK imports
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

class GeminiAdapter(ILLMAdapter):
    """
    Adapter for Google Gemini API (using google-genai SDK 0.x/1.x).
    """
    def __init__(self, api_key: str = None, model_name: str = "gemini-2.0-flash-exp"):
        if not genai:
            raise ImportError("google-genai package is not installed.")
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
             # Warning or Error? For now letting client init without key if they want, 
             # but invoke will fail.
             pass

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def invoke(self, context: InvocationContext) -> str:
        if not self.api_key:
             return "Error: GOOGLE_API_KEY not set."

        # Convert InvocationContext to Gemini Content/Part objects
        contents = []
        
        # In Gemini 2.0 / SDK, we usually send a list of contents or parts.
        # We assume the Strategy has already ordered them correctly (System vs User).
        # However, google-genai SDK might require specific 'role': 'user'/'model' structure if chat.
        # For simple generate_content, we can pass a list of parts.
        
        parts = []
        for frame in context.frames:
            if isinstance(frame, TextFrame):
                parts.append(types.Part.from_text(text=frame.content))
            elif isinstance(frame, BlobFrame):
                 parts.append(types.Part.from_bytes(data=frame.data, mime_type=frame.mime_type))
        
        # We wrap parts in a generic Content if needed, or pass list of parts directly if supported.
        # generate_content usually takes 'contents'.
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(
                        parts=parts,
                        role="user" 
                    )
                ],
                config=types.GenerateContentConfig(
                    tools=context.tools if context.tools else None
                )
            )
            return response.text
        except Exception as e:
            return f"Gemini Error: {e}"
