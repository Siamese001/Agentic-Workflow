"""Centralized shim that falls back to local stubs when pydantic is unavailable."""

from __future__ import annotations

try:  # pragma: no cover - exercised when pydantic is installed
    from pydantic import BaseModel, ConfigDict, Field, ValidationError
except ModuleNotFoundError:  # pragma: no cover - default in lightweight CI
    from vendor.pydantic_stub import BaseModel, ConfigDict, Field, ValidationError

__all__ = ["BaseModel", "ConfigDict", "Field", "ValidationError"]
