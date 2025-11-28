"""Public entry points for the vendored Pydantic shim."""
from .main import BaseModel, ConfigDict, Field, ValidationError

__all__ = ["BaseModel", "ConfigDict", "Field", "ValidationError"]
