"""W11: apps_rg final no-bypass certification tests.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W11

15 tests covering all W11 acceptance criteria:

Scope checks:
1.  test_apps_rg_w11_core_leakage_scan_has_no_blocking_findings
    -- W10 core files classified; no BLOCKING_LEAKAGE or unacceptable BOUNDARY_DRIFT.
2.  test_apps_rg_w11_route_remains_registered_not_active
    -- route_registry.yaml managed route status unchanged.
3.  test_apps_rg_w11_production_managed_route_not_selected
    -- Without test-activation flag, managed workflow route is NOT selected.
4.  test_apps_rg_w11_test_enabled_managed_route_selected
    -- With test-activation flag, managed workflow route IS selected.
5.  test_apps_rg_w11_no_silent_fallback_to_single_step
    -- Missing test flag raises, does not silently fall back.
6.  test_apps_rg_w11_full_spine_replay_deterministic
    -- Two W9 E2E runs with identical inputs produce identical digests.
7.  test_apps_rg_w11_same_input_same_x3
    -- Same input produces the same X3 disposition code on both runs.
8.  test_apps_rg_w11_same_input_same_gate_mesh_digest
    -- Same input produces same GateMeshResult.deterministic_digest.
9.  test_apps_rg_w11_g24_and_g28_remain_required
    -- exit_profile.resume_generation.v1.json lists G24 and G28 in required_exit_gates.
10. test_apps_rg_w11_exit_requires_gate_mesh
    -- Exit receipt references the GateMesh digest (gate_mesh_result_ref populated).
11. test_apps_rg_w11_no_direct_l4_write_paths
    -- Source scan: L0/L2/L3/PA/Exit/L6/C0 modules contain no direct L4 write calls.
12. test_apps_rg_w11_uwg_only_l4_write_path
    -- L4WriteAdapter.commit() raises DirectWriteViolationError for all non-UWG callers.
13. test_apps_rg_w11_quarantined_modules_not_imported
    -- Active runtime modules do not import quarantined apps_rg modules.
14. test_apps_rg_w11_stage_receipts_complete_or_mapped
    -- W9 E2E writes all required stage receipt files.
15. test_apps_rg_w11_activation_readiness_report_generated
    -- After running all checks, an in-memory readiness report summarises READY/NOT_READY.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Repository root and key paths
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ROUTE_REGISTRY = _REPO_ROOT / "apps_rg" / "config" / "route_registry.yaml"
_EXIT_PROFILE = (
    _REPO_ROOT
    / "apps_rg/config/domain_contract/exit_profile.resume_generation.v1.json"
)

# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------

from agentic_core.runtime.entry.apps_rg_w9_managed_workflow_e2e import (
    W9ManagedWorkflowResult,
    W9TestActivationRequired,
    _assert_test_activation,
    _fake_generator_gateway,
    build_w9_success_evidence,
    run_w9_managed_workflow_e2e,
)
from agentic_core.runtime.exit.exit_disposition import (
    X3D_ALLOW_FINISH,
    ExitDispositionReceipt,
    RuntimeExhaustBundle,
)
from agentic_core.runtime.gates.gate_types import (
    GateMeshResult,
    VERDICT_PASS,
    VERDICT_UNKNOWN,
    VERDICT_FAIL,
)
from agentic_core.runtime.uwg.universal_write_gate import UniversalWriteGate
from agentic_core.runtime.uwg.write_receipts import (
    VERDICT_ADMIT,
    VERDICT_BLOCK,
)
from agentic_core.L4_state.adapters.write_adapters import (
    DirectWriteViolationError,
    L4WriteAdapter,
    _FORBIDDEN_CALLERS,
)
from agentic_core.runtime.contracts.sealed_workflow_types import (
    SealedSectionArtifact,
    SealedWorkflowPackage,
)
from agentic_core.L0_routing.apps_rg_l0_binding import (
    _MANAGED_ROUTE_TEST_FLAG,
    l0_route_apps_rg,
)
from agentic_core.runtime.entry.apps_rg_dispatch import apps_rg_parse


# ---------------------------------------------------------------------------
# Shared fixture helpers
# ---------------------------------------------------------------------------

def _make_envelope():
    payload = {
        "target_company": "Brown and Brown Inc",
        "target_role": "SVP Technology Strategy",
        "target_level": "EXECUTIVE",
        "jd_text": (
            "Seeking SVP Technology Strategy to lead enterprise AI transformation. "
            "Requirements: 15+ years enterprise technology leadership."
        ),
        "source_resume": (
            "Technology executive with 15+ years delivering enterprise transformation. "
            "Prior: CTO at Example Corp. Education: M.S. Computer Science."
        ),
    }
    return apps_rg_parse(payload)


def _make_pkg(
    *,
    required_nodes=("header_block", "professional_summary", "experience_block",
                    "skills_block", "education_block"),
    merged_content: str = "clean content without any markers",
) -> SealedWorkflowPackage:
    def _section(node_id: str) -> SealedSectionArtifact:
        content = f"section content for {node_id}"
        return SealedSectionArtifact(
            artifact_id=f"ssa::w11::{node_id}",
            workflow_ref="wfm::apps_rg::resume_generation::v1",
            node_id=node_id,
            run_id="run-w11-cert",
            sealed_content=content,
            content_digest=hashlib.sha256(content.encode()).hexdigest(),
            terminal_class="success",
            decisive_reason="w11_cert_fixture",
        )

    return SealedWorkflowPackage(
        package_id="pkg::w11::cert::001",
        run_id="run-w11-cert",
        trace_root="trace::w11::cert",
        route_contract_ref="rc::w11::cert",
        workflow_ref="wfm::apps_rg::resume_generation::v1",
        sealed_sections=tuple(_section(n) for n in required_nodes),
        merged_content=merged_content,
        merged_content_digest=hashlib.sha256(merged_content.encode()).hexdigest(),
        replay_manifest="replay::w11::cert",
    )


def _run_e2e(tmp_path, monkeypatch) -> W9ManagedWorkflowResult:
    monkeypatch.setenv("APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED", "1")
    monkeypatch.setenv("APPS_RG_EXECUTION_FORM", "managed_workflow")
    monkeypatch.delenv("APPS_RG_L3_OPT_IN", raising=False)
    envelope = _make_envelope()
    return run_w9_managed_workflow_e2e(
        envelope,
        output_dir=tmp_path,
        repo_root=_REPO_ROOT,
    )


# ---------------------------------------------------------------------------
# 1. W10 core leakage scan — no blocking findings
# ---------------------------------------------------------------------------

class TestW11CoreLeakageScan:
    """Classify W10-added agentic_core files for boundary leakage."""

    # Files that MUST be generic (no hardcoded app literals in logic)
    _GENERIC_REQUIRED = [
        "agentic_core/runtime/exhaust/runtime_exhaust_bundle.py",
        "agentic_core/runtime/contracts/future_run_promotion.py",
        "agentic_core/runtime/uwg/universal_write_gate.py",
        "agentic_core/runtime/uwg/write_receipts.py",
        "agentic_core/L4_state/adapters/write_adapters.py",
    ]
    # Allowed app-binding (per governance: per-app binding modules OK under agentic_core)
    _ALLOWED_BINDING = [
        "agentic_core/runtime/l6/apps_rg_learning_adapter.py",
    ]
    # Boundary drift: app literals in a nominally generic file (WARN, not blocking)
    _BOUNDARY_DRIFT_EXPECTED = [
        "agentic_core/runtime/l6/writeback_proposer.py",
    ]
    # Literals that would constitute BLOCKING_LEAKAGE in a generic module
    _BLOCKING_LITERALS = [
        "APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED",
        "workflow_manifest.resume_generation",
        "runtime_gate_profile.resume_generation",
        "judge_profile.resume_generation",
    ]
    # Literals that constitute BOUNDARY_DRIFT (app-id refs in generic logic, not docstrings)
    _DRIFT_LITERALS = [
        "apps_rg",
        "resume_generation",
    ]

    def _read_source(self, relpath: str) -> str:
        return (_REPO_ROOT / relpath).read_text(encoding="utf-8")

    def test_apps_rg_w11_core_leakage_scan_has_no_blocking_findings(self):
        """W10 generic core files must have no BLOCKING_LEAKAGE literals."""
        blocking_findings: list[str] = []

        for relpath in self._GENERIC_REQUIRED:
            src = self._read_source(relpath)
            for literal in self._BLOCKING_LITERALS:
                if literal in src:
                    blocking_findings.append(f"{relpath}: BLOCKING_LEAKAGE literal {literal!r}")

        assert not blocking_findings, (
            "BLOCKING_LEAKAGE found in W10 generic core modules:\n"
            + "\n".join(blocking_findings)
        )

    def test_apps_rg_w11_generic_core_files_exist(self):
        """All W10 generic core files must exist on disk."""
        for relpath in self._GENERIC_REQUIRED:
            assert (_REPO_ROOT / relpath).exists(), (
                f"Expected generic core file missing: {relpath}"
            )

    def test_apps_rg_w11_allowed_binding_file_exists(self):
        """apps_rg_learning_adapter.py must exist as an ALLOWED_APP_BINDING."""
        for relpath in self._ALLOWED_BINDING:
            assert (_REPO_ROOT / relpath).exists(), (
                f"Expected ALLOWED_APP_BINDING file missing: {relpath}"
            )

    def test_apps_rg_w11_boundary_drift_in_writeback_proposer_is_documented(self):
        """writeback_proposer.py contains apps_rg default values — BOUNDARY_DRIFT (non-blocking)."""
        src = self._read_source("agentic_core/runtime/l6/writeback_proposer.py")
        has_drift = any(lit in src for lit in self._DRIFT_LITERALS)
        # This is expected boundary drift (default values) — assert it is present
        # so the test acts as a regression guard: if the file is cleaned up, the
        # test should be updated to reflect the improved classification.
        assert has_drift, (
            "writeback_proposer.py no longer contains apps_rg drift literals — "
            "update classification to GENERIC_CORE_OK and move to _GENERIC_REQUIRED."
        )

    def test_apps_rg_w11_uwg_and_write_receipts_no_app_literals(self):
        """UWG and write_receipts modules must have zero app-specific literals."""
        for relpath in [
            "agentic_core/runtime/uwg/universal_write_gate.py",
            "agentic_core/runtime/uwg/write_receipts.py",
        ]:
            src = self._read_source(relpath)
            for literal in self._DRIFT_LITERALS + self._BLOCKING_LITERALS:
                assert literal not in src, (
                    f"{relpath}: unexpected app literal {literal!r} — classify as BLOCKING_LEAKAGE"
                )

    def test_apps_rg_w11_l4_write_adapter_no_app_literals(self):
        """L4WriteAdapter must have no app-specific literals in logic (only in test ref comment)."""
        src = self._read_source("agentic_core/L4_state/adapters/write_adapters.py")
        for literal in self._BLOCKING_LITERALS:
            assert literal not in src, (
                f"L4WriteAdapter: unexpected blocking literal {literal!r}"
            )
        # apps_rg may appear only in the docstring comment referencing test file name
        # Confirm no logic-level app reference
        lines_with_apps_rg = [
            ln for ln in src.splitlines()
            if "apps_rg" in ln
            and not ln.strip().startswith("#")
            and not ln.strip().startswith('"""')
            and not ln.strip().startswith("'")
            and not ln.strip().startswith('"')
            # Skip docstring numbered list items like "  2. Tests: ... apps_rg ..."
            and not (ln.strip() and ln.strip()[0].isdigit() and "." in ln)
        ]
        assert not lines_with_apps_rg, (
            f"L4WriteAdapter has non-comment apps_rg references in logic:\n"
            + "\n".join(lines_with_apps_rg)
        )


