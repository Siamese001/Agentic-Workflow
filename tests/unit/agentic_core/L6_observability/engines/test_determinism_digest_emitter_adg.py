"""ADG importability contract for agentic_core/L6_observability/engines/determinism_digest_emitter.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L6_observability.engines.determinism_digest_emitter  # noqa: F401


def test_module_importable():
    import agentic_core.L6_observability.engines.determinism_digest_emitter  # noqa: F401
    """Module determinism_digest_emitter must be importable."""
    assert agentic_core.L6_observability.engines.determinism_digest_emitter is not None
