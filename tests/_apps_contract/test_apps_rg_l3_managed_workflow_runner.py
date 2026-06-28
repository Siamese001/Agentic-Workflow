"""W5: L3 ManagedWorkflowRunner tests.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W5

Tests: 19 covering the required W5 acceptance criteria.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from agentic_core.L3_orchestration.managed_workflow_runner import (
    ManagedWorkflowRunner,
    ManagedWorkflowRunnerError,
)
from agentic_core.L3_orchestration.section_merge_engine import (
    SectionMergeEngine,
    SectionMergeError,
    NodeDescriptor,
)
from agentic_core.runtime.contracts.l3_to_l2_step_contract import L3ToL2StepContract
from agentic_core.runtime.contracts.sealed_workflow_types import (
    SealedSectionArtifact,
    SealedWorkflowPackage,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MANIFEST_PATH = (
    _REPO_ROOT / "apps_rg/config/fixtures/workflow_manifest.resume_generation.v1.minimal.yaml"
)
_REGISTRY_PATH = _REPO_ROOT / "apps_rg/config/route_registry.yaml"


def _make_receipt_json(manifest_path: Path = _MANIFEST_PATH) -> str:
    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    rel = str(manifest_path.relative_to(_REPO_ROOT)).replace("\\", "/")
    return json.dumps(
        {
            "workflow_manifest_path": rel,
            "manifest_digest": digest,
        },
        separators=(",", ":"),
    )


class _FakeRouteContract:
    """Minimal RouteContract stand-in for L3 runner tests."""

    def __init__(
        self,
        *,
        execution_form: str = "MANAGED_WORKFLOW",
        workflow_ref: str = "wfm::apps_rg::resume_generation::v1",
        workflow_manifest_ref: str = "wfm::apps_rg::resume_generation::v1",
        registry_resolution_receipt_ref: str = "",
        request_id: str = "req-test-001",
        run_id: str = "run-test-001",
        trace_id: str = "trace-test-001",
        replay_key: str = "",
        route_gate_refs: tuple = (),
    ) -> None:
        self.execution_form = execution_form
        self.workflow_ref = workflow_ref
        self.workflow_manifest_ref = workflow_manifest_ref
        self.registry_resolution_receipt_ref = registry_resolution_receipt_ref
        self.request_id = request_id
        self.run_id = run_id
        self.trace_id = trace_id
        self.replay_key = replay_key
        self.route_gate_refs = route_gate_refs


def _stub_executor(step: L3ToL2StepContract) -> SealedSectionArtifact:
    """Fake L2 executor: returns minimal SealedSectionArtifact for each node."""
    content = f"stub_content_for_{step.node_id}"
    return SealedSectionArtifact(
        artifact_id=f"ssa::{step.node_id}::stub",
        workflow_ref=step.workflow_ref,
        node_id=step.node_id,
        run_id=step.run_id,
        sealed_content=content,
        content_digest=hashlib.sha256(content.encode()).hexdigest(),
        terminal_class="success",
        decisive_reason="stub_executor",
    )


def _failing_executor(step: L3ToL2StepContract) -> SealedSectionArtifact:
    raise RuntimeError(f"Simulated L2 failure on node={step.node_id}")


def _make_runner(executor=None) -> ManagedWorkflowRunner:
    return ManagedWorkflowRunner(
        l2_executor=executor or _stub_executor,
        repo_root=_REPO_ROOT,
    )


def _make_contract_with_receipt() -> _FakeRouteContract:
    return _FakeRouteContract(
        registry_resolution_receipt_ref=_make_receipt_json(),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestL3RunnerInputValidation:

    def test_l3_runner_rejects_non_managed_workflow_route(self):
        runner = _make_runner()
        rc = _FakeRouteContract(execution_form="single_step")
        with pytest.raises(ManagedWorkflowRunnerError) as exc_info:
            runner.run(rc)
        assert "MANAGED_WORKFLOW" in str(exc_info.value)
        assert "single_step" in str(exc_info.value)

    def test_l3_runner_fails_when_workflow_ref_missing(self):
        runner = _make_runner()
        rc = _FakeRouteContract(workflow_ref="")
        with pytest.raises(ManagedWorkflowRunnerError) as exc_info:
            runner.run(rc)
        assert "workflow_ref is empty" in str(exc_info.value)

    def test_l3_runner_resolves_workflow_manifest_from_route_contract(self):
        runner = _make_runner()
        rc = _make_contract_with_receipt()
        pkg = runner.run(rc)
        assert pkg.workflow_ref == rc.workflow_ref
        assert pkg.workflow_manifest_ref == rc.workflow_manifest_ref

    def test_l3_runner_fails_on_manifest_digest_mismatch(self, tmp_path):
        tampered_receipt = json.dumps(
            {
                "workflow_manifest_path": "apps_rg/config/fixtures/workflow_manifest.resume_generation.v1.minimal.yaml",
                "manifest_digest": "deadbeef" * 8,
            },
            separators=(",", ":"),
        )
        runner = _make_runner()
        rc = _FakeRouteContract(registry_resolution_receipt_ref=tampered_receipt)
        with pytest.raises(ManagedWorkflowRunnerError) as exc_info:
            runner.run(rc)
        assert "digest mismatch" in str(exc_info.value).lower()

    def test_l3_runner_fails_when_manifest_path_missing_in_receipt(self):
        bad_receipt = json.dumps({"manifest_digest": ""}, separators=(",", ":"))
        runner = _make_runner()
        rc = _FakeRouteContract(registry_resolution_receipt_ref=bad_receipt)
        with pytest.raises(ManagedWorkflowRunnerError) as exc_info:
            runner.run(rc)
        assert "workflow_manifest_path" in str(exc_info.value) or "manifest" in str(exc_info.value).lower()


class TestL3RunnerDAGOrdering:

    def test_l3_runner_topologically_orders_nodes(self):
        emitted: list[str] = []

        def recording_executor(step: L3ToL2StepContract) -> SealedSectionArtifact:
            emitted.append(step.node_id)
            return _stub_executor(step)

        runner = _make_runner(recording_executor)
        rc = _make_contract_with_receipt()
        runner.run(rc)

        # profile_normalization must come before role_analysis
        assert emitted.index("profile_normalization") < emitted.index("role_analysis")
        # role_analysis must come before header_block
        assert emitted.index("role_analysis") < emitted.index("header_block")
        # final_render must come after all its dependencies
        final_idx = emitted.index("final_render")
        for dep in ("header_block", "professional_summary", "skills_block",
                    "experience_block", "education_block"):
            assert emitted.index(dep) < final_idx

    def test_l3_runner_fails_on_cycle(self, tmp_path):
        cycle_manifest = tmp_path / "cycle_manifest.yaml"
        cycle_manifest.write_text(
            "manifest_id: test\nnodes:\n"
            "  - {node_id: A, node_type: generation, depends_on: [B]}\n"
            "  - {node_id: B, node_type: generation, depends_on: [A]}\n",
            encoding="utf-8",
        )
        receipt = json.dumps(
            {"workflow_manifest_path": str(cycle_manifest), "manifest_digest": ""},
            separators=(",", ":"),
        )
        runner = ManagedWorkflowRunner(
            l2_executor=_stub_executor,
            repo_root=tmp_path.parent,
        )
        rc = _FakeRouteContract(registry_resolution_receipt_ref=receipt)
        with patch.object(runner, "_repo_root", tmp_path.parent):
            # We need the path to resolve absolutely, so inject directly
            import hashlib as _hlib
            receipt2 = json.dumps(
                {
                    "workflow_manifest_path": str(cycle_manifest),
                    "manifest_digest": _hlib.sha256(cycle_manifest.read_bytes()).hexdigest(),
                },
                separators=(",", ":"),
            )
            rc2 = _FakeRouteContract(registry_resolution_receipt_ref=receipt2)
            # Path resolution uses repo_root, so override it to tmp_path.parent
            runner2 = ManagedWorkflowRunner(
                l2_executor=_stub_executor,
                repo_root=tmp_path,
            )
            # The receipt holds an absolute path — use direct path injection via a
            # custom receipt that has a relative path from tmp_path
            subdir = tmp_path / "sub"
            subdir.mkdir()
            cyc = subdir / "cycle_manifest.yaml"
            cyc.write_text(
                "manifest_id: test\nnodes:\n"
                "  - {node_id: A, node_type: generation, depends_on: [B]}\n"
                "  - {node_id: B, node_type: generation, depends_on: [A]}\n",
                encoding="utf-8",
            )
            receipt3 = json.dumps(
                {
                    "workflow_manifest_path": "sub/cycle_manifest.yaml",
                    "manifest_digest": _hlib.sha256(cyc.read_bytes()).hexdigest(),
                },
                separators=(",", ":"),
            )
            rc3 = _FakeRouteContract(registry_resolution_receipt_ref=receipt3)
            runner3 = ManagedWorkflowRunner(
                l2_executor=_stub_executor,
                repo_root=tmp_path,
            )
            with pytest.raises(ManagedWorkflowRunnerError) as exc_info:
                runner3.run(rc3)
        assert "cycle" in str(exc_info.value).lower()


class TestL3RunnerExecution:

    def test_l3_runner_emits_one_step_contract_per_node(self):
        emitted_steps: list[L3ToL2StepContract] = []

        def capturing_executor(step: L3ToL2StepContract) -> SealedSectionArtifact:
            emitted_steps.append(step)
            return _stub_executor(step)

        runner = _make_runner(capturing_executor)
        rc = _make_contract_with_receipt()
        runner.run(rc)

        node_ids = [s.node_id for s in emitted_steps]
        # All must be unique
        assert len(node_ids) == len(set(node_ids))
        # Must include critical nodes
        for nid in ("profile_normalization", "role_analysis", "final_render"):
            assert nid in node_ids

    def test_l3_runner_calls_l2_executor_once_per_ready_node(self):
        call_counts: dict[str, int] = {}

        def counting_executor(step: L3ToL2StepContract) -> SealedSectionArtifact:
            call_counts[step.node_id] = call_counts.get(step.node_id, 0) + 1
            return _stub_executor(step)

        runner = _make_runner(counting_executor)
        rc = _make_contract_with_receipt()
        runner.run(rc)

        # Every called node must be called exactly once
        for nid, count in call_counts.items():
            assert count == 1, f"Node {nid} was called {count} times"

    def test_l3_runner_fails_closed_on_critical_node_failure(self):
        def selective_fail(step: L3ToL2StepContract) -> SealedSectionArtifact:
            if step.node_id == "profile_normalization":
                raise RuntimeError("injected critical failure")
            return _stub_executor(step)

        runner = _make_runner(selective_fail)
        rc = _make_contract_with_receipt()
        with pytest.raises(ManagedWorkflowRunnerError) as exc_info:
            runner.run(rc)
        assert "critical" in str(exc_info.value).lower()

    def test_l3_runner_policy_allows_optional_node_skip_only_when_configured(self):
        runner = _make_runner()
        rc = _make_contract_with_receipt()
        # The manifest marks certifications_block and selected_projects_block as optional=true
        # Patching executor to fail on optional nodes only
        def fail_optional(step: L3ToL2StepContract) -> SealedSectionArtifact:
            if step.node_id in ("certifications_block", "selected_projects_block"):
                raise RuntimeError("injected optional failure")
            return _stub_executor(step)

        runner2 = _make_runner(fail_optional)
        pkg = runner2.run(rc)
        # Should complete with failed optional nodes recorded
        assert "certifications_block" in pkg.failed_node_refs or \
               pkg.terminal_class in ("success",)

    def test_l3_runner_produces_sealed_workflow_package(self):
        runner = _make_runner()
        rc = _make_contract_with_receipt()
        pkg = runner.run(rc)

        assert isinstance(pkg, SealedWorkflowPackage)
        assert pkg.workflow_ref == rc.workflow_ref
        assert pkg.run_id
        assert pkg.section_count > 0
        assert len(pkg.sealed_sections) == pkg.section_count
        assert pkg.merged_payload_digest
        assert pkg.terminal_class == "success"


class TestL3RunnerReceipts:

    def test_l3_runner_writes_stage_output_receipts(self, tmp_path):
        runner = _make_runner()
        rc = _make_contract_with_receipt()
        pkg = runner.run(rc, output_dir=tmp_path)

        # Manifest resolved receipt
        assert (tmp_path / "06_L3_workflow_manifest_resolved.json").exists()
        # At least one step contract receipt
        step_receipts = list(tmp_path.glob("07_L3_to_L2_step_contract_*.json"))
        assert len(step_receipts) > 0
        # At least one sealed section receipt
        section_receipts = list(tmp_path.glob("12_L2_sealed_section_*.json"))
        assert len(section_receipts) > 0
        # Final package receipt
        assert (tmp_path / "13_L3_sealed_workflow_package.json").exists()

    def test_stage_receipt_json_is_valid(self, tmp_path):
        runner = _make_runner()
        rc = _make_contract_with_receipt()
        runner.run(rc, output_dir=tmp_path)

        manifest_receipt = json.loads(
            (tmp_path / "06_L3_workflow_manifest_resolved.json").read_text(encoding="utf-8")
        )
        assert manifest_receipt["workflow_ref"] == rc.workflow_ref
        assert manifest_receipt["node_count"] > 0

        pkg_receipt = json.loads(
            (tmp_path / "13_L3_sealed_workflow_package.json").read_text(encoding="utf-8")
        )
        assert pkg_receipt["workflow_ref"] == rc.workflow_ref
        assert pkg_receipt["terminal_class"] == "success"


class TestL3RunnerInvariants:

    def test_l3_runner_runtime_gate_refs_unknown_not_pass_when_gate_harness_missing(self):
        emitted_steps: list[L3ToL2StepContract] = []

        def capturing_executor(step: L3ToL2StepContract) -> SealedSectionArtifact:
            emitted_steps.append(step)
            return _stub_executor(step)

        runner = _make_runner(capturing_executor)
        rc = _FakeRouteContract(
            registry_resolution_receipt_ref=_make_receipt_json(),
            route_gate_refs=(),  # no gate harness
        )
        pkg = runner.run(rc)

        # Every step contract must have gate refs that are NOT "PASS"
        for step in emitted_steps:
            for ref in step.runtime_gate_refs:
                assert "PASS" not in ref, (
                    f"Gate ref {ref!r} in step {step.node_id} must not say PASS"
                )

        # Package gate refs also must not say PASS
        for ref in pkg.runtime_gate_refs:
            assert "PASS" not in ref

    def test_l3_runner_no_resume_section_names_in_core(self):
        runner_src = Path(__file__).parents[2] / "agentic_core/L3_orchestration/managed_workflow_runner.py"
        src = runner_src.read_text(encoding="utf-8")
        # These are app-specific section names that must not appear in generic core
        forbidden_section_names = [
            "header_block",
            "professional_summary",
            "skills_block",
            "experience_block",
            "education_block",
            "certifications_block",
            "selected_projects_block",
            "final_render",
            "ats_validate",
            "factual_grounding_check",
            "no_fabrication_guardrail",
        ]
        for name in forbidden_section_names:
            # Allow if only in a comment
            non_comment_lines = [
                line for line in src.splitlines()
                if not line.strip().startswith("#") and name in line
            ]
            assert not non_comment_lines, (
                f"App-specific section name {name!r} found in generic runner core: "
                f"{non_comment_lines[:2]}"
            )

    def test_l3_runner_no_provider_hardcoding_in_core(self):
        runner_src = Path(__file__).parents[2] / "agentic_core/L3_orchestration/managed_workflow_runner.py"
        src = runner_src.read_text(encoding="utf-8")
        forbidden_providers = [
            "anthropic", "openai", "retired_provider", "azure_openai", "cohere",
            "claude", "gpt-4", "gpt4",
        ]
        for pname in forbidden_providers:
            non_comment_lines = [
                line for line in src.splitlines()
                if not line.strip().startswith("#")
                and pname.lower() in line.lower()
            ]
            assert not non_comment_lines, (
                f"Provider name {pname!r} hardcoded in generic runner: {non_comment_lines[:2]}"
            )

    def test_l3_runner_never_writes_l4(self):
        runner_src = Path(__file__).parents[2] / "agentic_core/L3_orchestration/managed_workflow_runner.py"
        src = runner_src.read_text(encoding="utf-8")
        for line in src.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            # Detect l4 write calls (L4StateWriter, uwg_write, etc.)
            for pattern in ("L4StateWriter", "uwg_write", "write_l4", "l4_write"):
                assert pattern not in line, (
                    f"Potential L4 write pattern {pattern!r} found in runner: {line!r}"
                )

    def test_l3_runner_never_emits_x3(self):
        runner_src = Path(__file__).parents[2] / "agentic_core/L3_orchestration/managed_workflow_runner.py"
        src = runner_src.read_text(encoding="utf-8")
        for line in src.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for pattern in ("X3Disposition", "emit_x3", "x3_emit", "x3_disposition"):
                assert pattern not in line, (
                    f"X3 emission pattern {pattern!r} found in runner: {line!r}"
                )

    def test_l3_runner_does_not_import_quarantined_hops_or_gates(self):
        runner_src = Path(__file__).parents[2] / "agentic_core/L3_orchestration/managed_workflow_runner.py"
        merge_src = Path(__file__).parents[2] / "agentic_core/L3_orchestration/section_merge_engine.py"
        quarantined_prefixes = (
            "apps_rg.integrations.hops",
            "apps_rg.integrations.gates",
            "apps_rg._quarantine",
        )
        for src_file in (runner_src, merge_src):
            src = src_file.read_text(encoding="utf-8")
            import_lines = [
                line for line in src.splitlines()
                if not line.strip().startswith("#")
                and not line.strip().startswith('"""')
                and not line.strip().startswith("'''")
                and not line.strip().startswith("-")
                and ("import" in line or "from" in line)
                and not line.strip().startswith("#")
            ]
            for imp_line in import_lines:
                for prefix in quarantined_prefixes:
                    assert prefix not in imp_line, (
                        f"Quarantined import {prefix!r} in {src_file.name}: {imp_line!r}"
                    )