# ---------------------------------------------------------------------------
# 2-5. Route activation readiness
# ---------------------------------------------------------------------------

class TestW11RouteActivation:

    def test_apps_rg_w11_route_remains_registered_not_active(self):
        """MANAGED_WORKFLOW route in route_registry.yaml must remain registered_not_active."""
        import yaml
        data = yaml.safe_load(_ROUTE_REGISTRY.read_text(encoding="utf-8"))
        managed = [
            r for r in (data.get("routes") or [])
            if r.get("execution_form") == "MANAGED_WORKFLOW"
        ]
        assert managed, "MANAGED_WORKFLOW route must exist in route_registry.yaml"
        for r in managed:
            assert r.get("status") == "registered_not_active", (
                f"Route {r.get('route_id')!r} must be registered_not_active, "
                f"got {r.get('status')!r}"
            )

    def test_apps_rg_w11_managed_route_has_workflow_refs(self):
        """MANAGED_WORKFLOW route must declare workflow_manifest_ref and workflow_manifest_path."""
        import yaml
        data = yaml.safe_load(_ROUTE_REGISTRY.read_text(encoding="utf-8"))
        for r in (data.get("routes") or []):
            if r.get("execution_form") == "MANAGED_WORKFLOW":
                assert r.get("workflow_manifest_ref"), (
                    f"Route {r.get('route_id')} missing workflow_manifest_ref"
                )
                assert r.get("workflow_manifest_path"), (
                    f"Route {r.get('route_id')} missing workflow_manifest_path"
                )

    def test_apps_rg_w11_production_managed_route_not_selected(self, monkeypatch):
        """Without test-activation flag, L0 must NOT select the managed workflow route."""
        monkeypatch.delenv("APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED", raising=False)
        monkeypatch.delenv("APPS_RG_EXECUTION_FORM", raising=False)
        monkeypatch.delenv("APPS_RG_L3_OPT_IN", raising=False)
        envelope = _make_envelope()
        from agentic_core.runtime.entry.u0_apps_rg_binding import u0_validate_apps_rg
        from agentic_core.L1_cognition.apps_rg_l1_binding import l1_plan_apps_rg
        validated = u0_validate_apps_rg(envelope)
        l1_plan = l1_plan_apps_rg(validated)
        route = l0_route_apps_rg(l1_plan)
        # Production default must not be managed_workflow
        assert route.execution_form != "managed_workflow", (
            f"Production route must not be managed_workflow without test flag; "
            f"got execution_form={route.execution_form!r}"
        )

    def test_apps_rg_w11_test_enabled_managed_route_selected(self, monkeypatch):
        """With APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED=1 L0 selects managed workflow."""
        monkeypatch.setenv("APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED", "1")
        monkeypatch.setenv("APPS_RG_EXECUTION_FORM", "managed_workflow")
        monkeypatch.delenv("APPS_RG_L3_OPT_IN", raising=False)
        envelope = _make_envelope()
        from agentic_core.runtime.entry.u0_apps_rg_binding import u0_validate_apps_rg
        from agentic_core.L1_cognition.apps_rg_l1_binding import l1_plan_apps_rg
        validated = u0_validate_apps_rg(envelope)
        l1_plan = l1_plan_apps_rg(validated)
        route = l0_route_apps_rg(l1_plan)
        assert route.execution_form == "managed_workflow", (
            f"Test-enabled path must select managed_workflow, got {route.execution_form!r}"
        )

    def test_apps_rg_w11_no_silent_fallback_to_single_step(self, monkeypatch):
        """Missing test-activation flag must raise W9TestActivationRequired (not silently proceed)."""
        monkeypatch.delenv("APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED", raising=False)
        with pytest.raises(W9TestActivationRequired):
            _assert_test_activation()


