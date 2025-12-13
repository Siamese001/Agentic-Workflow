"""Enum types for models."""


class ValidationSeverity(Enum):
    """Severity levels for validation results."""
    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

class Provider(str, Enum):
    """Available LLM providers."""
    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'
    GOOGLE = 'google'
    MISTRAL = 'mistral'
    COHERE = 'cohere'
    GROQ = 'groq'
    TOGETHER = 'together'
    FIREWORKS = 'fireworks'

class APICallStatus(Enum):
    """Status of API calls."""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    TIMEOUT = auto()
    RATE_LIMITED = auto()
