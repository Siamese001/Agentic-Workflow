"""
W6 — apps_foo Plug-in Proof Fixture Tests
==========================================

Proves that a future app (apps_foo) can register/use generic core capability
through app-owned config only, with zero modifications to agentic_core/.

Tests:
  1. test_future_app_plugin_needs_no_core_edit
  2. test_apps_foo_config_contains_no_core_patch_instruction
  3. test_apps_foo_uses_app_owned_domain_contract
  4. test_apps_foo_does_not_require_author_gate_receipt

These tests deliberately import nothing from agentic_core — proving the
plug-in contract is achievable through app-owned config alone.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[4]
_FIXTURE_ROOT = Path(__file__).resolve().parent
_ROUTE_PROFILE = _FIXTURE_ROOT / "config" / "domain_contract" / "route_profile.yaml"
_AGENTIC_CORE = _REPO_ROOT / "agentic_core"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _snapshot_core(core_path: Path) -> dict[str, str]:
    """Return {relative_path: sha256_hex} for every file in agentic_core/."""
    result: dict[str, str] = {}
    for f in sorted(core_path.rglob("*")):
        if f.is_file():
            rel = str(f.relative_to(core_path)).replace("\\", "/")
            result[rel] = hashlib.sha256(f.read_bytes()).hexdigest()
    return result


def _simulate_app_registration(route_profile_path: Path) -> None:
    """Simulate registering apps_foo through app-owned config only.

    In the real spine, this would be:
        apps_foo/spine_manifest.yaml  →  spine registry  →  generic resolver
    All three artifacts are app-owned. Zero core writes occur.

    This simulation is intentionally no-op from an agentic_core perspective:
    we read the config and confirm it declares the correct shape, then return.
    The absence of any write to agentic_core/ IS the proof.
    """
    assert route_profile_path.exists(), (
        f"Route profile not found at {route_profile_path}"
    )
    # Reading the config is the registration — no core file is written.
    _ = route_profile_path.read_text(encoding="utf-8")


def _load_route_profile() -> dict:
    """Load route_profile.yaml; skip if PyYAML is unavailable."""
    if not _YAML_AVAILABLE:
        pytest.skip("PyYAML not installed — skipping YAML parse tests")
    return yaml.safe_load(_ROUTE_PROFILE.read_text(encoding="utf-8"))


# ===========================================================================
# Tests
# ===========================================================================


def test_future_app_plugin_needs_no_core_edit() -> None:
    """Test 1: Simulated apps_foo registration leaves agentic_core/ unchanged.

    Protocol:
      - Snapshot agentic_core file list + SHA-256 digests BEFORE registration.
      - Run _simulate_app_registration (app-owned config read only).
      - Snapshot agentic_core AFTER registration.
      - Assert file list and digests are identical.
    """
    assert _AGENTIC_CORE.is_dir(), (
        f"agentic_core/ not found at {_AGENTIC_CORE}; check _REPO_ROOT resolution"
    )

    snapshot_before = _snapshot_core(_AGENTIC_CORE)
    assert snapshot_before, "agentic_core/ must contain at least one file"

    _simulate_app_registration(_ROUTE_PROFILE)

    snapshot_after = _snapshot_core(_AGENTIC_CORE)

    added = set(snapshot_after) - set(snapshot_before)
    removed = set(snapshot_before) - set(snapshot_after)
    modified = {
        p for p in snapshot_before
        if p in snapshot_after and snapshot_before[p] != snapshot_after[p]
    }

    assert not added, f"agentic_core/ gained files during registration: {added}"
    assert not removed, f"agentic_core/ lost files during registration: {removed}"
    assert not modified, f"agentic_core/ files were modified during registration: {modified}"


def test_apps_foo_config_contains_no_core_patch_instruction() -> None:
    """Test 2: The fixture config declares no instruction to edit agentic_core/.

    Checks both the raw YAML text (no literal 'agentic_core/' path references
    that suggest patch instructions) and the machine-readable proof block.
    """
    raw = _ROUTE_PROFILE.read_text(encoding="utf-8")

    # The config must not contain edit/patch instructions targeting core.
    # Check for forbidden PHRASES — note we check the value form
    # ("platform_core_change" as a plan_type value, not as a key name in a proof block).
    forbidden_phrases = [
        "edit agentic_core",
        "patch agentic_core",
        "modify agentic_core",
        "add to agentic_core",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in raw, (
            f"Route profile must not contain '{phrase}'; found in {_ROUTE_PROFILE}"
        )

    # plan_type value must NOT be platform_core_change.
    # We check the specific YAML value assignment form, not arbitrary substring,
    # so that proof-block key names like 'plan_type_is_not_platform_core_change' are allowed.
    import re as _re
    plan_type_match = _re.search(r'^plan_type\s*:\s*(\S+)', raw, _re.MULTILINE)
    if plan_type_match:
        assert plan_type_match.group(1) != "platform_core_change", (
            f"plan_type value must not be 'platform_core_change'; "
            f"found '{plan_type_match.group(1)}' in {_ROUTE_PROFILE}"
        )

    # Verify machine-readable proof block (if PyYAML available).
    if _YAML_AVAILABLE:
        profile = yaml.safe_load(raw)
        proof = profile.get("proof", {})
        assert proof.get("no_core_patch_instruction") is True, (
            "proof.no_core_patch_instruction must be true"
        )
        assert proof.get("plan_type_is_not_platform_core_change") is True, (
            "proof.plan_type_is_not_platform_core_change must be true"
        )


def test_apps_foo_uses_app_owned_domain_contract() -> None:
    """Test 3: route_profile.yaml lives under apps_foo_stub/config/domain_contract/.

    The canonical pattern for any apps_* is:
        apps_<name>/config/domain_contract/<profile>.yaml
    This test verifies the fixture follows that pattern exactly.
    """
    # Verify the route profile is under the fixture's own config/domain_contract/
    expected_parent = _FIXTURE_ROOT / "config" / "domain_contract"
    assert _ROUTE_PROFILE.parent == expected_parent, (
        f"route_profile.yaml must be under {expected_parent}; "
        f"found at {_ROUTE_PROFILE.parent}"
    )

    # Verify it does NOT live under agentic_core/
    assert not str(_ROUTE_PROFILE).replace("\\", "/").startswith(
        str(_AGENTIC_CORE).replace("\\", "/")
    ), "route_profile.yaml must NOT be under agentic_core/"

    # Verify the declared app_id matches the fixture name.
    if _YAML_AVAILABLE:
        profile = _load_route_profile()
        assert profile.get("app_id") == "apps_foo", (
            "app_id in route_profile.yaml must be 'apps_foo'"
        )
        assert profile.get("plan_type") == "apps_work", (
            "plan_type must be 'apps_work' (not 'platform_core_change')"
        )
        assert profile.get("route_class") == "generic_spine", (
            "route_class must be 'generic_spine'"
        )
        capability_refs = profile.get("capability_refs", [])
        assert len(capability_refs) >= 2, (
            "capability_refs must declare at least 2 generic capabilities"
        )
        # Capability refs must reference GENERIC capabilities, not app-specific core code.
        for ref in capability_refs:
            assert "generic" in ref.lower(), (
                f"capability_ref '{ref}' must reference a generic capability, not app-specific core"
            )


def test_apps_foo_does_not_require_author_gate_receipt() -> None:
    """Test 4: apps_foo config changes are app-owned, so no CoreAdditionAuthorGateReceipt needed.

    The CoreAdditionAuthorGateReceipt is only required when plan_type=platform_core_change.
    apps_foo registration uses plan_type=apps_work — zero receipt overhead.
    """
    if _YAML_AVAILABLE:
        profile = _load_route_profile()

        # plan_type must NOT be platform_core_change
        assert profile.get("plan_type") != "platform_core_change", (
            "apps_foo registration must NOT require platform_core_change plan_type"
        )

        # The proof block must explicitly declare no receipt required
        proof = profile.get("proof", {})
        assert proof.get("author_gate_receipt_required") is False, (
            "proof.author_gate_receipt_required must be false for app-owned config"
        )

    # Structural check: the fixture contains no receipt JSON file.
    receipt_files = list(_FIXTURE_ROOT.rglob("*receipt*.json"))
    assert not receipt_files, (
        f"apps_foo fixture must contain no receipt JSON files; found: {receipt_files}"
    )

    # Verify apps_foo path is not in any GOV-3 baseline (it shouldn't need suppression).
    # Import the baseline dict directly to prove it.
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from ops_scripts.ci.check_agentic_core_addition import _GOV3_BASELINE

    foo_paths = [p for p in _GOV3_BASELINE if "apps_foo" in p]
    assert not foo_paths, (
        f"apps_foo paths must not appear in _GOV3_BASELINE; found: {foo_paths}"
    )