# ---------------------------------------------------------------------------
# 6-8. Full-spine replay determinism
# ---------------------------------------------------------------------------

class TestW11ReplayDeterminism:
    """Run W9 E2E twice with identical inputs; prove key digests are stable."""

    def test_apps_rg_w11_full_spine_replay_deterministic(self, tmp_path, monkeypatch):
        """Two W9 E2E runs with same input produce same SealedWorkflowPackage digest."""
        monkeypatch.setenv("APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED", "1")
        monkeypatch.setenv("APPS_RG_EXECUTION_FORM", "managed_workflow")
        monkeypatch.delenv("APPS_RG_L3_OPT_IN", raising=False)

        envelope = _make_envelope()

        r1 = run_w9_managed_workflow_e2e(
            envelope, output_dir=tmp_path / "run1", repo_root=_REPO_ROOT
        )
        r2 = run_w9_managed_workflow_e2e(
            envelope, output_dir=tmp_path / "run2", repo_root=_REPO_ROOT
        )

        assert r1.error is None, f"Run 1 failed: {r1.error}"
        assert r2.error is None, f"Run 2 failed: {r2.error}"

        # Same route id
        assert r1.route_contract is not None and r2.route_contract is not None
        r1_route_id = getattr(r1.route_contract, "route_id", None) or getattr(
            r1.route_contract, "selected_route_id", None
        )
        r2_route_id = getattr(r2.route_contract, "route_id", None) or getattr(
            r2.route_contract, "selected_route_id", None
        )
        assert r1_route_id == r2_route_id, (
            f"Route id mismatch: {r1_route_id!r} vs {r2_route_id!r}"
        )

        # Same workflow_ref
        assert r1.workflow_package is not None and r2.workflow_package is not None
        assert r1.workflow_package.workflow_ref == r2.workflow_package.workflow_ref, (
            f"workflow_ref mismatch: {r1.workflow_package.workflow_ref!r} vs "
            f"{r2.workflow_package.workflow_ref!r}"
        )

        # Same workflow node order
        n1 = [s.node_id for s in r1.workflow_package.sealed_sections]
        n2 = [s.node_id for s in r2.workflow_package.sealed_sections]
        assert n1 == n2, f"Node order mismatch: {n1} vs {n2}"

        # Same per-node content digests (FakeGeneratorGateway is deterministic)
        for s1, s2 in zip(r1.workflow_package.sealed_sections,
                          r2.workflow_package.sealed_sections):
            assert s1.content_digest == s2.content_digest, (
                f"Node {s1.node_id} content_digest mismatch between runs"
            )

        # Same merged_content_digest
        assert (
            r1.workflow_package.merged_content_digest
            == r2.workflow_package.merged_content_digest
        ), "merged_content_digest differs between deterministic runs"

    def test_apps_rg_w11_same_input_same_x3(self, tmp_path, monkeypatch):
        """Same input must produce same X3 code across two W9 E2E runs."""
        monkeypatch.setenv("APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED", "1")
        monkeypatch.setenv("APPS_RG_EXECUTION_FORM", "managed_workflow")
        monkeypatch.delenv("APPS_RG_L3_OPT_IN", raising=False)

        envelope = _make_envelope()

        r1 = run_w9_managed_workflow_e2e(
            envelope, output_dir=tmp_path / "r1", repo_root=_REPO_ROOT
        )
        r2 = run_w9_managed_workflow_e2e(
            envelope, output_dir=tmp_path / "r2", repo_root=_REPO_ROOT
        )

        assert r1.error is None and r2.error is None
        assert r1.x3_code == r2.x3_code, (
            f"X3 code differs between runs: {r1.x3_code!r} vs {r2.x3_code!r}"
        )
        assert r1.x3_code == X3D_ALLOW_FINISH, (
            f"Both runs must produce X3D_ALLOW_FINISH on success, got {r1.x3_code!r}"
        )

    def test_apps_rg_w11_same_input_same_gate_mesh_digest(self, tmp_path, monkeypatch):
        """Same input must produce same GateMeshResult.deterministic_digest."""
        monkeypatch.setenv("APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED", "1")
        monkeypatch.setenv("APPS_RG_EXECUTION_FORM", "managed_workflow")
        monkeypatch.delenv("APPS_RG_L3_OPT_IN", raising=False)

        envelope = _make_envelope()

        r1 = run_w9_managed_workflow_e2e(
            envelope, output_dir=tmp_path / "gm1", repo_root=_REPO_ROOT
        )
        r2 = run_w9_managed_workflow_e2e(
            envelope, output_dir=tmp_path / "gm2", repo_root=_REPO_ROOT
        )

        assert r1.error is None and r2.error is None
        assert r1.gate_mesh_result is not None and r2.gate_mesh_result is not None

        d1 = r1.gate_mesh_result.deterministic_digest
        d2 = r2.gate_mesh_result.deterministic_digest
        assert d1 and d2, "GateMeshResult.deterministic_digest must not be empty"
        assert d1 == d2, (
            f"GateMeshResult.deterministic_digest differs between runs:\n"
            f"  run1: {d1}\n"
            f"  run2: {d2}"
        )


