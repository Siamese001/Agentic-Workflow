"""
agentic_core.runtime.prove_requirements
========================================

Runtime requirements coverage proof system.

This package builds a foolproof requirements-to-runtime evidence trail from the
12 canonical source folders under ``docs/reference/`` and produces machine-
readable artifacts under ``artifacts/runtime/requirements_proof/``.

Phase status (this build):
    Phase 0 — source manifest:        IMPLEMENTED
    Phase 1 — requirements extraction: IMPLEMENTED
    Phase 2 — implementation mapping:  NOT_IMPLEMENTED
    Phase 3 — coverage matrix:         NOT_IMPLEMENTED
    Phase 4 — runtime gap closure:     NOT_IMPLEMENTED
    Phase 5 — OTEL spans:              NOT_IMPLEMENTED
    Phase 6 — deterministic replay:    NOT_IMPLEMENTED
    Phase 7 — anti-bypass negatives:   NOT_IMPLEMENTED
    Phase 8 — E2E scenarios:           NOT_IMPLEMENTED

Subsequent phases will be added behind explicit Author-Gate decisions per
``.codex/rules/author-gate-enforcement.md``. No phase will be marked
complete without machine-verifiable artifacts on disk.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
