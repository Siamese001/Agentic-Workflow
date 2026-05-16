"""Exit compatibility policy hooks on binding manifests."""

from __future__ import annotations

from pathlib import Path

from agentic_core.runtime.bindings.exit_binding_validator import validate_manifest_exit_compatibility_policy


def test_manifest_with_absence_reason_and_no_exit_bundle_ok() -> None:
    manifest = {
        "exit_compatibility_absence_reason": "fixture scope only",
        "sections": {},
    }
    assert validate_manifest_exit_compatibility_policy(manifest, {}) == []


def test_missing_reason_when_no_exit_bundle_fails() -> None:
    manifest = {"sections": {}}
    errs = validate_manifest_exit_compatibility_policy(manifest, {})
    assert errs