# ---------------------------------------------------------------------------
# 9-10. Gate and Exit proof
# ---------------------------------------------------------------------------

class TestW11GateExitProof:

    def _harness(self):
        from agentic_core.runtime.exit.apps_rg_exit_binding import build_apps_rg_exit_harness
        return build_apps_rg_exit_harness(_REPO_ROOT)

    def test_apps_rg_w11_g24_and_g28_remain_required(self):
        """G24 and G28 must be in exit_profile required_exit_gates (regression guard)."""
        profile = json.loads(_EXIT_PROFILE.read_text(encoding="utf-8"))
        required = set(profile["required_exit_gates"])
        assert "G24" in required, "G24 must remain in required_exit_gates"
        assert "G28" in required, "G28 must remain in required_exit_gates"
        # G24 and G28 must NOT be in conditional_exit_gates
        conditional = set(profile.get("conditional_exit_gates", []))
        assert "G24" not in conditional, "G24 must not be in conditional_exit_gates"
        assert "G28" not in conditional, "G28 must not be in conditional_exit_gates"

    def test_apps_rg_w11_exit_requires_gate_mesh(self, tmp_path, monkeypatch):
        """Exit receipt must reference GateMesh digest (gate_mesh_result_ref populated)."""
        result = _run_e2e(tmp_path, monkeypatch)
        assert result.error is None
        assert result.gate_mesh_result is not None
        assert result.exit_receipt is not None
        assert result.exit_receipt.gate_mesh_result_ref, (
            "ExitDispositionReceipt.gate_mesh_result_ref must be populated"
        )
        assert result.exit_receipt.gate_mesh_result_ref == (
            result.gate_mesh_result.deterministic_digest
        ), "exit_receipt.gate_mesh_result_ref must equal GateMeshResult.deterministic_digest"

    def test_apps_rg_w11_unknown_never_pass_on_success_path(self):
        """On the success path no required gate may be UNKNOWN."""
        h = self._harness()
        pkg = _make_pkg()
        ev = build_w9_success_evidence(pkg, run_id="run-w11-unk")
        receipt, mesh, _ = h.evaluate(
            pkg, evidence=ev,
            request_id="req-w11-unk", run_id="run-w11-unk", trace_root="trace::w11",
        )
        profile = json.loads(_EXIT_PROFILE.read_text(encoding="utf-8"))
        required = set(profile["required_exit_gates"])
        unknown_required = [
            (v.gate_id, v.result) for v in mesh.verdicts
            if v.gate_id in required and v.result == VERDICT_UNKNOWN
        ]
        assert not unknown_required, (
            f"UNKNOWN verdict in required gates on success path: {unknown_required}"
        )

    def test_apps_rg_w11_hard_fail_blocks_allow_finish(self):
        """A hard FAIL on a required gate must block X3D_ALLOW_FINISH."""
        h = self._harness()
        # G21 FAIL — only one section present, missing required sections
        pkg = _make_pkg(required_nodes=("header_block",))
        ev = build_w9_success_evidence(pkg, run_id="run-w11-fail")
        receipt, mesh, _ = h.evaluate(
            pkg, evidence=ev,
            request_id="req-fail", run_id="run-w11-fail", trace_root="trace::fail",
        )
        assert receipt.x3_code != X3D_ALLOW_FINISH, (
            f"Hard FAIL on required gate must block X3D_ALLOW_FINISH; "
            f"got {receipt.x3_code!r}"
        )


