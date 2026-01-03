from dataclasses import dataclass, field
from typing import List, Any, Optional

@dataclass
class ContextFrame:
    """Base class for frames (parts) of the prompt."""
    pass

@dataclass
class TextFrame(ContextFrame):
    """Represents a text part of the prompt."""
    content: str

@dataclass
class BlobFrame(ContextFrame):
    """Represents a binary part of the prompt (image, audio, etc.)."""
    mime_type: str
    data: bytes  # For small binary payloads
    uri: Optional[str] = None # For Cloud Storage URIs

@dataclass
class PromptModule:
    """Represents a loaded DCL Prompt Module."""
    id: str
    version: str
    type: str # OPERATOR, MODIFIER, etc.
    content: str # Raw content (YAML/Text)
    metadata: dict = field(default_factory=dict)
    path: Optional[str] = None

@dataclass
class InvocationContext:
    """
    Holds the assembled context in a generic format.
    """
    frames: List[ContextFrame] = field(default_factory=list)
    """
    List of content frames (Text, Images, etc.) representing the input task/message.
    """

    tools: List[Any] = field(default_factory=list) # Generic tool definitions

@dataclass
class Entity:
    """Represents a generic DCL Entity (Structural)."""
    type: str  # e.g. "PromptModule", "Lens", "String"
    value: str # Content or Args, e.g. "sys/ops/write"

@dataclass
class ResourceRef:
    """Represents a reference to a DCL resource (e.g. Lens('Tone'))."""
    id: str  # The raw ID or Name
    type: Optional[str] = None # The explicit type if provided (e.g. Lens)

@dataclass
class Instruction:
    """Represents a parsed DCL instruction."""
    action: str # Operator ID
    operand: Entity # The object being operated on (Universal Entity)
    sources: List[ResourceRef] = field(default_factory=list) # FROM ...
    modifiers: List[ResourceRef] = field(default_factory=list) # USING ...
    goals: List[ResourceRef] = field(default_factory=list) # OPTIMIZING_FOR ...
    original_dcl_instruction: str = "" # The raw source DCL instruction text

