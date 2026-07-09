"""Unit tests for the manifest schema + runner mechanics."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Allow importing the runner module by file path.
import importlib.util

RUNNER_PATH = REPO_ROOT / "ops_scripts" / "ci" / "run_adg_three_graph_tests.py"
spec = importlib.util.spec_from_file_location("_adg_runner", RUNNER_PATH)
assert spec is not None and spec.loader is not None
_runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_runner)

from agentic_core.adg.ci.gate_result import VALID_BUCKETS, VALID_STATUSES, GateResult

MANIFEST_PATH = REPO_ROOT / "ops_scripts" / "ci" / "adg_gate_manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    return _runner.load_manifest()


class TestManifestShape:
    def test_manifest_loads(self, manifest):
        assert manifest["schema"] == "adg_gate_manifest_v1"
        assert isinstance(manifest["gates"], list)
        assert len(manifest["gates"]) >= 10

    def test_every_gate_has_required_fields(self, manifest):
        for gate in manifest["gates"]:
            assert gate.get("gate_id"), gate
            assert gate["bucket"] in VALID_BUCKETS, gate
            assert gate.get("evidence_mode") in {"proof", "risk", "inventory"}, gate
            assert gate.get("enforcement_mode") in {
                "strict", "advisory", "ratchet", "audit",
            }, gate
            # Either script or view_rule must be present.
            assert ("script" in gate) ^ ("view_rule" in gate), gate

    def test_gate_ids_unique(self, manifest):
        ids = [g["gate_id"] for g in manifest["gates"]]
        assert len(ids) == len(set(ids))

    def test_view_rule_gates_well_formed(self, manifest):
        for gate in manifest["gates"]:
            rule = gate.get("view_rule")
            if rule is None:
                continue
            assert rule.get("kind") == "scalar", gate["gate_id"]
            assert rule.get("sql"), gate["gate_id"]
            # At least one expectation.
            expectations = {
                "expect", "expect_min", "expect_max", "expect_regex", "expect_in",
            }
            assert expectations & set(rule.keys()), gate["gate_id"]

    def test_legacy_gates_marked_with_accepts_runner_flags_false(self, manifest):
        # Every gate flagged ``legacy: true`` should declare it does not
        # accept runner-injected flags (else the runner will pass flags
        # the gate's argparse rejects).
        for gate in manifest["gates"]:
            if gate.get("legacy"):
                assert gate.get("accepts_runner_flags") is False, gate["gate_id"]


class TestSuiteFiltering:
    def test_quick_suite_includes_each_bucket(self, manifest):
        quick = _runner.filter_gates(manifest, suite="quick", bucket_filter=None)
        buckets = {g["bucket"] for g in quick}
        # Quick must cover at least preflight + each of the three graphs.
        assert "preflight" in buckets
        assert "static" in buckets
        assert "registry" in buckets
        assert "runtime" in buckets
        assert "cross_bucket" in buckets

    def test_bucket_filter(self, manifest):
        only_registry = _runner.filter_gates(
            manifest, suite="full", bucket_filter="registry"
        )
        assert all(g["bucket"] == "registry" for g in only_registry)
        assert len(only_registry) >= 1

    def test_full_suite_includes_quick(self, manifest):
        quick_ids = {
            g["gate_id"]
            for g in _runner.filter_gates(manifest, suite="quick", bucket_filter=None)
        }
        full_ids = {
            g["gate_id"]
            for g in _runner.filter_gates(manifest, suite="full", bucket_filter=None)
        }
        # Every quick gate is also in full.
        assert quick_ids <= full_ids


class TestBypassDetection:
    def test_no_bypass_env_set(self, manifest, monkeypatch):
        for var in ("REGISTRY_INTEGRITY_BYPASS", "FOO_BYPASS"):
            monkeypatch.delenv(var, raising=False)
        gate = next(g for g in manifest["gates"] if g["gate_id"] == "registry.graph_integrity")
        assert _runner._detect_bypass(gate) == []

    def test_bypass_env_detected(self, manifest, monkeypatch):
        gate = next(g for g in manifest["gates"] if g["gate_id"] == "registry.graph_integrity")
        monkeypatch.setenv("REGISTRY_INTEGRITY_BYPASS", "1")
        assert "REGISTRY_INTEGRITY_BYPASS" in _runner._detect_bypass(gate)


class TestStrictBypassOverride:
    def test_strict_bypass_overrides_pass_to_fail(self):
        gate = {"gate_id": "x.y", "bucket": "static", "bypass_env": "FOO_BYPASS"}
        result = GateResult(
            gate_id="x.y",
            bucket="static",
            status="PASS",
            bypass_env_detected=["FOO_BYPASS"],
        ).finalize()
        overridden = _runner.apply_strict_bypass_override(result, gate)
        assert overridden.status == "FAIL"
        assert overridden.actual_fail_reason.startswith("STRICT_BYPASS_DETECTED:")

    def test_strict_bypass_skipped_when_allowed_to_skip(self):
        gate = {
            "gate_id": "x.y", "bucket": "static",
            "bypass_env": "FOO_BYPASS", "allowed_to_skip": True,
        }
        result = GateResult(
            gate_id="x.y",
            bucket="static",
            status="PASS",
            bypass_env_detected=["FOO_BYPASS"],
        ).finalize()
        overridden = _runner.apply_strict_bypass_override(result, gate)
        assert overridden.status == "PASS"

    def test_strict_bypass_no_op_when_no_bypass(self):
        gate = {"gate_id": "x.y", "bucket": "static"}
        result = GateResult(gate_id="x.y", bucket="static", status="PASS").finalize()
        overridden = _runner.apply_strict_bypass_override(result, gate)
        assert overridden.status == "PASS"


class TestRollup:
    def test_overall_pass(self):
        results = [
            GateResult(gate_id="a", bucket="static", status="PASS").finalize(),
            GateResult(gate_id="b", bucket="static", status="PASS").finalize(),
        ]
        from datetime import datetime, timezone
        rollup = _runner.build_rollup(
            "quick", None, datetime.now(timezone.utc), results, strict=False
        )
        assert rollup.overall_status == "PASS"

    def test_overall_fail_when_any_fail(self):
        results = [
            GateResult(gate_id="a", bucket="static", status="PASS").finalize(),
            GateResult(
                gate_id="b", bucket="static", status="FAIL",
                actual_fail_reason="x",
            ).finalize(),
        ]
        from datetime import datetime, timezone
        rollup = _runner.build_rollup(
            "quick", None, datetime.now(timezone.utc), results, strict=False
        )
        assert rollup.overall_status == "FAIL"

    def test_strict_does_not_promote_warn_to_fail(self):
        """WARN is a gate's intentional advisory state. --strict should
        fail-close on real invariant violations (FAIL) and infrastructure
        problems (ERROR), but should NOT promote WARNs that the gate
        deliberately emitted as non-failure advisory signals.

        Conflating WARN→FAIL at the rollup level loses the gate-author's
        intent: the gate already chose WARN because the condition is not
        a real defect (e.g., aspirational schema fields, topology data
        unavailable). Per-gate code is responsible for choosing FAIL vs
        WARN; the rollup merely aggregates.
        """
        results = [
            GateResult(gate_id="a", bucket="static", status="WARN").finalize(),
        ]
        from datetime import datetime, timezone
        rollup = _runner.build_rollup(
            "quick", None, datetime.now(timezone.utc), results, strict=True
        )
        assert rollup.overall_status == "WARN"

    def test_warn_left_alone_in_non_strict(self):
        results = [
            GateResult(gate_id="a", bucket="static", status="WARN").finalize(),
        ]
        from datetime import datetime, timezone
        rollup = _runner.build_rollup(
            "quick", None, datetime.now(timezone.utc), results, strict=False
        )
        assert rollup.overall_status == "WARN"

    def test_strict_still_fails_on_real_fail(self):
        """Sanity check: strict still raises overall FAIL when any gate
        reports a real FAIL (not a WARN)."""
        results = [
            GateResult(gate_id="a", bucket="static", status="WARN").finalize(),
            GateResult(
                gate_id="b", bucket="static", status="FAIL",
                actual_fail_reason="real_defect",
            ).finalize(),
        ]
        from datetime import datetime, timezone
        rollup = _runner.build_rollup(
            "quick", None, datetime.now(timezone.utc), results, strict=True
        )
        assert rollup.overall_status == "FAIL"

    def test_error_dominates(self):
        results = [
            GateResult(
                gate_id="a", bucket="static", status="ERROR",
                actual_fail_reason="boom",
            ).finalize(),
            GateResult(gate_id="b", bucket="static", status="PASS").finalize(),
        ]
        from datetime import datetime, timezone
        rollup = _runner.build_rollup(
            "quick", None, datetime.now(timezone.utc), results, strict=False
        )
        assert rollup.overall_status == "ERROR"


class TestLegacySnapshotPin:
    def test_subprocess_gate_sets_adg_snapshot_env(self, tmp_path, monkeypatch):
        """Legacy gates must receive ADG_SNAPSHOT when the runner has --snapshot."""
        captured: dict[str, str] = {}

        def fake_run(cmd, **kwargs):  # noqa: ANN001
            captured["ADG_SNAPSHOT"] = kwargs.get("env", {}).get("ADG_SNAPSHOT", "")
            class _Proc:
                returncode = 0
                stdout = ""
                stderr = ""

            return _Proc()

        monkeypatch.setattr(_runner.subprocess, "run", fake_run)
        snap = tmp_path / "adg_indexed_01012026_1200.sqlite"
        snap.write_bytes(b"")
        logging.info("C3 write receipt: ADG gate snapshot fixture written")
        gate = {
            "gate_id": "static.edge_authority_well_formed",
            "bucket": "static",
            "script": "ops_scripts/ci/check_edge_authority_well_formed.py",
            "evidence_mode": "proof",
            "enforcement_mode": "strict",
            "legacy": True,
            "accepts_runner_flags": False,
        }
        _runner._run_subprocess_gate(gate, snapshot=snap, strict=True)
        assert captured["ADG_SNAPSHOT"] == str(snap.resolve())