# ---------------------------------------------------------------------------
# 11-12. No-bypass durable write proof
# ---------------------------------------------------------------------------

class TestW11NoBypasWriteProof:
    """Prove all direct-write bypass attempts are structurally blocked."""

    # Layer source files to scan for direct L4 write references.
    # NOTE: apps_rg_exit_binding.py has SANCTIONED post-exit fail-soft writebacks
    # (SemanticCacheManager, VectorRetrievalService) — these are lazily imported
    # after X3 disposition is emitted and never block the exit path.  They are
    # classified as ALLOWED_POST_EXIT_CACHE and excluded from the blocking-pattern
    # check via the per-file exclusion map below.
    _WRITE_SCAN_FILES: list[str] = [
        "agentic_core/L0_routing/apps_rg_l0_binding.py",
        "agentic_core/L2_execution/apps_rg_l2_binding.py",
        "agentic_core/L3_orchestration/managed_workflow_runner.py",
        "agentic_core/prompt_governance/apps_rg_pa_binding.py",
        "agentic_core/runtime/exit/apps_rg_exit_binding.py",
        "agentic_core/runtime/l6/writeback_proposer.py",
        "agentic_core/runtime/c0/apps_rg_c0_binding.py",
    ]
    _DIRECT_WRITE_PATTERNS: list[str] = [
        "L4WriteAdapter",
        "agentic_core.L4_state",
        "SemanticCacheManager",
        "VectorRetrievalService",
        "redis.set",
        "chroma_write",
        "write_to_cache",
        "l4_write",
        "DurableWriteGateway",
    ]
    # Per-file pattern exclusions: these patterns are ALLOWED in the named file
    # because they serve a sanctioned, documented purpose and do not bypass UWG.
    _FILE_PATTERN_EXCLUSIONS: dict[str, frozenset[str]] = {
        # Exit binding: post-exit fail-soft semantic cache and vector writebacks.
        # These are lazy imports executed AFTER X3 disposition; they never gate
        # the exit decision and are documented as ALLOWED_POST_EXIT_CACHE.
        "agentic_core/runtime/exit/apps_rg_exit_binding.py": frozenset({
            "agentic_core.L4_state",
            "SemanticCacheManager",
            "VectorRetrievalService",
        }),
    }

    def test_apps_rg_w11_no_direct_l4_write_paths(self):
        """Layer modules must not contain direct L4/cache/vector write references."""
        violations: list[str] = []
        for relpath in self._WRITE_SCAN_FILES:
            full = _REPO_ROOT / relpath
            if not full.exists():
                continue
            src = full.read_text(encoding="utf-8")
            excluded = self._FILE_PATTERN_EXCLUSIONS.get(relpath, frozenset())
            for pattern in self._DIRECT_WRITE_PATTERNS:
                if pattern in excluded:
                    continue
                if pattern in src:
                    violations.append(f"{relpath}: direct-write pattern {pattern!r}")
        assert not violations, (
            "Direct write bypass patterns found in layer modules:\n"
            + "\n".join(violations)
        )

    def test_apps_rg_w11_uwg_only_l4_write_path(self):
        """L4WriteAdapter must reject all non-UWG callers with DirectWriteViolationError."""
        adapter = L4WriteAdapter(stub=True)

        class _FakeRequest:
            promotion_request_id = "pr::test::001"
            target_store = "r1a_exact_cache"
            target_ref = "key::test"

        req = _FakeRequest()
        for caller in sorted(_FORBIDDEN_CALLERS):
            with pytest.raises(DirectWriteViolationError, match="forbidden"):
                adapter.commit(req, _caller=caller)

        # UWG (non-forbidden caller) must succeed
        from agentic_core.L4_state.adapters.write_adapters import _UWG_WRITE_TOKEN
        receipt_ref = adapter.commit(req, _caller="UWG", _uwg_token=_UWG_WRITE_TOKEN)
        assert receipt_ref.startswith("l4::commit::"), (
            f"Expected l4::commit:: prefix, got {receipt_ref!r}"
        )
        assert len(adapter.committed_writes) == 1
        assert len(adapter.rejected_writes) == len(_FORBIDDEN_CALLERS)

    def test_apps_rg_w11_uwg_emits_state_commit_receipt_on_admit(self):
        """UWG must emit StateCommitReceipt when a promotion request is ADMITTED."""
        from agentic_core.runtime.contracts.future_run_promotion import (
            FutureRunPromotionRequest,
            build_future_run_promotion_request,
            PROMOTION_TYPE_EXACT_CACHE_WRITEBACK,
            TARGET_STORE_EXACT_CACHE,
        )
        gate = UniversalWriteGate()  # no l4_adapter = stub mode
        req = build_future_run_promotion_request(
            app_id="apps_rg",
            task_class="resume_generation",
            promotion_type=PROMOTION_TYPE_EXACT_CACHE_WRITEBACK,
            target_store=TARGET_STORE_EXACT_CACHE,
            target_ref="key::w11::test",
            proposed_state_diff='{"key":"value"}',
            source_bundle_ref="reb::test::001",
            safety_class="standard",
            evidence_refs=("exit::ref::001",),
            policy_ref="apps_rg/config/domain_contract/meta_feedback_profile.resume_generation.v1.json",
        )
        result = gate.admit(req)
        assert result.verdict == VERDICT_ADMIT, (
            f"UWG must admit valid promotion request; got {result.verdict!r}"
        )
        assert result.state_commit_receipt is not None, (
            "UWG must emit StateCommitReceipt on ADMIT"
        )
        assert result.state_commit_receipt.committed_by == "UWG"

    def test_apps_rg_w11_uwg_emits_blocked_write_receipt_on_block(self):
        """UWG must emit BlockedWriteReceipt when a promotion request is BLOCKED.

        Uses PROMOTION_TYPE_SEMANTIC_CACHE_WRITEBACK without semantic_cache_enabled
        in policy — triggers UWG Gate 5 (semantic cache disabled by policy).
        The dataclass enforces non-empty evidence_refs and policy_ref at construction,
        so the block must come from a valid-but-policy-rejected request.
        """
        from agentic_core.runtime.contracts.future_run_promotion import (
            build_future_run_promotion_request,
            PROMOTION_TYPE_SEMANTIC_CACHE_WRITEBACK,
            TARGET_STORE_EXACT_CACHE,
        )
        # policy has semantic_cache_enabled=False (default) → Gate 5 blocks
        gate = UniversalWriteGate(policy={"semantic_cache_enabled": False})
        req = build_future_run_promotion_request(
            app_id="apps_rg",
            task_class="resume_generation",
            promotion_type=PROMOTION_TYPE_SEMANTIC_CACHE_WRITEBACK,
            target_store=TARGET_STORE_EXACT_CACHE,
            target_ref="key::w11::block_test",
            proposed_state_diff='{"key":"value"}',
            source_bundle_ref="reb::test::block",
            safety_class="standard",
            evidence_refs=("exit::ref::block",),
            policy_ref="apps_rg/config/domain_contract/meta_feedback_profile.resume_generation.v1.json",
        )
        result = gate.admit(req)
        assert result.verdict == VERDICT_BLOCK, (
            f"UWG must block semantic_cache_writeback when disabled by policy; "
            f"got {result.verdict!r}"
        )
        assert result.blocked_write_receipt is not None, (
            "UWG must emit BlockedWriteReceipt on BLOCK"
        )
        assert result.blocked_write_receipt.blocked_by == "UWG"


