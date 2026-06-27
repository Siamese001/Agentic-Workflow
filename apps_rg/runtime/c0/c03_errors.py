"""Shared C0.3 exception types with no runtime-spine imports."""

from __future__ import annotations


class RoleFamilyProjectionError(RuntimeError):
    """Raised when role-family targeting cannot be resolved from the graph SSOT."""

