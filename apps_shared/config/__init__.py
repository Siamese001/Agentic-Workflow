"""Shared configuration package for apps_shared.

Keep the package import side-effect free. Callers should import concrete config
modules directly to avoid pulling optional dependencies during package import.
"""

from __future__ import annotations

__all__: list[str] = []
