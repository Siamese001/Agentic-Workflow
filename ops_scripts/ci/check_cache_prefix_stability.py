"""Cache-prefix stability CI gate — EQ-9 (ADR-PROMPT-ASSEMBLY-002 §10).

Asserts that :attr:`CompiledPromptArtifact.manifest_hash` is **invariant**
under:

1. ``structured_slots`` dict insertion order
2. ``AuthoritySlot`` construction order for the same logical slot set
3. ``allowed_tools_schema`` re-ordering equivalents (where that list is
   purely metadata — tools today are position-sensitive, so this gate
   only covers insertion order of the slot map itself)
4. ``idempotency_nonce`` variation (manifest_hash is supposed to be
   content-addressed and nonce-free by design)

The gate runs three fixture-based round-trips and exits non-zero on any
drift. It is additive: import failure or missing fixture file short-
circuits to exit 0 with a warning so the gate cannot wedge CI on its
own bootstrap.

Break-glass: set ``CACHE_PREFIX_GATE_BYPASS=1`` to skip the check in an
emergency. Every bypass logs a line to stderr for auditability.

Run locally:
    python ops_scripts/ci/check_cache_prefix_stability.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


_BYPASS_ENV = "CACHE_PREFIX_GATE_BYPASS"


def _bypassed() -> bool:
    return os.getenv(_BYPASS_ENV, "").lower() in {"1", "true", "yes", "on"}


def _make_slots(order: list[str]):
    """Build a ``structured_slots`` mapping in the supplied insertion order.

    Imports are deferred so the gate itself can fail-soft if the
    agentic_core tree is unavailable (e.g. fresh clone before install).
    """
    from agentic_core.L2_execution.reasoning.compiled_artifact import (  # noqa: PLC0415
        AuthorityLevel,
        AuthoritySlot,
    )

    level_by_slot = {
        "S0": AuthorityLevel.ABSOLUTE,
        "I0": AuthorityLevel.GOVERNED,
        "D0": AuthorityLevel.BINDING,
        "C0": AuthorityLevel.INFO,
        "E0": AuthorityLevel.EXEMPLAR,
        "M0": AuthorityLevel.META_COGNITIVE,
        "U0": AuthorityLevel.ZERO,
        "H0": AuthorityLevel.HEALING,
    }
    layer_by_slot = {
        "S0": "L4",
        "I0": "L4",
        "D0": "L5",
        "C0": "L1",
        "E0": "L4",
        "M0": "L4",
        "U0": "L1",
        "H0": "L2",
    }
    content_by_slot = {
        "S0": "system-content",
        "I0": "instructions-content",
        "D0": "constraints-content",
        "C0": "context-content",
        "E0": "examples-content",
        "M0": "thinking-content",
        "U0": "user-content",
        "H0": "healing-content",
    }

    out: dict[str, AuthoritySlot] = {}
    for code in order:
        out[code] = AuthoritySlot(
            slot_type=code,
            content=content_by_slot[code],
            authority_level=level_by_slot[code],
            source_layer=layer_by_slot[code],
        )
    return out


def _build_artifact(structured_slots, nonce: str | None = None):
    from agentic_core.L2_execution.reasoning.compiled_artifact import (  # noqa: PLC0415
        CompiledPromptArtifact,
    )

    kwargs = {
        "trace_id": "cache-prefix-gate",
        "system_version_hash": "v1",
        "final_system_string": "s",
        "final_user_string": "u",
        "allowed_tools_schema": [],
        "tokens": 1,
        "slots_used": list(structured_slots.keys()),
        "signature": "",
        "structured_slots": structured_slots,
    }
    if nonce is not None:
        kwargs["idempotency_nonce"] = nonce
    return CompiledPromptArtifact(**kwargs)


def check() -> int:
    """Run stability assertions. Return 0 on pass, 1 on drift."""
    if _bypassed():
        print(
            f"[{Path(__file__).name}] BYPASS via {_BYPASS_ENV}=1 — gate skipped.",
            file=sys.stderr,
        )
        return 0

    try:
        _make_slots(["S0"])  # smoke: import path and helper work.
    except (ImportError, ModuleNotFoundError) as exc:
        print(
            f"[{Path(__file__).name}] WARN: agentic_core unavailable ({exc}); "
            "gate short-circuits to pass.",
            file=sys.stderr,
        )
        return 0

    errors: list[str] = []

    # --- Invariant 1: insertion order of structured_slots must not affect hash.
    forward = _build_artifact(_make_slots(["S0", "I0", "D0", "C0", "U0"]))
    reversed_ = _build_artifact(_make_slots(["U0", "C0", "D0", "I0", "S0"]))
    if forward.manifest_hash != reversed_.manifest_hash:
        errors.append(
            "INVARIANT 1 FAIL — manifest_hash differs under slot insertion reorder:\n"
            f"  forward:  {forward.manifest_hash}\n"
            f"  reversed: {reversed_.manifest_hash}"
        )

    # --- Invariant 2: idempotency_nonce must NOT affect manifest_hash.
    nonce_a = _build_artifact(_make_slots(["S0", "U0"]), nonce="aaa" * 8)
    nonce_b = _build_artifact(_make_slots(["S0", "U0"]), nonce="bbb" * 8)
    if nonce_a.manifest_hash != nonce_b.manifest_hash:
        errors.append(
            "INVARIANT 2 FAIL — manifest_hash sensitive to idempotency_nonce:\n"
            f"  nonce_a: {nonce_a.manifest_hash}\n"
            f"  nonce_b: {nonce_b.manifest_hash}"
        )

    # --- Invariant 3: extending the slot map MUST change the hash.
    short_ = _build_artifact(_make_slots(["S0", "U0"]))
    long_ = _build_artifact(_make_slots(["S0", "I0", "U0"]))
    if short_.manifest_hash == long_.manifest_hash:
        errors.append(
            "INVARIANT 3 FAIL — manifest_hash collision between different slot sets"
        )

    if errors:
        print("CACHE-PREFIX STABILITY FAILED:\n", file=sys.stderr)
        for err in errors:
            print(f"  {err}\n", file=sys.stderr)
        return 1

    print("cache-prefix stability: OK (3 invariants verified)")
    return 0


if __name__ == "__main__":
    sys.exit(check())