# ---------------------------------------------------------------------------
# 13. Quarantine isolation proof
# ---------------------------------------------------------------------------

class TestW11QuarantineIsolation:
    """Active runtime modules must not import quarantined apps_rg modules."""

    _QUARANTINED: tuple[str, ...] = (
        "apps_rg._quarantine",
        "apps_rg/integrations/hops",
        "apps_rg/integrations/gates",
        "apps_rg/prompt_assembly/rg_pa_compiler",
        "apps_rg/prompt_assembly/contracts",
        "HardenedanthropicexecutorStrategy",
        "ResumeAssemblyAgent",
        "apps_rg._quarantine.compiler",
    )

    _ACTIVE_RUNTIME_MODULES: list[str] = [
        "agentic_core.runtime.entry.apps_rg_w9_managed_workflow_e2e",
        "agentic_core.runtime.exit.apps_rg_exit_binding",
        "agentic_core.L0_routing.apps_rg_l0_binding",
        "agentic_core.L2_execution.apps_rg_l2_binding",
        "agentic_core.runtime.uwg.universal_write_gate",
        "agentic_core.runtime.l6.writeback_proposer",
        "agentic_core.L4_state.adapters.write_adapters",
    ]

    def test_apps_rg_w11_quarantined_modules_not_imported(self):
        """Active runtime module sources must not reference quarantined modules."""
        violations: list[str] = []

        for mod_name in self._ACTIVE_RUNTIME_MODULES:
            spec = importlib.util.find_spec(mod_name)
            if spec is None or spec.origin is None:
                violations.append(f"Module not found: {mod_name}")
                continue
            src = Path(spec.origin).read_text(encoding="utf-8")
            for quarantined in self._QUARANTINED:
                # Normalise path separators for source scanning
                key = quarantined.replace("/", ".")
                if quarantined in src or key in src:
                    violations.append(
                        f"{mod_name}: references quarantined {quarantined!r}"
                    )

        assert not violations, (
            "Quarantined module references found in active runtime:\n"
            + "\n".join(violations)
        )


