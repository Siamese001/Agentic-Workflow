"""W1 phase 4 — anti-cheat invariants (no SSOT mutation, no forced green)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SSOT = REPO_ROOT / "agentic_core" / "L4_state" / "utils" / "memory" / "semantic_cache_manager.py"


class TestSemanticCacheManagerUnchanged:
    """SSOT threshold MUST remain at 0.95 dynamic / 1.0 static."""

    @pytest.fixture(scope="class")
    def source(self) -> str:
        return SSOT.read_text(encoding="utf-8")

    def test_dynamic_default_unchanged(self, source):
        # Canonical form at line 159:
        # _TIER_THRESHOLD_DEFAULTS: dict[str, float] = {"static": 1.0, "dynamic": 0.95}
        assert '"dynamic": 0.95' in source, (
            "W1p4 MUST NOT mutate _TIER_THRESHOLD_DEFAULTS.dynamic from 0.95"
        )
        assert "_TIER_THRESHOLD_DEFAULTS" in source

    def test_static_default_unchanged(self, source):
        assert '"static": 1.0' in source, (
            "W1p4 MUST NOT mutate _TIER_THRESHOLD_DEFAULTS.static from 1.0"
        )


class TestADRProposedNotApplied:
    def test_adr_never_applied_by_generator(self):
        """Running the generator must ALWAYS land at applied=False."""
        adr_path = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_threshold_adr.json"
        result = subprocess.run(
            [sys.executable, "ops_scripts/ci/generate_threshold_adr.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        adr = json.loads(adr_path.read_text(encoding="utf-8"))
        assert adr["config_binding"]["applied"] is False
        assert adr["implementation_status"] == "PROPOSED_NOT_APPLIED"
        assert adr["owner_approval"]["status"] == "PENDING_APPROVAL"


class TestRTCReq055StaysPartial:
    """End-to-end invariant: with ADR PENDING, RTC-REQ-055 must stay PARTIAL."""

    def test_overrides_show_rtc_055_partial(self):
        overrides_path = REPO_ROOT / "artifacts" / "certification" / "runtime_evidence_overrides.json"
        if not overrides_path.exists():
            pytest.skip("overrides not present — run the composer + verifier first")
        o = json.loads(overrides_path.read_text(encoding="utf-8"))
        status = o.get("final_acceptance_status", {}).get("RTC-REQ-055")
        assert status in ("PARTIAL", "BLOCKED"), (
            f"W1p4 invariant violated: RTC-REQ-055 = {status} "
            f"(expected PARTIAL or BLOCKED while ADR PENDING)"
        )

    def test_sidecar_threshold_not_pass_without_approved_adr(self):
        sidecar_path = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_subclaims.json"
        adr_path = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_threshold_adr.json"
        if not (sidecar_path.exists() and adr_path.exists()):
            pytest.skip("sidecar or ADR not present")
        sc = json.loads(sidecar_path.read_text(encoding="utf-8"))
        adr = json.loads(adr_path.read_text(encoding="utf-8"))
        threshold_status = sc["subclaims"]["R1B_PRODUCTION_THRESHOLD_PROOF"]["status"]
        approval = adr["owner_approval"]["status"]
        applied = adr["config_binding"]["applied"]
        if approval != "APPROVED" or not applied:
            assert threshold_status != "PASS", (
                f"ADR gate violated: threshold={threshold_status} but "
                f"ADR approval={approval}, applied={applied}"
            )


class TestNoOverrideShipped:
    """No W1p4 code path sets any threshold override env var."""

    @pytest.fixture(scope="class")
    def w1p4_files(self) -> list[Path]:
        return [
            REPO_ROOT / "tools" / "certification" / "evidence" / "probe_threshold_sweep.py",
            REPO_ROOT / "scripts" / "generate_threshold_adr.py",
            REPO_ROOT / "tools" / "certification" / "evidence" / "probe_semantic_cache_model.py",
            REPO_ROOT / "tools" / "certification" / "evidence" / "probe_semantic_cache_threshold.py",
            REPO_ROOT / "scripts" / "compose_semantic_cache_subclaims.py",
        ]

    def test_no_env_mutation_of_threshold_overrides(self, w1p4_files):
        pattern = re.compile(
            r'os\.environ\s*\[\s*["\']SEMANTIC_CACHE_THRESHOLD',
            re.IGNORECASE,
        )
        for f in w1p4_files:
            if not f.exists():
                continue
            src = f.read_text(encoding="utf-8")
            # Allow `os.environ.get(...)` reads (they don't mutate); only forbid item-assignment
            matches = pattern.findall(src)
            # os.environ["KEY"] = ... is assignment; os.environ["KEY"] on its own is a read. But
            # the regex above is safe because it matches the indexing expression, which in a read
            # context is harmless. We detect ASSIGNMENT by checking for `=` after the bracket.
            assign_pattern = re.compile(
                r'os\.environ\s*\[\s*["\']SEMANTIC_CACHE_THRESHOLD[^"\']*["\']\s*\]\s*=',
                re.IGNORECASE,
            )
            assigns = assign_pattern.findall(src)
            assert not assigns, (
                f"{f.name} contains threshold env assignment: {assigns}"
            )


class TestNoSSOTYamlMutation:
    """No W1p4 artifact or code writes to config/YAML defaults."""

    def test_no_config_yaml_under_config_cert(self):
        # Defense-in-depth: the cert pipeline produces JSON under
        # artifacts/certification/ and docs/adr/, never a config/yaml write.
        cert_dir = REPO_ROOT / "artifacts" / "certification"
        assert cert_dir.exists()
        # No yaml files authored by W1p4
        yaml_files = list(cert_dir.glob("*.yaml")) + list(cert_dir.glob("*.yml"))
        assert not yaml_files, f"Unexpected YAML artifacts in cert dir: {yaml_files}"


class TestW1P4ProbeNeverCreatesADR:
    """Anti-cheat: sweep probe MUST NOT create the ADR."""

    def test_sweep_probe_anti_cheat_block(self):
        art = REPO_ROOT / "artifacts" / "certification" / "threshold_sweep_results.json"
        if not art.exists():
            pytest.skip("sweep not run locally")
        d = json.loads(art.read_text(encoding="utf-8"))
        assert d["anti_cheat_rules_honored"]["probe_did_not_create_adr"] is True


class TestW1P4NoForceGreen:
    """RTC-REQ-055 final_acceptance must not be ACCEPTED while ADR pending."""

    def test_if_adr_pending_then_row_not_accepted(self):
        adr_path = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_threshold_adr.json"
        overrides_path = REPO_ROOT / "artifacts" / "certification" / "runtime_evidence_overrides.json"
        if not (adr_path.exists() and overrides_path.exists()):
            pytest.skip("artifacts missing")
        adr = json.loads(adr_path.read_text(encoding="utf-8"))
        overrides = json.loads(overrides_path.read_text(encoding="utf-8"))
        if adr["owner_approval"]["status"] != "APPROVED":
            row_status = overrides.get("final_acceptance_status", {}).get("RTC-REQ-055")
            assert row_status != "ACCEPTED", (
                f"forced green detected: ADR pending but RTC-REQ-055 = {row_status}"
            )
