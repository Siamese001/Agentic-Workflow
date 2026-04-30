"""OTEL span receipt fixtures for the W4d-4 proof-evidence pilot.

A SpanReceipt is the deterministic in-test stand-in for a real OTEL span.
It records the span name and attribute set so a test can assert that:

  - the expected span_name was emitted
  - all required attributes are present
  - the attribute values bind the run (req_id, trace_id, ..., owner_surface)

When real OTEL helpers ship, the same tests can be re-pointed at the
runtime exporter; only the construction call changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

# Base attributes required on every emitted span per the ledger's
# otel_required_attributes column (W4d-2). The ledger always prefixes
# this set; per-owner extras are appended.
BASE_REQUIRED_ATTRS: tuple[str, ...] = (
    "req_id",
    "run_id",
    "trace_id",
    "request_id",
    "owner_surface",
    "policy_hash",
    "blueprint_hash",
    "replay_key",
)


@dataclass(frozen=True)
class SpanReceipt:
    """Deterministic record of a single emitted span."""

    span_name: str
    attributes: Mapping[str, Any] = field(default_factory=dict)


class SpanAssertionError(AssertionError):
    """Raised when an emitted span fails its required-shape contract."""


def make_receipt(span_name: str, attributes: Mapping[str, Any]) -> SpanReceipt:
    return SpanReceipt(span_name=span_name, attributes=dict(attributes))


def assert_span_shape(
    receipt: SpanReceipt,
    expected_name: str,
    required_attrs: tuple[str, ...] = BASE_REQUIRED_ATTRS,
) -> None:
    """Assert receipt has expected_name and every required attribute."""
    if receipt.span_name != expected_name:
        raise SpanAssertionError(
            f"span name mismatch: expected '{expected_name}', got '{receipt.span_name}'"
        )
    missing = [a for a in required_attrs if a not in receipt.attributes]
    if missing:
        raise SpanAssertionError(
            f"span '{expected_name}' missing required attributes: {missing}"
        )
    # All required attributes must be non-empty
    empty = [a for a in required_attrs if not str(receipt.attributes[a])]
    if empty:
        raise SpanAssertionError(
            f"span '{expected_name}' has empty required attributes: {empty}"
        )


def assert_owner_surface_matches(receipt: SpanReceipt, expected_owner: str) -> None:
    actual = receipt.attributes.get("owner_surface")
    if actual != expected_owner:
        raise SpanAssertionError(
            f"span owner_surface mismatch: expected '{expected_owner}', got '{actual}'"
        )