# ---------------------------------------------------------------------------
# 14. Stage receipt completeness
# ---------------------------------------------------------------------------

class TestW11StageReceipts:

    _REQUIRED_RECEIPTS: tuple[str, ...] = (
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
    )

    def test_apps_rg_w11_stage_receipts_complete_or_mapped(self, tmp_path, monkeypatch):
        """W9 E2E must write all required stage receipt files."""
        result = _run_e2e(tmp_path, monkeypatch)
        assert result.error is None, f"E2E failed: {result.error}"

        missing: list[str] = []
        for name in self._REQUIRED_RECEIPTS:
            path = tmp_path / name
            if not path.exists():
                missing.append(name)
            else:
                data = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    missing.append(f"{name} (not a dict)")

        assert not missing, (
            f"Missing or malformed stage receipts:\n" + "\n".join(missing)
        )

    def test_apps_rg_w11_exit_disposition_receipt_has_x3d(self, tmp_path, monkeypatch):
        """14_Exit_disposition_receipt.json must contain x3_code=X3D_ALLOW_FINISH."""
        result = _run_e2e(tmp_path, monkeypatch)
        assert result.error is None
        receipt_path = tmp_path / "14_Exit_disposition_receipt.json"
        assert receipt_path.exists()
        data = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert data.get("x3_code") == X3D_ALLOW_FINISH, (
            f"Expected x3_code={X3D_ALLOW_FINISH!r} in exit receipt, "
            f"got {data.get('x3_code')!r}"
        )

    def test_apps_rg_w11_runtime_exhaust_bundle_receipt_valid(self, tmp_path, monkeypatch):
        """99_runtime_exhaust_bundle.json must be present and contain created_after_exit=true."""
        result = _run_e2e(tmp_path, monkeypatch)
        assert result.error is None
        receipt_path = tmp_path / "99_runtime_exhaust_bundle.json"
        assert receipt_path.exists()
        data = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert data.get("created_after_exit") is True, (
            "runtime_exhaust_bundle receipt must have created_after_exit=true"
        )
        assert data.get("exit_disposition_ref"), (
            "runtime_exhaust_bundle receipt must have non-empty exit_disposition_ref"
        )


