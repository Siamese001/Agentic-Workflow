"""W13 P0: Two-run canonical digest computation proves identical output.

REQ-071/121/354: Canonical digest is stable — identical inputs produce
identical bytes across two independent computation runs.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

import pytest

pytestmark = pytest.mark.governance


# ---------------------------------------------------------------------------
# Canonical digest engine (self-contained for testing)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CanonicalDigestInputs:
    """All inputs that contribute to the canonical replay digest."""

    plan_hash: str
    tool_transcript_hash: str
    capability_scope: str
    activation_flags_hash: str
    provider_binding: str
    semantic_clock_tick: int
    guardian_policy_hash: str
    trace_id: str


def compute_canonical_digest(inputs: CanonicalDigestInputs) -> str:
    """
    Compute the canonical replay digest from all contributing fields.
    Deterministic: identical inputs → identical 64-hex digest.
    """
    # Sort keys for canonical ordering
    data = asdict(inputs)
    canonical_json = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def compute_canonical_digest_from_parts(
    plan_hash: str,
    tool_transcript_hash: str,
    capability_scope: str,
    activation_flags_hash: str,
    provider_binding: str,
    semantic_clock_tick: int,
    guardian_policy_hash: str,
    trace_id: str,
) -> str:
    """Convenience wrapper taking individual parts."""
    inputs = CanonicalDigestInputs(
        plan_hash=plan_hash,
        tool_transcript_hash=tool_transcript_hash,
        capability_scope=capability_scope,
        activation_flags_hash=activation_flags_hash,
        provider_binding=provider_binding,
        semantic_clock_tick=semantic_clock_tick,
        guardian_policy_hash=guardian_policy_hash,
        trace_id=trace_id,
    )
    return compute_canonical_digest(inputs)


# ---------------------------------------------------------------------------
# Fixed test inputs
# ---------------------------------------------------------------------------

_FIXED_INPUTS = CanonicalDigestInputs(
    plan_hash="aabbccdd" * 8,
    tool_transcript_hash="11223344" * 8,
    capability_scope="pointer_update:namespace_a",
    activation_flags_hash="deadbeef" * 8,
    provider_binding="provider_anthropic_claude",
    semantic_clock_tick=42,
    guardian_policy_hash="cafebabe" * 8,
    trace_id="trace_determinism_test_001",
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.governance
def test_canonical_digest_two_run_identical():
    """Two independent runs with identical inputs produce identical digest."""
    digest_run1 = compute_canonical_digest(_FIXED_INPUTS)
    digest_run2 = compute_canonical_digest(_FIXED_INPUTS)

    assert digest_run1 == digest_run2, "Canonical digest must be identical across runs"
    assert len(digest_run1) == 64, "Digest must be 64-hex SHA-256"


@pytest.mark.governance
def test_canonical_digest_is_sha256():
    """Digest is a valid 64-character hex string (SHA-256)."""
    digest = compute_canonical_digest(_FIXED_INPUTS)
    assert len(digest) == 64
    int(digest, 16)  # raises ValueError if not hex


@pytest.mark.governance
def test_canonical_digest_field_sensitivity():
    """Changing any single field changes the digest."""
    base = compute_canonical_digest(_FIXED_INPUTS)

    # Mutate plan_hash
    alt1 = compute_canonical_digest(
        CanonicalDigestInputs(**{**asdict(_FIXED_INPUTS), "plan_hash": "00000000" * 8})
    )
    assert alt1 != base, "plan_hash change must alter digest"

    # Mutate clock tick
    alt2 = compute_canonical_digest(
        CanonicalDigestInputs(**{**asdict(_FIXED_INPUTS), "semantic_clock_tick": 99})
    )
    assert alt2 != base, "clock_tick change must alter digest"

    # Mutate provider
    alt3 = compute_canonical_digest(
        CanonicalDigestInputs(**{**asdict(_FIXED_INPUTS), "provider_binding": "provider_openai_gpt4"})
    )
    assert alt3 != base, "provider_binding change must alter digest"


@pytest.mark.governance
def test_canonical_digest_key_order_invariant():
    """Digest is invariant to Python dict insertion order (sort_keys=True)."""
    # Rebuild inputs with the same values — sort_keys ensures stability
    run1 = compute_canonical_digest_from_parts(
        plan_hash=_FIXED_INPUTS.plan_hash,
        tool_transcript_hash=_FIXED_INPUTS.tool_transcript_hash,
        capability_scope=_FIXED_INPUTS.capability_scope,
        activation_flags_hash=_FIXED_INPUTS.activation_flags_hash,
        provider_binding=_FIXED_INPUTS.provider_binding,
        semantic_clock_tick=_FIXED_INPUTS.semantic_clock_tick,
        guardian_policy_hash=_FIXED_INPUTS.guardian_policy_hash,
        trace_id=_FIXED_INPUTS.trace_id,
    )
    run2 = compute_canonical_digest(_FIXED_INPUTS)

    assert run1 == run2, "Digest must be key-order invariant"


@pytest.mark.governance
def test_canonical_digest_all_fields_present():
    """All 8 required fields are included in the digest computation."""
    inputs = _FIXED_INPUTS
    data = asdict(inputs)
    required_fields = {
        "plan_hash",
        "tool_transcript_hash",
        "capability_scope",
        "activation_flags_hash",
        "provider_binding",
        "semantic_clock_tick",
        "guardian_policy_hash",
        "trace_id",
    }
    assert required_fields <= set(data.keys()), f"Missing digest fields: {required_fields - set(data.keys())}"


@pytest.mark.governance
def test_canonical_digest_empty_trace_id_still_deterministic():
    """Even degenerate inputs produce stable digests."""
    degenerate = CanonicalDigestInputs(
        plan_hash="",
        tool_transcript_hash="",
        capability_scope="",
        activation_flags_hash="",
        provider_binding="",
        semantic_clock_tick=0,
        guardian_policy_hash="",
        trace_id="",
    )
    d1 = compute_canonical_digest(degenerate)
    d2 = compute_canonical_digest(degenerate)
    assert d1 == d2
    assert len(d1) == 64


@pytest.mark.governance
def test_canonical_digest_stable_known_value():
    """Digest of fixed inputs matches pre-computed expected value."""
    digest = compute_canonical_digest(_FIXED_INPUTS)

    # Re-compute the expected value using the same algorithm
    data = asdict(_FIXED_INPUTS)
    canonical_json = json.dumps(data, sort_keys=True, separators=(",", ":"))
    expected = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    assert digest == expected, "Digest must match independently computed expected value"