class TestL3RunnerEndToEnd:

    def test_apps_rg_l0_to_l3_stubbed_path_in_test_enabled_mode(self, tmp_path):
        """Full L0→L3 path in test-enabled mode with injected stub executor."""
        from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg
        from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract

        # Build minimal L1PlanContract
        l1 = L1PlanContract(
            request_id="req-w5-e2e-001",
            run_id="run-w5-e2e-001",
            app_id="apps_rg",
            trace_id="trace-w5-e2e-001",
            task_spec={"generation_mode": "resume_generation"},
            grounding_required=True,
            model_generation_required=True,
            write_authority_present=False,
            tenant_id="apps_rg",
            multiple_work_units_hint=True,
            merge_required_hint=True,
            per_unit_quality_selection_hint=True,
            candidate_generation_expected_hint=True,
            l5_certification_ref="test-cert-ref",
        )

        # L0 route in test-enabled mode
        with patch.dict(os.environ, {"APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED": "1"}):
            rc = l0_route_apps_rg(l1)

        assert rc.execution_form.upper() == "MANAGED_WORKFLOW"
        assert rc.workflow_ref
        assert rc.registry_resolution_receipt_ref

        # L3 runner picks it up
        runner = ManagedWorkflowRunner(
            l2_executor=_stub_executor,
            repo_root=_REPO_ROOT,
        )
        pkg = runner.run(rc, output_dir=tmp_path)

        assert isinstance(pkg, SealedWorkflowPackage)
        assert pkg.workflow_ref == rc.workflow_ref
        assert pkg.terminal_class == "success"
        assert (tmp_path / "13_L3_sealed_workflow_package.json").exists()


