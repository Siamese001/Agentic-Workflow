"""Negative controls for binding manifest Exit compatibility policy."""

from __future__ import annotations

from agentic_core.runtime.bindings.exit_binding_validator import validate_manifest_exit_compatibility_policy


def test_manifest_without_exit_bundle_or_reason_fails() -> None:
    manifest = {"sections": {}}
    errs = validate_manifest_exit_compatibility_policy(manifest, {})
    assert errs


def test_manifest_with_sections_only_and_reason_passes() -> None:
    manifest = {"sections": {}, "exit_compatibility_absence_reason": "negative control"}
    assert validate_manifest_exit_compatibility_policy(manifest, {}) == []
