"""Unit tests for apps_shared.spine_emission (W1 scaffolding)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_shared.spine_emission import (
    EmissionConfig,
    GovernedRun,
    StageTracer,
    governed_run,
)
from apps_shared.spine_emission.contracts import (
    C0GroundingReceipt,
    ExitReviewPacket,
    L1PlanContract,
    L1PlanStep,
    L2ExecutionReceipt,
    L3BypassReceipt,
    L3OrchestrationReceipt,
    PromptAssemblyManifest,
    RouteContract,
    RuntimeExhaustBundle,
    U0IntakeEnvelope,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_route_registry(path: Path, *, execution_form: str, l3_required: bool,
                        static_dag_ref: str | None = None) -> None:
    body = f"""app_name: apps_test
schema_version: "apps_test.route_registry/v1"
routes:
  - route_id: apps_test.default_v1
    execution_form: {execution_form}
    l3_required: {"true" if l3_required else "false"}
    selected_capability: apps_test.default_v1
"""
    if static_dag_ref:
        body += f"    static_dag_ref: {static_dag_ref}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _make_l3_dag(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "dag_id: apps_test.static_l3\nversion: v1\nnodes: []\nedges: []\n",
        encoding="utf-8",
    )


@pytest.fixture
def bypass_cfg(tmp_path: Path) -> EmissionConfig:
    route_registry = tmp_path / "config" / "route_registry.yaml"
    _make_route_registry(route_registry, execution_form="SINGLE_STEP", l3_required=False)
    return EmissionConfig(
        app_name="apps_test",
        entrypoint_command="python -m apps_test",
        runs_root=tmp_path / "artifacts" / "apps_test" / "runs",
        route_registry_path=route_registry,
        l3_dag_path=None,
        plan_steps=[L1PlanStep(step_id="s0", name="step0", kind="ingest")],
        plan_rationale="test rationale",
        expects_c0_grounding=False,
        expects_prompt_assembly=False,
        expects_static_dag=False,
        expected_execution_form="SINGLE_STEP",
        expected_l3_path="BYPASSED",
        repo_root=tmp_path,
    )


@pytest.fixture
def managed_workflow_cfg(tmp_path: Path) -> EmissionConfig:
    route_registry = tmp_path / "config" / "route_registry.yaml"
    _make_route_registry(
        route_registry, execution_form="MANAGED_WORKFLOW", l3_required=True,
        static_dag_ref="config/l3_dag.yaml",
    )
    l3_dag = tmp_path / "config" / "l3_dag.yaml"
    _make_l3_dag(l3_dag)
    return EmissionConfig(
        app_name="apps_test_mw",
        entrypoint_command="python -m apps_test_mw",
        runs_root=tmp_path / "artifacts" / "apps_test_mw" / "runs",
        route_registry_path=route_registry,
        l3_dag_path=l3_dag,
        plan_steps=[
            L1PlanStep(step_id="hop_0", name="hop0", kind="ingest"),
            L1PlanStep(step_id="hop_1", name="hop1", kind="transform"),
        ],
        plan_rationale="managed workflow test",
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_static_dag=True,
        expected_execution_form="MANAGED_WORKFLOW",
        expected_l3_path="RAN",
        repo_root=tmp_path,
    )


# ---------------------------------------------------------------------------
# Test 1-5: contract type round-trip (pydantic validation)
# ---------------------------------------------------------------------------


class TestContractTypes:
    def _base(self) -> dict:
        return {"app_name": "apps_test", "run_id": "r", "request_id": "r", "trace_root": "r"}

    def test_u0_intake_envelope(self):
        v = U0IntakeEnvelope(**self._base(), intake_id="i",
                             entrypoint_command="python -m apps_test",
                             cli_args_digest="x" * 64, user_intent="test")
        assert v.app_name == "apps_test"

    def test_l1_plan_contract(self):
        v = L1PlanContract(**self._base(), plan_id="p",
                           steps=[L1PlanStep(step_id="s", name="n", kind="ingest")],
                           plan_rationale="r")
        assert v.grounding_required is False

    def test_route_contract(self):
        v = RouteContract(**self._base(), route_contract_id="rc", route_id="r",
                          execution_form="SINGLE_STEP", route_reason="x",
                          l3_required=False, selected_capability="c")
        assert v.execution_form == "SINGLE_STEP"

    def test_l3_bypass_receipt(self):
        v = L3BypassReceipt(**self._base(), l3_bypass_receipt_id="b",
                            route_contract_id="rc", execution_form="SINGLE_STEP",
                            l3_bypass_reason="NO_MANAGED_WORKFLOW_REQUIRED",
                            static_dag_available=False, why_static_dag_not_used="n/a")
        assert v.l3_required is False

    def test_l3_orchestration_receipt(self):
        v = L3OrchestrationReceipt(**self._base(), l3_runtime_receipt_id="rr",
                                    route_contract_id="rc", dag_id="d",
                                    dag_sha256="a" * 64, static_dag_hash="a" * 64,
                                    workflow_id="w", selected_entry_node="n0",
                                    node_count=1, scheduled_node_ids=["n0"],
                                    ready_node_ids=["n0"], step_contract_refs=[])
        assert v.dag_sha256 == v.static_dag_hash  # N6 binding

    def test_c0_grounding_receipt(self):
        v = C0GroundingReceipt(**self._base(), c0_grounding_receipt_id="c",
                               route_contract_id="rc", retrieval_plan_id="rp",
                               retrieval_backend="deterministic_fixture",
                               evidence_count=0)
        assert v.deterministic is True

    def test_prompt_assembly_manifest(self):
        v = PromptAssemblyManifest(**self._base(), prompt_assembly_manifest_id="pa",
                                   route_contract_id="rc", assembly_note="x")
        assert v.assembly_strategy == "deterministic_template"


# ---------------------------------------------------------------------------
# Test 6-7: StageTracer
# ---------------------------------------------------------------------------


class TestStageTracer:
    def test_empty_trace_seals_cleanly(self):
        t = StageTracer("apps_test", "run", "req", "tr")
        trace = t.seal()
        assert trace.span_count == 0
        assert trace.contains_synthetic_spans is False

    def test_span_records_monotonic_duration(self):
        t = StageTracer("apps_test", "run", "req", "tr")
        with t.span("stage_a", key="v"):
            pass
        trace = t.seal()
        assert trace.span_count == 1
        assert trace.spans[0].is_synthetic is False
        assert trace.spans[0].duration_ms >= 0


# ---------------------------------------------------------------------------
# Test 8-11: GovernedRun (bypass path) end-to-end
# ---------------------------------------------------------------------------


class TestGovernedRunBypass:
    def test_pre_and_post_emit_all_expected_files(self, bypass_cfg: EmissionConfig):
        with governed_run(bypass_cfg, cli_args=["--flag"]) as gr:
            with gr.span("L2_execute"):
                pass
            gr.set_subprocess_exit_code(0)
        files = {p.name for p in gr.run_dir.iterdir()}
        assert "u0_intake_envelope.json" in files
        assert "l1_plan_contract.json" in files
        assert "route_contract.json" in files
        assert "l3_bypass_receipt.json" in files  # bypass, not orchestration
        assert "l3_orchestration_receipt.json" not in files
        assert "l2_execution_receipt.json" in files
        assert "exit_review_packet.json" in files
        assert "runtime_exhaust_bundle.json" in files
        assert "otel_runtime_trace.json" in files
        # C0 + Prompt NOT emitted when expects_* are False
        assert "final_evidence_contract.json" not in files
        assert "prompt_assembly_manifest.json" not in files

    def test_run_id_threaded_across_all_receipts(self, bypass_cfg: EmissionConfig):
        with governed_run(bypass_cfg, cli_args=[]) as gr:
            with gr.span("noop"):
                pass
        expected_run_id = gr.run_id
        for fname in (
            "u0_intake_envelope.json", "l1_plan_contract.json", "route_contract.json",
            "l3_bypass_receipt.json", "l2_execution_receipt.json",
            "exit_review_packet.json", "runtime_exhaust_bundle.json",
            "otel_runtime_trace.json",
        ):
            data = json.loads((gr.run_dir / fname).read_text(encoding="utf-8"))
            assert data["run_id"] == expected_run_id, f"run_id drift in {fname}"

    def test_exit_timestamp_precedes_exhaust_timestamp(self, bypass_cfg: EmissionConfig):
        """N7 guard: exhaust.observed_after_exit_at_utc must be >= exit.emitted_at_utc."""
        with governed_run(bypass_cfg, cli_args=[]) as gr:
            pass
        exit_data = json.loads((gr.run_dir / "exit_review_packet.json").read_text(encoding="utf-8"))
        exhaust_data = json.loads((gr.run_dir / "runtime_exhaust_bundle.json").read_text(encoding="utf-8"))
        assert exhaust_data["observed_after_exit_at_utc"] >= exit_data["emitted_at_utc"]


# ---------------------------------------------------------------------------
# Test 12-14: GovernedRun (managed-workflow path)
# ---------------------------------------------------------------------------


class TestGovernedRunManagedWorkflow:
    def test_l3_orchestration_receipt_emitted_not_bypass(self, managed_workflow_cfg: EmissionConfig):
        with governed_run(managed_workflow_cfg, cli_args=[]) as gr:
            with gr.span("L3_orchestrate"):
                pass
        files = {p.name for p in gr.run_dir.iterdir()}
        assert "l3_orchestration_receipt.json" in files
        assert "l3_bypass_receipt.json" not in files

    def test_static_dag_hash_bound_to_l3_receipt(self, managed_workflow_cfg: EmissionConfig):
        """N6 guard: l3_orchestration_receipt.static_dag_hash MUST equal route_contract.static_dag_sha256."""
        with governed_run(managed_workflow_cfg, cli_args=[]) as gr:
            pass
        route = json.loads((gr.run_dir / "route_contract.json").read_text(encoding="utf-8"))
        l3 = json.loads((gr.run_dir / "l3_orchestration_receipt.json").read_text(encoding="utf-8"))
        assert route["static_dag_sha256"] is not None
        assert l3["static_dag_hash"] == route["static_dag_sha256"]
        assert l3["dag_sha256"] == route["static_dag_sha256"]

    def test_c0_and_prompt_emitted_when_expected(self, managed_workflow_cfg: EmissionConfig):
        with governed_run(managed_workflow_cfg, cli_args=[]) as gr:
            pass
        files = {p.name for p in gr.run_dir.iterdir()}
        assert "final_evidence_contract.json" in files
        assert "prompt_assembly_manifest.json" in files


# ---------------------------------------------------------------------------
# Test 15-16: exception path + exit-code discipline
# ---------------------------------------------------------------------------


class TestGovernedRunErrorPaths:
    def test_exception_still_seals_receipts_and_sets_exit_fail(self, bypass_cfg: EmissionConfig):
        with pytest.raises(RuntimeError, match="boom"):
            with governed_run(bypass_cfg, cli_args=[]) as gr:
                with gr.span("L2_execute"):
                    raise RuntimeError("boom")
        exit_data = json.loads((gr.run_dir / "exit_review_packet.json").read_text(encoding="utf-8"))
        assert exit_data["x3_disposition"] == "EXIT_FAIL"
        assert "entrypoint_exception" in exit_data["failed_stages"]

    def test_set_run_dir_retargets_phase2_receipts(self, bypass_cfg: EmissionConfig, tmp_path: Path):
        """apps_rg pattern: app-owned pipeline creates its own run dir;
        spine seals Phase-2 receipts next to the app artifacts via set_run_dir."""
        retargeted = tmp_path / "custom_run_dir" / "20260502_000000"
        with governed_run(bypass_cfg, cli_args=[]) as gr:
            with gr.span("L2_execute"):
                gr.mark_stage("L2_execute", "ok")
            gr.set_run_dir(retargeted)
        assert gr.run_dir == retargeted
        # Receipts landed in the retargeted dir, NOT in the original bypass_cfg.runs_root
        assert (retargeted / "exit_review_packet.json").exists()
        assert (retargeted / "runtime_exhaust_bundle.json").exists()

    def test_target_company_and_role_thread_into_u0_intake(self, tmp_path: Path):
        """apps_rg pattern: target_company + target_role must thread
        into u0_intake_envelope.json, NOT be hard-coded None."""
        route_registry = tmp_path / "config" / "route_registry.yaml"
        _make_route_registry(route_registry, execution_form="DETERMINISTIC_PIPELINE", l3_required=False)
        cfg = EmissionConfig(
            app_name="apps_target",
            entrypoint_command="python -m apps_target",
            runs_root=tmp_path / "runs",
            route_registry_path=route_registry,
            l3_dag_path=None,
            plan_steps=[L1PlanStep(step_id="s0", name="s0", kind="ingest")],
            plan_rationale="test",
            expects_c0_grounding=False,
            expects_prompt_assembly=False,
            expects_static_dag=False,
            expected_execution_form="DETERMINISTIC_PIPELINE",
            expected_l3_path="BYPASSED",
            target_company="Acme Corp",
            target_role="SVP Engineering",
            repo_root=tmp_path,
        )
        with governed_run(cfg, cli_args=[]) as gr:
            pass
        u0 = json.loads((gr.run_dir / "u0_intake_envelope.json").read_text(encoding="utf-8"))
        assert u0["target_company"] == "Acme Corp"
        assert u0["target_role"] == "SVP Engineering"

    def test_missing_l3_dag_for_ran_raises(self, tmp_path: Path):
        route_registry = tmp_path / "config" / "route_registry.yaml"
        _make_route_registry(
            route_registry, execution_form="MANAGED_WORKFLOW", l3_required=True,
        )
        cfg = EmissionConfig(
            app_name="apps_test_bad",
            entrypoint_command="python -m apps_test_bad",
            runs_root=tmp_path / "runs",
            route_registry_path=route_registry,
            l3_dag_path=tmp_path / "config" / "missing_l3_dag.yaml",  # does not exist
            plan_steps=[L1PlanStep(step_id="s", name="n", kind="ingest")],
            plan_rationale="x",
            expects_c0_grounding=False,
            expects_prompt_assembly=False,
            expects_static_dag=True,
            expected_execution_form="MANAGED_WORKFLOW",
            expected_l3_path="RAN",
            repo_root=tmp_path,
        )
        with pytest.raises(RuntimeError, match="requires a real l3_dag.yaml"):
            with governed_run(cfg, cli_args=[]):
                pass
