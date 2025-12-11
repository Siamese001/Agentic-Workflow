"""
03_runtime/compat/__init__.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: 8d1887fd12429731946c270f0cdc37c7cdc8262da83a9012706709291d92798a
"""


from __future__ import annotations

# Re-export everything from shared modules for compatibility
from ..shared.exceptions import *  # Implementation pending# noqa: F401, F403
from shared.models import *  # Import from shared/models instead of runtime.shared.models# noqa: F401, F403
from shared.config import *  # Import from shared/config instead of runtime.shared.config# noqa: F401, F403
from runtime.shared.utils import *
