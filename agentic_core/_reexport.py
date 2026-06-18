"""Helpers for compatibility shims that need to re-export a public API."""

from __future__ import annotations

from importlib import import_module
from typing import Any


def reexport_public_api(target_module: str, namespace: dict[str, Any]) -> list[str]:
    """Populate ``namespace`` with the public names exported by ``target_module``."""
    module = import_module(target_module)
    public_names = list(getattr(module, "__all__", ()))
    if not public_names:
        public_names = [name for name in module.__dict__ if not name.startswith("_")]
    for name in public_names:
        namespace[name] = getattr(module, name)
    return public_names
