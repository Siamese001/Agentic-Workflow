"""L5 certification reference verification helper.

Standalone module per AG-W0-4 decision (2026-05-09): single-responsibility —
``registry.py`` remains a pure symbol-table lookup; this module owns validation.

Policy (AG-W0-2=plain_str, AG-W0-5=fail_closed):
- Empty string is invalid — emit-side ``__post_init__`` raises ``ValueError``.
- Non-empty strings are structurally accepted; semantic validity (expiry, scope,
  HMAC) is deferred to a future hardening wave.

Import path: ``from agentic_core.L5_safety.contracts.verify import verify_certification_ref``

This module intentionally has no imports from ``agentic_core.runtime.*`` so it
can be safely imported by runtime contract dataclasses without creating a
circular dependency (L5 → runtime would invert the layer-gravity direction).
"""

from __future__ import annotations


def verify_certification_ref(ref: str) -> bool:
    """Return True iff *ref* is structurally valid as an L5 certification ref.

    A non-empty ``str`` is accepted as structurally valid.  Semantic checks
    (cert expiry, scope, HMAC signature) are intentionally deferred — they
    require I/O and belong in a runtime gate, not a dataclass constructor.

    Args:
        ref: The certification reference string to validate.

    Returns:
        ``True`` if *ref* is a non-empty string, ``False`` otherwise.
    """
    return isinstance(ref, str) and bool(ref.strip())


__all__ = ["verify_certification_ref"]
