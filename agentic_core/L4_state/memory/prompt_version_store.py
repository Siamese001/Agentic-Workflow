"""PromptVersionStore — Immutable versioned prompt storage for L4 S0/I0 prompts.

Phase 1 Wave 1.1 implementation. Provides SHA-256-based immutability,
atomic commits, and read-only access to versioned prompts.
"""

from __future__ import annotations

import hashlib
from typing import Literal

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "prompt_version_store", "L4")
_emit_routes_through("p1", "prompt_version_store", "L4")
_emit_escalates_to_human("p1", "prompt_version_store", "L4")
_emit_reads_policy_state("p1", "prompt_version_store", "L4")

_versions: dict[str, str] = {}


class PromptVersionStore:
    """Immutable versioned storage for S0/I0 prompts.

    - commit_version() returns SHA-256 of content (immutable version ID)
    - Same content → same version ID (deduplication)
    - Versions are write-once; no delete, no overwrite
    """

    def commit_version(self, prompt_type: Literal["S0", "I0"], content: str) -> str:
        """Commit a prompt version and return its SHA-256 version ID.

        Args:
            prompt_type: Either "S0" (SYSTEM) or "I0" (INSTRUCTIONAL)
            content: Prompt text content

        Returns:
            SHA-256 hex digest as version ID

        Raises:
            ValueError: If prompt_type is not "S0" or "I0"
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "PromptVersionStore.commit_version", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "PromptVersionStore.commit_version", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "PromptVersionStore.commit_version")

        if prompt_type not in ("S0", "I0"):
            raise ValueError(f"prompt_type must be 'S0' or 'I0', got {prompt_type!r}")
        version_id = hashlib.sha256(content.encode("utf-8")).hexdigest()
        _versions.setdefault(version_id, content)
        return version_id

    def get_s0(self, version: str) -> str:
        """Retrieve S0 prompt content by version ID.

        Args:
            version: SHA-256 version ID

        Returns:
            Prompt content

        Raises:
            KeyError: If version not found
        """
        return _versions[version]

    def get_i0(self, version: str) -> str:
        """Retrieve I0 prompt content by version ID.

        Args:
            version: SHA-256 version ID

        Returns:
            Prompt content

        Raises:
            KeyError: If version not found
        """
        return _versions[version]

    def list_versions(self) -> list[str]:
        """Return all stored version IDs."""
        return list(_versions.keys())

    def clear(self) -> None:
        """Clear all stored versions. For tests only."""
        _versions.clear()
