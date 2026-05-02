"""Waiver parsing and validity for the apps_e2e two-gate certification harness.

Plan: apps-e2e-two-gate-certification-d8b3a1 §4.4

A waiver is valid iff:
  - waiver_reason, waiver_owner, waiver_expiry are ALL set (non-empty), AND
  - waiver_expiry parses as ISO-8601 UTC, AND
  - waiver_expiry is strictly in the future at validation time.

Waivers are required when:
  - spec.runnable=False (skeleton apps), OR
  - spec.certification_required=False (non-runtime apps).

The verifier emits the matching violation when a waiver is required but
incomplete (`waiver_incomplete`) or expired (`waiver_expired`).

This module is the SSOT for waiver semantics. compute_level() in
certification_levels.py imports `is_waiver_valid` from here. The W1.2
inline helper is now a thin pass-through to preserve the test surface.
"""
from __future__ import annotations

from datetime import datetime, timezone

from tools.certification.apps_e2e.app_specs import AppSpec, has_waiver


def parse_iso_utc(value: str | None) -> datetime | None:
    """Parse an ISO-8601 UTC timestamp. Returns None on any failure.

    Accepts the canonical ``...Z`` suffix as well as ``...+00:00``. Naive
    datetimes (no timezone) are REJECTED.
    """
    if not value or not isinstance(value, str):
        return None
    try:
        normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt.astimezone(timezone.utc)


def waiver_required(spec: AppSpec) -> bool:
    """True iff this spec MUST carry a waiver to be considered valid."""
    return (not spec.runnable) or (not spec.certification_required)


def is_waiver_valid(spec: AppSpec, now: datetime | None = None) -> bool:
    """True iff the waiver triple is set AND parses AND is in the future.

    Returns False on:
      - Missing reason / owner / expiry (any of the three).
      - Unparseable expiry.
      - Naive (no tzinfo) expiry.
      - Expiry equal to or before ``now``.

    ``now`` defaults to ``datetime.now(timezone.utc)``. Pass an explicit
    ``now`` for deterministic tests.
    """
    if not has_waiver(spec):
        return False
    expiry = parse_iso_utc(spec.waiver_expiry)
    if expiry is None:
        return False
    if now is None:
        now = datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return expiry > now


def waiver_violation_rule_id(spec: AppSpec, now: datetime | None = None) -> str | None:
    """Return the matching rule_id when a required waiver is invalid.

    Returns None when the waiver is valid OR when no waiver is required.
    Useful for verifier error reporting.
    """
    if not waiver_required(spec):
        return None
    if not has_waiver(spec):
        return "waiver_incomplete"
    expiry = parse_iso_utc(spec.waiver_expiry)
    if expiry is None:
        return "waiver_expiry_unparseable"
    if now is None:
        now = datetime.now(timezone.utc)
    if expiry <= now:
        return "waiver_expired"
    return None


__all__ = [
    "parse_iso_utc",
    "waiver_required",
    "is_waiver_valid",
    "waiver_violation_rule_id",
]