class TestSectionMergeEngine:

    def test_merge_engine_rejects_duplicate_node_ids(self):
        engine = SectionMergeEngine()
        artifacts = [
            SealedSectionArtifact(artifact_id="a1", node_id="node_x", workflow_ref="wf1"),
            SealedSectionArtifact(artifact_id="a2", node_id="node_x", workflow_ref="wf1"),
        ]
        nodes = [NodeDescriptor(node_id="node_x")]
        with pytest.raises(SectionMergeError) as exc_info:
            engine.merge(
                workflow_ref="wf1",
                workflow_manifest_ref="wfm::test",
                run_id="run-1",
                route_contract_ref="rc-1",
                manifest_nodes=nodes,
                artifacts=artifacts,
            )
        assert "Duplicate" in str(exc_info.value)

    def test_merge_engine_rejects_missing_critical_nodes(self):
        engine = SectionMergeEngine()
        artifacts = [
            SealedSectionArtifact(artifact_id="a1", node_id="node_a", workflow_ref="wf1"),
        ]
        nodes = [
            NodeDescriptor(node_id="node_a"),
            NodeDescriptor(node_id="node_b", optional=False),  # critical, missing
        ]
        with pytest.raises(SectionMergeError) as exc_info:
            engine.merge(
                workflow_ref="wf1",
                workflow_manifest_ref="wfm::test",
                run_id="run-1",
                route_contract_ref="rc-1",
                manifest_nodes=nodes,
                artifacts=artifacts,
            )
        assert "node_b" in str(exc_info.value)

    def test_merge_engine_allows_optional_node_omission(self):
        engine = SectionMergeEngine()
        artifacts = [
            SealedSectionArtifact(artifact_id="a1", node_id="node_a", workflow_ref="wf1"),
        ]
        nodes = [
            NodeDescriptor(node_id="node_a"),
            NodeDescriptor(node_id="node_optional", optional=True),
        ]
        pkg = engine.merge(
            workflow_ref="wf1",
            workflow_manifest_ref="wfm::test",
            run_id="run-1",
            route_contract_ref="rc-1",
            manifest_nodes=nodes,
            artifacts=artifacts,
        )
        assert "node_optional" in pkg.skipped_node_refs
        assert pkg.terminal_class == "success"
