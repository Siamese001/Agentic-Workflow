"""Canonical hash re-export for L0-L6 consumption.

L0-L6 layers must not import tools.vllm_boundary_client directly
(enforced by governance tests). This module provides a narrow
re-export of the canonical_hash function only, without exposing
model-related functionality.
"""

from __future__ import annotations

from tools.vllm_boundary_client import canonical_hash

__all__ = ["canonical_hash"]
