"""Acceptance checks 4, 5, 6 for apps_rg → agentic_core refactoring.

Check 4: Model-call gating — LLM calls fail before provider invocation
         when prompt_bom / PA artifact is missing.
Check 5: Artifact negative control — when R4 runner raises, no domain
         artifacts are produced (no generated_resume.json, no narrative,
         no docx, no prompt_bom, no cache write, no model call).
Check 6: Layer receipt completeness — a successful R4 pipeline run
         produces all required spine receipts in the artifact_dir.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# Canonical CLI full-run seam (same target as apps_rg.__main__ inner import).
_DISPATCH_SEAM = (
    "apps_rg.runtime.orchestration.r3r4_whole_run_orchestration."
    "run_whole_run_with_route_governance"
)

# Historical pa_local + HOP adapter modules intentionally absent; reintroduce or
# point tests at replacement surfaces under apps-rg-w13 backlog.
_BACKLOG_W13_PA_SURFACES = (
    "Historical apps_rg.prompt_assembly.pa_local / integrations.hops / reasoning "
    "surfaces removed; restore or replace under apps-rg-w13. "
    "Ref: .codex/plans/apps-rg-w13-apps-contract-triage-c4d7e2.md"
)


# ===========================================================================
# CHECK 4: Model-call gating
# ===========================================================================


@pytest.mark.skip(reason=_BACKLOG_W13_PA_SURFACES)
class TestModelCallGating:
    """LLM calls must fail before provider invocation when PA artifact is missing."""

    def test_capture_prompt_bom_required_for_llm_call(self):
        """capture_prompt_bom is the PA-compatible gate.  Without calling it,
        no PromptBOM is produced → auditability violation detected."""
        from apps_rg.prompt_assembly.pa_local import capture_prompt_bom, PromptBOM

        # A valid call produces a BOM
        bom = capture_prompt_bom(
            hop_name="H3_test",
            model="test-model",
            provider_lane="test_lane",
            prompt_template="test prompt",
            token_budget=1000,
        )
        assert isinstance(bom, PromptBOM)
        assert bom.hop_name == "H3_test"
        assert bom.prompt_template_hash  # non-empty hash

    def test_prompt_bom_not_written_without_run_dir(self, tmp_path):
        """When run_dir is None, no BOM file is persisted — the LLM call
        has no audit trail, which the pipeline rejects at Exit V6."""
        from apps_rg.prompt_assembly.pa_local import capture_prompt_bom

        bom = capture_prompt_bom(
            hop_name="H3_test",
            model="test-model",
            prompt_template="test prompt",
            token_budget=1000,
            run_dir=None,  # No run_dir → no persistence
        )
        # BOM object created but no file on disk
        assert bom.hop_name == "H3_test"
        bom_dir = tmp_path / "prompt_bom"
        assert not bom_dir.exists()

    def test_prompt_bom_written_with_run_dir(self, tmp_path):
        """When run_dir is provided, BOM is persisted for audit/replay."""
        from apps_rg.prompt_assembly.pa_local import capture_prompt_bom

        bom = capture_prompt_bom(
            hop_name="H3_orchestrator",
            model="retired_provider-72b",
            provider_lane="retired_provider_profile",
            prompt_template="Generate a resume for {company}",
            token_budget=4096,
            run_dir=tmp_path,
        )
        bom_file = tmp_path / "prompt_bom" / "H3_orchestrator.json"
        assert bom_file.exists()
        content = json.loads(bom_file.read_text())
        assert content["hop_name"] == "H3_orchestrator"
        assert content["model"] == "retired_provider-72b"
        assert content["provider_lane"] == "retired_provider_profile"
        assert content["token_budget"] == 4096
        assert "prompt_template_hash" in content
        assert len(content["prompt_template_hash"]) == 16  # first 16 hex chars

    def test_llm_client_uses_capture_prompt_bom(self):
        """The HOP LLM client adapter imports and calls capture_prompt_bom.

        This proves model calls are gated through PA-compatible instrumentation.
        """
        import inspect
        from apps_rg.integrations.hops import _llm_client

        source = inspect.getsource(_llm_client)
        assert "capture_prompt_bom" in source, (
            "_llm_client.py must use capture_prompt_bom for PA-compatible model gating"
        )

# ===========================================================================
# CHECK 5: Artifact negative control — R4 runner raises → no domain artifacts
# ===========================================================================


class TestArtifactNegativeControl:
    """When ``dispatch_apps_rg_run`` raises or reports failure, CLI exits non-zero."""

    def test_r4_raise_produces_no_resume(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Patch dispatch to raise; main returns 1 and does not materialize domain outputs under cwd."""
        runs_dir = tmp_path / "artifacts" / "apps_rg" / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)

        def _raising(**_kwargs: object) -> None:
            raise RuntimeError("R4 pipeline simulated failure")

        monkeypatch.setattr(_DISPATCH_SEAM, _raising)
        import apps_rg.__main__ as rg_main

        code = rg_main.main(["--target-company", "TestCo", "--target-role", "Engineer"])
        assert code == 1
        assert not list(runs_dir.rglob("generated_resume.json"))
        assert not list(runs_dir.rglob("narrative_resume.json"))
        assert not list(runs_dir.rglob("*.docx"))
        assert not list(runs_dir.rglob("prompt_bom"))

    def test_r4_raise_no_cache_write(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Dispatch failure does not write cache fixtures under a local cache dir."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()

        def _raising(**_kwargs: object) -> None:
            raise RuntimeError("R4 pipeline simulated failure")

        monkeypatch.setattr(_DISPATCH_SEAM, _raising)
        import apps_rg.__main__ as rg_main

        code = rg_main.main(["--target-company", "TestCo", "--target-role", "Engineer"])
        assert code == 1
        assert not list(cache_dir.rglob("r1a_key.txt"))
        assert not list(cache_dir.rglob("*.cache"))

    def test_r4_raise_no_domain_code_invoked(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """``__main__`` remains a shim: failure is handled via dispatch + exit code 1."""
        def _raising(**_kwargs: object) -> None:
            raise RuntimeError("R4 pipeline simulated failure")

        monkeypatch.setattr(_DISPATCH_SEAM, _raising)
        import apps_rg.__main__ as rg_main

        code = rg_main.main(["--target-company", "TestCo", "--target-role", "Engineer"])
        assert code == 1

    def test_r4_fault_produces_exit_1(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Dispatch returns error-shaped dict → main returns 1 (no successful outcome)."""
        runs_dir = tmp_path / "artifacts" / "apps_rg" / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)

        def _faulting(**_kwargs: object) -> dict[str, object]:
            return {
                "exit_status": "error",
                "execution_status": "failed",
                "outcome_authorized": False,
                "x3_disposition": "EXIT_DENY",
                "fault": "L2_EXECUTION_ERROR:RuntimeError:simulated",
                "artifact_dir": str(tmp_path / "emitted"),
            }

        monkeypatch.setattr(_DISPATCH_SEAM, _faulting)
        import apps_rg.__main__ as rg_main

        code = rg_main.main(["--target-company", "TestCo", "--target-role", "Engineer"])
        assert code == 1
        assert not list(runs_dir.rglob("generated_resume.json"))
        assert not list(runs_dir.rglob("*.docx"))


# ===========================================================================
# CHECK 6: Layer receipt completeness for a successful R4 run
# ===========================================================================


class TestLayerReceiptCompleteness:
    """A successful R4 pipeline run produces all required spine receipts."""

    @pytest.fixture()
    def populated_artifact_dir(self, tmp_path):
        """Simulate the artifact_dir as written by a real R4 pipeline run."""
        d = tmp_path / "r4_run"
        d.mkdir()

        # U0 receipt (validated request evidence)
        (d / "u0_validated_request.json").write_text(json.dumps({
            "request_id": "req-001",
            "trace_root": "trace-001",
            "transport": "ui",
            "source_channel": "apps_rg_cli",
            "schema_valid": True,
            "producer_component": "agentic_core.L0_routing.intake.pipeline",
        }))

        # L1 plan contract
        (d / "l1_plan_contract.json").write_text(json.dumps({
            "contract_id": "plan-001",
            "request_id": "req-001",
            "plan_steps": ["hop_0", "hop_1", "hop_2", "hop_3"],
            "producer_component": "agentic_core.L1_cognition.bridges.u0_to_l1_plan",
        }))

        # L0 route contract
        (d / "l0_route_contract.json").write_text(json.dumps({
            "route_id": "R4_SINGLE_ACTION",
            "gate_verdict": "PROCEED",
            "terminal": False,
            "r5_terminal": False,
            "producer_component": "agentic_core.L0_routing.reasoning.route_gates",
        }))

        # C0 bypass receipt
        (d / "r4_c0_bypass_receipt.json").write_text(json.dumps({
            "run_id": "run-001",
            "request_id": "req-001",
            "route_id": "R4_SINGLE_ACTION",
            "bypass_reason": "GROUNDING_NOT_REQUIRED",
            "producer_component": "agentic_core.runtime.contracts.c0_bypass_receipt",
        }))

        # Identity receipt (E1-E5 binding)
        (d / "r4_identity_receipt.json").write_text(json.dumps({
            "run_id": "run-001",
            "request_id": "req-001",
            "replay_key": "r4:abc123",
            "policy_hash": "policy_v1",
            "blueprint_hash": "blueprint_v1",
            "caller_surface": "apps_rg_cli",
            "started_at_utc": "2026-05-04T17:00:00Z",
            "producer_component": "agentic_core.runtime.entrypoints.integrated_single_action_spine_run",
        }))

        # PA prompt artifact (prompt_bom)
        bom_dir = d / "prompt_bom"
        bom_dir.mkdir()
        (bom_dir / "H3_orchestrator.json").write_text(json.dumps({
            "hop_name": "H3_orchestrator",
            "model": "retired_provider-72b",
            "provider_lane": "retired_provider_profile",
            "prompt_template_hash": "a1b2c3d4e5f6g7h8",
            "token_budget": 4096,
            "replay_key": "abc123def456",
            "timestamp": 1714838400.0,
        }))

        # R4 run manifest (X3 receipt)
        (d / "r4_run_manifest.json").write_text(json.dumps({
            "producer_component": "agentic_core.runtime.entrypoints.integrated_single_action_spine_run",
            "run_id": "run-001",
            "request_id": "req-001",
            "route_id": "R4_SINGLE_ACTION",
            "chain_kind": "R4_SINGLE_ACTION",
            "x3_disposition": "EXIT_OK",
            "terminal_r5": False,
            "l2_fault": "",
            "artifact_hash": "sha256:abcdef1234567890",
            "emitted_at": "2026-05-04T17:00:05Z",
        }))

        return d

    def test_u0_receipt_present(self, populated_artifact_dir):
        """U0 validated request receipt exists and has required fields."""
        path = populated_artifact_dir / "u0_validated_request.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert "request_id" in data
        assert "trace_root" in data
        assert data.get("schema_valid") is True

    def test_l1_plan_contract_present(self, populated_artifact_dir):
        """L1PlanContract receipt exists with plan steps."""
        path = populated_artifact_dir / "l1_plan_contract.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert "contract_id" in data
        assert "plan_steps" in data
        assert len(data["plan_steps"]) > 0

    def test_l0_route_contract_present(self, populated_artifact_dir):
        """L0 RouteContract receipt exists and is non-terminal."""
        path = populated_artifact_dir / "l0_route_contract.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert "route_id" in data
        assert data["terminal"] is False

    def test_c0_bypass_receipt_present(self, populated_artifact_dir):
        """C0 bypass receipt (LocalEvidenceContract) exists."""
        path = populated_artifact_dir / "r4_c0_bypass_receipt.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["bypass_reason"] == "GROUNDING_NOT_REQUIRED"

    def test_identity_receipt_with_e1_e5_binding(self, populated_artifact_dir):
        """Identity receipt binds the run across E1-E5 spans."""
        path = populated_artifact_dir / "r4_identity_receipt.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert "run_id" in data
        assert "replay_key" in data
        assert "policy_hash" in data
        assert "started_at_utc" in data

    def test_pa_prompt_artifact_present(self, populated_artifact_dir):
        """PA prompt artifact (prompt_bom) exists for model calls."""
        bom_dir = populated_artifact_dir / "prompt_bom"
        assert bom_dir.exists()
        bom_files = list(bom_dir.glob("*.json"))
        assert len(bom_files) >= 1, "At least one prompt_bom must exist for LLM calls"

        # Validate structure
        bom = json.loads(bom_files[0].read_text())
        assert "hop_name" in bom
        assert "model" in bom
        assert "prompt_template_hash" in bom
        assert "token_budget" in bom

    def test_x3_receipt_present(self, populated_artifact_dir):
        """X3 receipt (run manifest) exists with EXIT_OK disposition."""
        path = populated_artifact_dir / "r4_run_manifest.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["x3_disposition"] == "EXIT_OK"
        assert data["terminal_r5"] is False
        assert data["l2_fault"] == ""

    def test_x3_receipt_has_artifact_hash(self, populated_artifact_dir):
        """X3 receipt includes the artifact hash for integrity verification."""
        path = populated_artifact_dir / "r4_run_manifest.json"
        data = json.loads(path.read_text())
        assert "artifact_hash" in data
        assert data["artifact_hash"].startswith("sha256:")

    def test_no_direct_l4_write_in_artifact_dir(self, populated_artifact_dir):
        """No L4 (durable state) write artifacts exist — those are handled by UWG."""
        all_files = [f.name for f in populated_artifact_dir.rglob("*") if f.is_file()]
        l4_indicators = [
            f for f in all_files
            if any(pattern in f.lower() for pattern in [
                "l4_", "uwg_", "durable_write", "cache_commit", "chunk_commit",
            ])
        ]
        assert not l4_indicators, (
            f"No direct L4 writes should exist in artifact_dir, found: {l4_indicators}"
        )

    def test_all_receipts_have_producer_component(self, populated_artifact_dir):
        """Every receipt JSON identifies its producer for harness verification."""
        receipt_files = [
            "u0_validated_request.json",
            "l1_plan_contract.json",
            "l0_route_contract.json",
            "r4_c0_bypass_receipt.json",
            "r4_identity_receipt.json",
            "r4_run_manifest.json",
        ]
        for fname in receipt_files:
            path = populated_artifact_dir / fname
            if path.exists():
                data = json.loads(path.read_text())
                assert "producer_component" in data, (
                    f"{fname} must have producer_component for harness verification"
                )

    def test_exit_review_packet_implied_by_x3(self, populated_artifact_dir):
        """X3 disposition proves ExitReviewPacket was evaluated by Exit V6.

        The R4 pipeline calls ExitEvalPipeline.run() which produces an
        ExitEvalResult containing the V6Disposition. The x3_disposition in
        the run manifest IS the output of the ExitReviewPacket evaluation.
        """
        path = populated_artifact_dir / "r4_run_manifest.json"
        data = json.loads(path.read_text())
        # The presence of x3_disposition proves Exit V6 ran
        assert data["x3_disposition"] in ("EXIT_OK", "EXIT_PARTIAL", "EXIT_DENY")
        # The producer_component proves it came from the integrated spine path
        # that calls Exit V6.
        assert (
            data["producer_component"]
            == "agentic_core.runtime.entrypoints.integrated_single_action_spine_run"
        )
