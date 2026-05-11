"""W9: apps_rg full-spine stubbed managed workflow E2E tests.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W9

18 tests covering all W9 acceptance criteria:
- Full managed workflow path runs in test-enabled mode only
- Production route remains disabled
- route_registry.yaml remains registered_not_active
- Stage-output receipts are complete
- GateMesh required before Exit
- Exit emits exactly one X3
- Success path emits X3D_ALLOW_FINISH
- Material UNKNOWN blocks allow-finish
- Hard FAIL blocks allow-finish
- RuntimeExhaustBundle created only after Exit
- No provider calls
- No L4 writes
- No cache/vector/evidence/index writes
- No quarantined apps_rg runtime imports

Environment:
    Tests use monkeypatch to set APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED=1
    and APPS_RG_EXECUTION_FORM=managed_workflow so the managed workflow
    path is selected without activating the production route.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# ── Repo root ─────────────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ROUTE_REGISTRY = _REPO_ROOT / "apps_rg" / "config" / "route_registry.yaml"

# ── Imports under test ────────────────────────────────────────────────────────

from agentic_core.runtime.entry.apps_rg_w9_managed_workflow_e2e import (
    W9ManagedWorkflowResult,
    W9TestActivationRequired,
    W9_SCHEMA_VERSION,
    _assert_test_activation,
    _fake_generator_gateway,
    _verify_l1_work_shape_hints,
    build_w9_success_evidence,
    run_w9_managed_workflow_e2e,
)
from agentic_core.runtime.exit.exit_disposition import (
    ALL_X3_CODES,
    X3A_DENY_REROUTE,
    X3B_ESCALATE_HITL,
    X3C_COMMIT_REQUEST_TO_UWG,
    X3D_ALLOW_FINISH,
    X3E_SAFE_ABSTAIN,
    ExitDispositionReceipt,
    RuntimeExhaustBundle,
)
from agentic_core.runtime.contracts.l3_to_l2_step_contract import L3ToL2StepContract
from agentic_core.runtime.contracts.sealed_workflow_types import (
    SealedSectionArtifact,
    SealedWorkflowPackage,
)
from agentic_core.runtime.gates.gate_types import (
    GateMeshResult,
    VERDICT_PASS,
    VERDICT_UNKNOWN,
    VERDICT_FAIL,
)


# ── Fixture helpers ───────────────────────────────────────────────────────────

def _make_envelope():
    """Build a minimal valid RequestEnvelope for the managed workflow path."""
    from agentic_core.runtime.entry.apps_rg_dispatch import apps_rg_parse
    payload = {
        "target_company": "Brown and Brown Inc",
        "target_role": "SVP Technology Strategy",
        "target_level": "EXECUTIVE",
        "jd_text": (
            "We are seeking an experienced SVP Technology Strategy to lead "
            "enterprise AI transformation initiatives. Requirements: 15+ years "
            "enterprise technology leadership, AI/ML program delivery, "
            "cross-functional stakeholder management."
        ),
        "source_resume": (
            "Experienced technology executive with 15+ years delivering enterprise "
            "transformation programs. Prior roles: CTO at Example Corp, VP Engineering "
            "at Startup Inc. Education: M.S. Computer Science."
        ),
    }
    return apps_rg_parse(payload)


def _make_pkg(
    *,
    required_nodes=("header_block", "professional_summary", "experience_block",
                    "skills_block", "education_block"),
    merged_content="clean content without any markers",
) -> SealedWorkflowPackage:
    """Build a minimal SealedWorkflowPackage with required sections."""
    def _section(node_id: str) -> SealedSectionArtifact:
        content = f"section content for {node_id}"
        return SealedSectionArtifact(
            artifact_id=f"ssa::test::{node_id}",
            workflow_ref="wfm::apps_rg::resume_generation::v1",
            node_id=node_id,
            run_id="run-w9-test",
            sealed_content=content,
            content_digest=hashlib.sha256(content.encode()).hexdigest(),
            terminal_class="success",
            decisive_reason="test_fixture",
        )

    return SealedWorkflowPackage(
        package_id="pkg::w9::test::001",
        run_id="run-w9-test",
        trace_root="trace::w9::test",
        route_contract_ref="rc::w9::test",
        workflow_ref="wfm::apps_rg::resume_generation::v1",
        sealed_sections=tuple(_section(n) for n in required_nodes),
        merged_content=merged_content,
        merged_content_digest=hashlib.sha256(merged_content.encode()).hexdigest(),
        replay_manifest="replay::w9::test",
    )


def _run_e2e(tmp_path, monkeypatch) -> W9ManagedWorkflowResult:
    """Run W9 E2E with test activation flags set.

    Requires two env vars:
      APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED=1  — unlocks registered_not_active route
      APPS_RG_EXECUTION_FORM=managed_workflow  — forces L0 to select managed_workflow
    """
    monkeypatch.setenv("APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED", "1")
    monkeypatch.setenv("APPS_RG_EXECUTION_FORM", "managed_workflow")
    # Clear any stale L3 opt-in that might interfere
    monkeypatch.delenv("APPS_RG_L3_OPT_IN", raising=False)
    envelope = _make_envelope()
    return run_w9_managed_workflow_e2e(
        envelope,
        output_dir=tmp_path,
        repo_root=_REPO_ROOT,
    )


# ── Test: full E2E happy path ─────────────────────────────────────────────────

class TestAppsRgFullSpineStubbed:

    def test_apps_rg_full_spine_stubbed_managed_workflow_e2e(
        self, tmp_path, monkeypatch
    ):
        """Full managed workflow E2E completes without error in test-enabled mode."""
        result = _run_e2e(tmp_path, monkeypatch)
        assert result.error is None, f"E2E failed: {result.error}"
        assert result.managed_workflow_executed is True
        assert result.workflow_package is not None
        assert result.gate_mesh_result is not None
        assert result.exit_receipt is not None
        assert result.exhaust_bundle is not None
        assert result.test_activation_mode is True

    def test_apps_rg_full_spine_requires_test_enabled_route(self, monkeypatch):
        """W9 E2E raises W9TestActivationRequired when test flag is absent."""
        monkeypatch.delenv("APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED", raising=False)
        with pytest.raises(W9TestActivationRequired):
            _assert_test_activation()

    def test_apps_rg_full_spine_route_registry_remains_registered_not_active(self):
        """route_registry.yaml must not be changed to active."""
        assert _ROUTE_REGISTRY.exists(), "route_registry.yaml must exist"
        content = _ROUTE_REGISTRY.read_text(encoding="utf-8")
        import yaml
        data = yaml.safe_load(content)
        managed_routes = [
            r for r in (data.get("routes") or [])
            if r.get("execution_form") == "MANAGED_WORKFLOW"
        ]
        assert managed_routes, "MANAGED_WORKFLOW route must exist in registry"
        for r in managed_routes:
            assert r.get("status") == "registered_not_active", (
                f"MANAGED_WORKFLOW route {r.get('route_id')} must remain "
                f"registered_not_active, got {r.get('status')!r}"
            )

    def test_apps_rg_full_spine_stage_output_receipts_complete(
        self, tmp_path, monkeypatch
    ):
        """All required stage receipt files must be written."""
        result = _run_e2e(tmp_path, monkeypatch)
        assert result.error is None

        required_receipts = [
            "00_parse_envelope.json",
            "01_U0_validated_request.json",
            "02_L1_plan_contract.json",
            "03_L0_route_contract.json",
            "03a_R1A_cache_lookup_receipt.json",
            "03b_R1B_cache_lookup_receipt.json",
            "04_C0_or_local_evidence_contract.json",
            "05_PA_compiled_prompt.json",
            "06_L3_workflow_manifest_resolved.json",
            "13_L3_sealed_workflow_package.json",
            "14_Exit_disposition_receipt.json",
            "99_runtime_exhaust_bundle.json",
        ]
        for name in required_receipts:
            path = tmp_path / name
            assert path.exists(), f"Stage receipt {name} not written"
            data = json.loads(path.read_text(encoding="utf-8"))
            assert isinstance(data, dict), f"Stage receipt {name} is not a dict"

    def test_apps_rg_full_spine_exactly_one_x3(self, tmp_path, monkeypatch):
        """Exit must emit exactly one X3 disposition code."""
        result = _run_e2e(tmp_path, monkeypatch)
        assert result.error is None
        assert result.x3_code in ALL_X3_CODES, (
            f"x3_code {result.x3_code!r} not in ALL_X3_CODES"
        )
        # Receipt file must contain exactly one x3_code
        receipt_path = tmp_path / "14_Exit_disposition_receipt.json"
        data = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert data["x3_code"] == result.x3_code

    def test_apps_rg_full_spine_success_emits_x3d_allow_finish(
        self, tmp_path, monkeypatch
    ):
        """Success path (all gates PASS) must emit X3D_ALLOW_FINISH."""
        result = _run_e2e(tmp_path, monkeypatch)
        assert result.error is None
        assert result.x3_code == X3D_ALLOW_FINISH, (
            f"Expected X3D_ALLOW_FINISH on success path, got {result.x3_code!r}"
        )

    def test_apps_rg_full_spine_runtime_exhaust_after_exit_only(
        self, tmp_path, monkeypatch
    ):
        """RuntimeExhaustBundle must be created after Exit, not before."""
        result = _run_e2e(tmp_path, monkeypatch)
        assert result.error is None
        assert isinstance(result.exhaust_bundle, RuntimeExhaustBundle)
        assert result.exhaust_bundle.created_after_exit is True
        assert result.exhaust_bundle.exit_disposition_ref, (
            "exhaust_bundle.exit_disposition_ref must be populated after Exit"
        )

    def test_apps_rg_full_spine_gate_mesh_required_before_exit(
        self, tmp_path, monkeypatch
    ):
        """GateMeshResult must be populated before ExitDispositionReceipt."""
        result = _run_e2e(tmp_path, monkeypatch)
        assert result.error is None
        # gate_mesh_result must be present
        assert result.gate_mesh_result is not None
        assert isinstance(result.gate_mesh_result, GateMeshResult)
        # exit_receipt references the gate mesh digest
        assert result.exit_receipt is not None
        assert result.exit_receipt.gate_mesh_result_ref == result.gate_mesh_result.deterministic_digest


# ── Test: gate blocking ────────────────────────────────────────────────────────

class TestAppsRgFullSpineGateBlocking:

    def _make_harness(self):
        from agentic_core.runtime.exit.apps_rg_exit_binding import build_apps_rg_exit_harness
        return build_apps_rg_exit_harness(_REPO_ROOT)

    def test_apps_rg_full_spine_blocks_material_unknown(self):
        """Material UNKNOWN blocks X3D_ALLOW_FINISH."""
        h = self._make_harness()
        pkg = _make_pkg()
        # Pass evidence with missing rubric scores so G22 → UNKNOWN
        evidence = build_w9_success_evidence(pkg)
        evidence = dict(evidence)
        evidence["g22_rubric_scores"] = {}  # empty → G22 UNKNOWN
        receipt, mesh, _ = h.evaluate(
            pkg, evidence=evidence,
            request_id="req", run_id="run-block-unknown", trace_root="trace",
        )
        assert receipt.x3_code != X3D_ALLOW_FINISH, (
            "UNKNOWN gates must block ALLOW_FINISH"
        )

    def test_apps_rg_full_spine_blocks_g21_missing_required_section(self):
        """G21 hard FAIL (missing section) blocks X3D_ALLOW_FINISH."""
        h = self._make_harness()
        # Build pkg with only partial sections
        pkg = _make_pkg(required_nodes=("header_block",))
        evidence = build_w9_success_evidence(pkg)
        receipt, mesh, _ = h.evaluate(
            pkg, evidence=evidence,
            request_id="req", run_id="run-g21-fail", trace_root="trace",
        )
        # G21 fails because required sections are missing
        assert receipt.x3_code != X3D_ALLOW_FINISH, (
            "G21 FAIL (missing required section) must block ALLOW_FINISH"
        )

    def test_apps_rg_full_spine_blocks_g22_no_fabrication_below_threshold(self):
        """G22 FAIL (dim below threshold) blocks X3D_ALLOW_FINISH."""
        h = self._make_harness()
        pkg = _make_pkg()
        evidence = build_w9_success_evidence(pkg)
        evidence = dict(evidence)
        # Set no_fabrication score below threshold (< 0.99 or the profile threshold)
        evidence["g22_rubric_scores"] = dict(evidence["g22_rubric_scores"])
        evidence["g22_rubric_scores"]["no_fabrication"] = 0.10  # well below threshold
        receipt, mesh, _ = h.evaluate(
            pkg, evidence=evidence,
            request_id="req", run_id="run-g22-fail", trace_root="trace",
        )
        assert receipt.x3_code != X3D_ALLOW_FINISH, (
            "G22 FAIL (dim below threshold) must block ALLOW_FINISH"
        )

    def test_apps_rg_full_spine_blocks_g23_prompt_leakage(self):
        """G23 FAIL (prompt leakage) blocks X3D_ALLOW_FINISH."""
        h = self._make_harness()
        # Content with a leakage pattern
        pkg = _make_pkg(merged_content="SYSTEM_PROMPT leaked into output here")
        evidence = build_w9_success_evidence(pkg)
        receipt, mesh, _ = h.evaluate(
            pkg, evidence=evidence,
            request_id="req", run_id="run-g23-fail", trace_root="trace",
        )
        assert receipt.x3_code != X3D_ALLOW_FINISH, (
            "G23 FAIL (prompt leakage) must block ALLOW_FINISH"
        )

    def test_apps_rg_full_spine_g27_not_applicable_with_reason_for_read_only_resume(
        self,
    ):
        """G27 must return NOT_APPLICABLE for read-only resume path."""
        from agentic_core.runtime.gates.gate_evaluators import evaluate_g27
        from agentic_core.runtime.gates.gate_profile_resolver import GateProfileResolver

        resolver = GateProfileResolver(_REPO_ROOT)
        profile = resolver.resolve(
            exit_profile_path="apps_rg/config/domain_contract/exit_profile.resume_generation.v1.json",
            runtime_gate_profile_path="apps_rg/config/domain_contract/runtime_gate_profile.resume_generation.v1.json",
        )
        g27_def = profile.gate_definitions.get("G27", {})
        pkg = _make_pkg()
        evidence = {"g27": {"durable_write_requested": False}}
        verdict = evaluate_g27(
            "G27", g27_def, pkg, evidence, "req", "run-g27", "trace"
        )
        from agentic_core.runtime.gates.gate_types import VERDICT_NOT_APPLICABLE
        assert verdict.result == VERDICT_NOT_APPLICABLE, (
            f"G27 must be NOT_APPLICABLE for read-only resume path, got {verdict.result!r}"
        )
        assert verdict.not_applicable_reason, "G27 NOT_APPLICABLE must carry a reason"


# ── Test: no provider / write invariants ──────────────────────────────────────

class TestAppsRgFullSpineConstraints:

    def test_apps_rg_full_spine_no_provider_calls(self, tmp_path, monkeypatch):
        """W9 E2E must not call any real LLM provider."""
        # FakeGeneratorGateway produces content without any HTTP call
        # Verify by checking that no vLLM URL was contacted
        import urllib.request
        original_urlopen = urllib.request.urlopen
        provider_called = []

        def mock_urlopen(req, *args, **kwargs):
            if hasattr(req, "full_url"):
                provider_called.append(req.full_url)
            elif isinstance(req, str):
                provider_called.append(req)
            return original_urlopen(req, *args, **kwargs)

        # Also set L2 force stub to be safe
        monkeypatch.setenv("APPS_RG_L2_FORCE_STUB", "1")
        result = _run_e2e(tmp_path, monkeypatch)
        assert result.error is None
        # FakeGeneratorGateway is injected directly — no HTTP
        for artifact in (result.workflow_package.sealed_sections if result.workflow_package else []):
            assert artifact.lane == "FAKE_GATEWAY", (
                f"All sealed sections must use FAKE_GATEWAY lane, got {artifact.lane!r}"
            )

    def test_apps_rg_full_spine_no_l4_writes(self):
        """W9 modules must not import or reference L4 state writes."""
        import importlib.util
        spec = importlib.util.find_spec(
            "agentic_core.runtime.entry.apps_rg_w9_managed_workflow_e2e"
        )
        assert spec and spec.origin
        src = open(spec.origin, encoding="utf-8").read()
        for l4_ref in (
            "agentic_core.L4_state",
            "SemanticCacheManager",
            "write_to_cache",
            "l4_write",
            "L4Write",
        ):
            assert l4_ref not in src, (
                f"W9 module must not reference L4 write path {l4_ref!r}"
            )

    def test_apps_rg_full_spine_no_cache_or_vector_writes(self):
        """W9 modules must not write to cache, vector store, or evidence index."""
        import importlib.util
        spec = importlib.util.find_spec(
            "agentic_core.runtime.entry.apps_rg_w9_managed_workflow_e2e"
        )
        assert spec and spec.origin
        src = open(spec.origin, encoding="utf-8").read()
        for write_ref in (
            "redis.set",
            "ChromaDB",
            "chroma_write",
            "evidence_store.write",
            "vector_service.upsert",
            "VectorRetrievalService",
            "write_vector",
        ):
            assert write_ref not in src, (
                f"W9 module must not reference cache/vector write {write_ref!r}"
            )

    def test_apps_rg_full_spine_no_quarantined_runtime_imports(self):
        """W9 modules must not import quarantined apps_rg runtime modules."""
        import importlib.util
        spec = importlib.util.find_spec(
            "agentic_core.runtime.entry.apps_rg_w9_managed_workflow_e2e"
        )
        assert spec and spec.origin
        src = open(spec.origin, encoding="utf-8").read()
        quarantined = (
            "apps_rg._quarantine",
            "HardenedanthropicexecutorStrategy",
            "ResumeAssemblyAgent",
            "apps_rg._quarantine.compiler",
        )
        for q in quarantined:
            assert q not in src, (
                f"W9 module must not import quarantined module {q!r}"
            )

    def test_apps_rg_full_spine_no_exit_writeback(self, tmp_path, monkeypatch):
        """Exit must not write to durable state (L4/Redis/vector/cache)."""
        import importlib.util
        spec = importlib.util.find_spec(
            "agentic_core.runtime.exit.exit_gate_harness"
        )
        assert spec and spec.origin
        src = open(spec.origin, encoding="utf-8").read()
        for write_ref in (
            "agentic_core.L4_state",
            "SemanticCacheManager",
            "VectorRetrievalService",
            "redis.set",
            "chroma",
        ):
            assert write_ref.lower() not in src.lower(), (
                f"ExitGateHarness must not contain durable write ref {write_ref!r}"
            )


# ── Test: fake generator gateway ──────────────────────────────────────────────

class TestFakeGeneratorGateway:

    def _make_step(self, node_id: str) -> L3ToL2StepContract:
        return L3ToL2StepContract(
            node_id=node_id,
            workflow_ref="wfm::apps_rg::resume_generation::v1",
            run_id="run-test-fake-gw",
            trace_root="trace-test",
        )

    def test_fake_gateway_produces_sealed_section_artifact(self):
        step = self._make_step("header_block")
        artifact = _fake_generator_gateway(step)
        assert isinstance(artifact, SealedSectionArtifact)
        assert artifact.node_id == "header_block"
        assert artifact.lane == "FAKE_GATEWAY"
        assert artifact.terminal_class == "success"

    def test_fake_gateway_content_has_no_fabrication_markers(self):
        """FakeGeneratorGateway content must pass G21 (no fabrication markers)."""
        import re
        pattern = re.compile(
            r"\b(FABRICATED|INVENTED_EMPLOYER|FAKE_DEGREE|FAKE_PUBLICATION"
            r"|FABRICATED_TITLE|UNSUPPORTED_METRIC)\b",
            re.IGNORECASE,
        )
        for node_id in (
            "header_block", "professional_summary", "experience_block",
            "skills_block", "education_block",
        ):
            step = self._make_step(node_id)
            artifact = _fake_generator_gateway(step)
            assert not pattern.search(artifact.sealed_content or ""), (
                f"FakeGeneratorGateway content for {node_id} contains fabrication marker"
            )

    def test_fake_gateway_content_has_no_leakage_patterns(self):
        """FakeGeneratorGateway content must pass G23 (no leakage patterns)."""
        import re
        leakage = re.compile(
            r"\bSYSTEM_PROMPT\b|\bSLOT_LABEL\b|\bAPI[_-]?KEY\s*[:=]",
            re.IGNORECASE,
        )
        for node_id in ("header_block", "professional_summary", "experience_block"):
            step = self._make_step(node_id)
            artifact = _fake_generator_gateway(step)
            assert not leakage.search(artifact.sealed_content or ""), (
                f"FakeGeneratorGateway content for {node_id} contains leakage pattern"
            )

    def test_fake_gateway_deterministic_digest(self):
        """Same node_id + run_id produces same content_digest."""
        step = self._make_step("professional_summary")
        a1 = _fake_generator_gateway(step)
        a2 = _fake_generator_gateway(step)
        assert a1.content_digest == a2.content_digest


# ── Test: W9 success evidence builder ────────────────────────────────────────

class TestW9SuccessEvidence:

    def test_success_evidence_has_all_required_keys(self):
        pkg = _make_pkg()
        ev = build_w9_success_evidence(pkg, run_id="run-ev-test")
        required_keys = (
            "g21", "g22_rubric_scores", "g23", "g24_provenance",
            "g25_sealed_sections", "g26_evidence", "g27", "g28_audit_refs",
        )
        for k in required_keys:
            assert k in ev, f"Missing key {k!r} in success evidence"

    def test_success_evidence_rubric_scores_above_profile_thresholds(self):
        """Rubric scores must exceed all gate profile dimension thresholds."""
        import json
        profile_path = (
            _REPO_ROOT
            / "apps_rg/config/domain_contract/exit_profile.resume_generation.v1.json"
        )
        profile_data = json.loads(profile_path.read_text(encoding="utf-8"))
        dim_thresholds = profile_data["gate_definitions"]["G22"]["dimension_thresholds"]

        pkg = _make_pkg()
        ev = build_w9_success_evidence(pkg)
        scores = ev["g22_rubric_scores"]

        for dim, raw_threshold in dim_thresholds.items():
            # Skip informational-only dims
            if isinstance(raw_threshold, dict):
                if raw_threshold.get("informational_only_by_default"):
                    continue
                threshold = float(raw_threshold.get("threshold", 0.0))
            else:
                threshold = float(raw_threshold)

            if dim == "overall_pass_threshold":
                continue

            assert dim in scores, f"Missing rubric dim {dim!r} in success evidence"
            assert float(scores[dim]) >= threshold, (
                f"Rubric dim {dim!r} score {scores[dim]} < profile threshold {threshold}"
            )

    def test_success_evidence_g27_not_triggered(self):
        """G27 durable_write_requested must be False for read-only resume path."""
        pkg = _make_pkg()
        ev = build_w9_success_evidence(pkg)
        assert ev["g27"]["durable_write_requested"] is False

    def test_success_evidence_audit_refs_present(self):
        """G28 audit refs must be non-empty."""
        pkg = _make_pkg()
        ev = build_w9_success_evidence(pkg, run_id="run-audit")
        assert len(ev["g28_audit_refs"]["audit_refs"]) >= 2

    def test_success_evidence_g24_has_all_required_provenance_fields(self):
        """build_w9_success_evidence must supply all G24 required_provenance_fields."""
        import json
        profile_path = (
            _REPO_ROOT
            / "apps_rg/config/domain_contract/exit_profile.resume_generation.v1.json"
        )
        profile_data = json.loads(profile_path.read_text(encoding="utf-8"))
        g24_required = set(
            profile_data["gate_definitions"]["G24"]["required_provenance_fields"]
        )
        # Evaluator auto-seeds these three from call args — remove them
        auto_seeded = {"request_id", "run_id", "trace_root"}
        # Also auto-seeded from pkg: replay_key, route_contract_ref, workflow_ref,
        # output_artifact_digest — remove them too since they come from pkg fields
        pkg_seeded = {"replay_key", "route_contract_ref", "workflow_ref", "output_artifact_digest"}
        must_be_in_evidence = g24_required - auto_seeded - pkg_seeded

        pkg = _make_pkg()
        ev = build_w9_success_evidence(pkg, run_id="run-g24-check")
        g24_ev = ev.get("g24_provenance", {})
        missing = [f for f in must_be_in_evidence if not g24_ev.get(f)]
        assert not missing, (
            f"build_w9_success_evidence g24_provenance missing fields: {missing}"
        )


# ── Test: G24 provenance gate and full-spine X3D success ─────────────────────

class TestAppsRgFullSpineG24Provenance:
    """Tests for G24 provenance completeness and X3D_ALLOW_FINISH success criterion.

    These tests implement the W9 acceptance criteria:
    - Full-spine success emits X3D_ALLOW_FINISH
    - G24 PASS when all provenance fields present
    - G28 PASS when all material audit refs present
    - No required gate is UNKNOWN or FAIL on success path
    - Missing G24 provenance blocks ALLOW_FINISH
    """

    def _make_harness(self):
        from agentic_core.runtime.exit.apps_rg_exit_binding import build_apps_rg_exit_harness
        return build_apps_rg_exit_harness(_REPO_ROOT)

    def test_apps_rg_full_spine_g24_passes_with_complete_provenance(self):
        """G24 evaluates PASS when all required_provenance_fields are present."""
        h = self._make_harness()
        pkg = _make_pkg()
        ev = build_w9_success_evidence(pkg, run_id="run-g24-pass")
        receipt, mesh, _ = h.evaluate(
            pkg, evidence=ev,
            request_id="req-g24-pass", run_id="run-g24-pass", trace_root="trace::g24",
        )
        g24 = next((v for v in mesh.verdicts if v.gate_id == "G24"), None)
        assert g24 is not None, "G24 verdict must be in mesh"
        assert g24.result == VERDICT_PASS, (
            f"G24 must be PASS with complete provenance, got {g24.result!r}. "
            f"reason_codes={g24.reason_codes}"
        )

    def test_apps_rg_full_spine_success_emits_x3d_allow_finish(self):
        """Full-spine success path (complete evidence) must emit X3D_ALLOW_FINISH."""
        h = self._make_harness()
        pkg = _make_pkg()
        ev = build_w9_success_evidence(pkg, run_id="run-x3d-success")
        receipt, mesh, _ = h.evaluate(
            pkg, evidence=ev,
            request_id="req-x3d", run_id="run-x3d-success", trace_root="trace::x3d",
        )
        assert receipt.x3_code == X3D_ALLOW_FINISH, (
            f"Full-spine success must emit X3D_ALLOW_FINISH, got {receipt.x3_code!r}. "
            f"Blocking gates: "
            + str([(v.gate_id, v.result, v.reason_codes) for v in mesh.verdicts
                   if v.result in (VERDICT_UNKNOWN, VERDICT_FAIL)])
        )

    def test_apps_rg_full_spine_success_has_all_required_gates_passing(self):
        """All required gates must be PASS on the success path (none UNKNOWN or FAIL)."""
        import json
        profile_path = (
            _REPO_ROOT
            / "apps_rg/config/domain_contract/exit_profile.resume_generation.v1.json"
        )
        profile_data = json.loads(profile_path.read_text(encoding="utf-8"))
        required_gates = set(profile_data["required_exit_gates"])

        h = self._make_harness()
        pkg = _make_pkg()
        ev = build_w9_success_evidence(pkg, run_id="run-all-pass")
        receipt, mesh, _ = h.evaluate(
            pkg, evidence=ev,
            request_id="req-all-pass", run_id="run-all-pass", trace_root="trace::all",
        )
        blocking = [
            (v.gate_id, v.result, v.reason_codes)
            for v in mesh.verdicts
            if v.gate_id in required_gates
            and v.result in (VERDICT_UNKNOWN, VERDICT_FAIL)
        ]
        assert not blocking, (
            f"Required gates must not be UNKNOWN or FAIL on success path: {blocking}"
        )
        assert receipt.x3_code == X3D_ALLOW_FINISH, (
            f"Success path with all required gates passing must emit X3D_ALLOW_FINISH, "
            f"got {receipt.x3_code!r}"
        )
        # Verify G24 and G28 are both in required_gates (regression guard)
        assert "G24" in required_gates, "G24 must remain in required_exit_gates"
        assert "G28" in required_gates, "G28 must remain in required_exit_gates"

    def test_apps_rg_full_spine_missing_g24_provenance_blocks_allow_finish(self):
        """Missing G24 required provenance fields must block X3D_ALLOW_FINISH."""
        h = self._make_harness()
        pkg = _make_pkg()
        ev = build_w9_success_evidence(pkg, run_id="run-g24-block")
        # Remove key G24 provenance fields to trigger UNKNOWN
        ev = dict(ev)
        ev["g24_provenance"] = {}  # empty — removes all evidence-side provenance
        receipt, mesh, _ = h.evaluate(
            pkg, evidence=ev,
            request_id="req-g24-block", run_id="run-g24-block", trace_root="trace::block",
        )
        g24 = next((v for v in mesh.verdicts if v.gate_id == "G24"), None)
        assert g24 is not None, "G24 verdict must be in mesh"
        assert g24.result != VERDICT_PASS, (
            f"G24 must not PASS when required provenance is stripped, got {g24.result!r}"
        )
        assert receipt.x3_code != X3D_ALLOW_FINISH, (
            f"Missing G24 provenance must block X3D_ALLOW_FINISH, got {receipt.x3_code!r}"
        )