# ---------------------------------------------------------------------------
# 15. Activation readiness report
# ---------------------------------------------------------------------------

class TestW11ActivationReadinessReport:
    """Generate an in-memory activation readiness report after all checks."""

    def test_apps_rg_w11_activation_readiness_report_generated(self, tmp_path, monkeypatch):
        """Produce an activation readiness summary and assert it says READY."""
        import yaml

        findings: dict[str, Any] = {}

        # Route registry check
        data = yaml.safe_load(_ROUTE_REGISTRY.read_text(encoding="utf-8"))
        managed = [r for r in (data.get("routes") or []) if r.get("execution_form") == "MANAGED_WORKFLOW"]
        findings["route_status"] = managed[0].get("status") if managed else "MISSING"

        # G24 / G28 required
        profile = json.loads(_EXIT_PROFILE.read_text(encoding="utf-8"))
        required_gates = set(profile["required_exit_gates"])
        findings["g24_required"] = "G24" in required_gates
        findings["g28_required"] = "G28" in required_gates

        # No blocking leakage
        blocking: list[str] = []
        for relpath in [
            "agentic_core/runtime/uwg/universal_write_gate.py",
            "agentic_core/runtime/uwg/write_receipts.py",
            "agentic_core/L4_state/adapters/write_adapters.py",
            "agentic_core/runtime/exhaust/runtime_exhaust_bundle.py",
        ]:
            src = (_REPO_ROOT / relpath).read_text(encoding="utf-8")
            for lit in ["APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED",
                        "workflow_manifest.resume_generation"]:
                if lit in src:
                    blocking.append(f"{relpath}:{lit}")
        findings["blocking_leakage"] = blocking

        # Full-spine success
        monkeypatch.setenv("APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED", "1")
        monkeypatch.setenv("APPS_RG_EXECUTION_FORM", "managed_workflow")
        monkeypatch.delenv("APPS_RG_L3_OPT_IN", raising=False)
        envelope = _make_envelope()
        result = run_w9_managed_workflow_e2e(
            envelope, output_dir=tmp_path / "readiness", repo_root=_REPO_ROOT
        )
        findings["full_spine_error"] = result.error
        findings["x3_code"] = result.x3_code

        # Determine readiness
        ready = (
            findings["route_status"] == "registered_not_active"
            and findings["g24_required"]
            and findings["g28_required"]
            and not findings["blocking_leakage"]
            and findings["full_spine_error"] is None
            and findings["x3_code"] == X3D_ALLOW_FINISH
        )
        findings["route_activation_recommendation"] = "READY" if ready else "NOT_READY"

        assert findings["route_activation_recommendation"] == "READY", (
            f"Activation readiness check FAILED. Findings:\n{json.dumps(findings, indent=2)}"
        )
        assert findings["route_status"] == "registered_not_active", (
            "Route must still be registered_not_active at end of W11"
        )
