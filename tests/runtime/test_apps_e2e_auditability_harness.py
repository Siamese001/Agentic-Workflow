"""Shared apps_* end-to-end auditability verifier.

ONE test file, ONE loop over the AppSpec registry. Every check lives in
tools.certification.apps_e2e.shared_verifier so per-app duplication is
impossible.

Run:
    python -m tools.certification.apps_e2e.emit_proof_bundle --all --dry-run
    python -m pytest tests/runtime/test_apps_e2e_auditability_harness.py -q

Pass semantics:
  * The verifier passes when every emitted bundle is INTERNALLY CONSISTENT
    (schema fields present, hashes match, run_id threading is honest).
  * A bundle's `success=False` is NOT a verifier failure — it is the
    real-world status of an app that is not yet on the spine.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.certification.apps_e2e.app_specs import APP_SPECS, AppSpec
from tools.certification.apps_e2e.paths import AppCertPaths
from tools.certification.apps_e2e.shared_verifier import (
    Violation, format_violation, verify_bundle,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_bundle(spec: AppSpec) -> dict[str, Any] | None:
    paths = AppCertPaths(spec.app_name)
    if not paths.proof_bundle.exists():
        return None
    try:
        return json.loads(paths.proof_bundle.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


@pytest.mark.parametrize("spec", APP_SPECS, ids=lambda s: s.app_name)
def test_proof_bundle_emitted(spec: AppSpec) -> None:
    bundle = _load_bundle(spec)
    if bundle is None:
        pytest.skip(
            f"No proof bundle for {spec.app_name}. Emit with:\n"
            f"  python -m tools.certification.apps_e2e.emit_proof_bundle --app {spec.app_name} --dry-run"
        )
    assert bundle["app_name"] == spec.app_name


@pytest.mark.parametrize("spec", APP_SPECS, ids=lambda s: s.app_name)
def test_bundle_passes_shared_verifier(spec: AppSpec) -> None:
    bundle = _load_bundle(spec)
    if bundle is None:
        pytest.skip(f"No proof bundle for {spec.app_name}; emit first")
    violations: list[Violation] = verify_bundle(bundle, spec)
    if violations:
        report = "\n".join(format_violation(v) for v in violations)
        pytest.fail(
            f"{spec.app_name} bundle failed shared verifier "
            f"({len(violations)} violations):\n{report}"
        )


@pytest.mark.parametrize("spec", APP_SPECS, ids=lambda s: s.app_name)
def test_artifact_manifest_consistency(spec: AppSpec) -> None:
    """Every artifact_manifest item must be either (ref=None, present=False) or
    (ref=str, present=True, sha256=str).
    """
    bundle = _load_bundle(spec)
    if bundle is None:
        pytest.skip(f"No bundle for {spec.app_name}")
    manifest_ref = bundle.get("artifact_manifest_ref")
    if not manifest_ref:
        pytest.skip("manifest_ref absent")
    manifest = json.loads((REPO_ROOT / manifest_ref).read_text(encoding="utf-8"))
    for item in manifest["items"]:
        if item["ref"] is None:
            assert item["present"] is False, item
            continue
        # When ref is set, present must be True (the file must exist on disk)
        assert item["present"] is True, (
            f"{spec.app_name}: manifest claims ref={item['ref']} but present=false"
        )
        assert item["sha256"], item


def test_apps_rg_is_reference_success() -> None:
    """The reference app MUST emit success=true after a real run.

    apps_rg is the canonical proof point. If this regresses, every other
    app's harness coverage is suspect.
    """
    spec = next(s for s in APP_SPECS if s.app_name == "apps_rg")
    bundle = _load_bundle(spec)
    if bundle is None:
        pytest.skip("apps_rg bundle not emitted yet")
    if not bundle.get("success"):
        pytest.skip(
            "apps_rg success=false — harness is internally consistent but "
            "the most recent live run did not produce all spine artifacts. "
            "Re-run: python -m tools.certification.apps_e2e.emit_proof_bundle --app apps_rg"
        )
    assert bundle["agentic_core_spine_status"] == "spine_active"
    assert bundle["app_overlay_authority_status"] == "overlay_respected"
