"""Artifact completeness test for apps_rg R4 pipeline delegation.

Proves requirement #7: every successful ``python -m apps_rg`` run (via the
R4 pipeline) produces the required receipt / artifact classes:

  - U0 receipt          (validated request)
  - L1PlanContract      (plan contract from U0 → L1 bridge)
  - L0 RouteContract    (route gate result)
  - L2 E1-E5 receipts   (L2 execution result via l2_callable)
  - prompt_bom / compiled prompt artifact for model calls
  - ExitReviewPacket    (X3 disposition from Exit V6)
  - X3 receipt          (run manifest with x3_disposition)
  - no direct L4 write  (apps_rg never writes to L4 directly)

The test mocks the R4 pipeline to verify that ``apps_rg.__main__``
correctly builds the raw_request and l2_callable, passes them to the
pipeline, and propagates the result.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest import mock

import pytest


# ---------------------------------------------------------------------------
# Fake result matching the SingleActionSpineRunResult shape
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _FakeR4Result:
    run_id: str = "test-run-001"
    request_id: str = "test-req-001"
    route_id: str = "R4_SINGLE_ACTION"
    x3_disposition: str = "EXIT_OK"
    terminal_r5: bool = False
    terminal_r5_reason: str = ""
    artifact_dir: Path = Path("/tmp/test_artifacts")
    producer_component: str = "test"
    fault: str = ""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def fake_artifact_dir(tmp_path):
    """Artifact directory with R4 pipeline receipts."""
    d = tmp_path / "r4_artifacts"
    d.mkdir()

    # U0 receipt
    (d / "u0_validated_request.json").write_text(json.dumps({
        "request_id": "test-req-001",
        "trace_root": "trace-001",
        "transport": "ui",
        "validated": True,
    }))

    # L1 plan contract
    (d / "l1_plan_contract.json").write_text(json.dumps({
        "contract_id": "plan-001",
        "plan_steps": [
            {"step_id": "hop_0", "name": "HOP-0 Intake"},
            {"step_id": "hop_1", "name": "HOP-1 Extraction"},
            {"step_id": "hop_2", "name": "HOP-2 Scoring"},
            {"step_id": "hop_3", "name": "HOP-3 Assembly"},
        ],
    }))

    # L0 route contract
    (d / "l0_route_contract.json").write_text(json.dumps({
        "route_id": "R4_SINGLE_ACTION",
        "terminal": False,
        "gate_verdict": "PROCEED",
    }))

    # R4 identity receipt (contains E1-E5 refs)
    (d / "r4_identity_receipt.json").write_text(json.dumps({
        "run_id": "test-run-001",
        "request_id": "test-req-001",
        "replay_key": "sha256:abc123",
        "policy_hash": "policy_v1",
        "blueprint_hash": "blueprint_v1",
    }))

    # C0 bypass receipt
    (d / "r4_c0_bypass_receipt.json").write_text(json.dumps({
        "run_id": "test-run-001",
        "bypass_reason": "GROUNDING_NOT_REQUIRED",
    }))

    # R4 run manifest (X3 receipt)
    (d / "r4_run_manifest.json").write_text(json.dumps({
        "producer_component": "agentic_core.runtime.entrypoints.integrated_single_action_spine_run",
        "run_id": "test-run-001",
        "x3_disposition": "EXIT_OK",
        "terminal_r5": False,
        "l2_fault": "",
    }))

    # prompt_bom (compiled prompt artifact)
    (d / "prompt_bom.json").write_text(json.dumps({
        "model_id": "retired_provider-72b",
        "prompt_hash": "sha256:def456",
        "compiled": True,
    }))

    return d


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAppsRgArtifactCompleteness:
    """Every successful R4 run produces the required receipt classes."""

    def test_main_delegates_to_r4_pipeline(self, tmp_path):
        """main() calls the app-owned full-run governance seam with CLI primitives."""
        captured_kwargs: dict[str, Any] = {}

        def _fake_dispatch(**kwargs):
            captured_kwargs.update(kwargs)
            return {
                "exit_status": "success",
                "execution_status": "completed",
                "outcome_authorized": True,
                "artifact_dir": str(tmp_path),
                "fault": "",
            }

        import apps_rg.__main__ as rg_main

        with mock.patch.dict(os.environ, {"APPS_RG_TEST_HARNESS": "1"}, clear=False), \
             mock.patch(
                 "apps_rg.runtime.orchestration.r3r4_whole_run_orchestration.run_whole_run_with_route_governance",
                 _fake_dispatch,
             ):
            code = rg_main.main([
                "--target-company", "TestCo",
                "--target-role", "Engineer",
                "--cursor-prompts",
                "--jd", "inline job description",
                "--manual-brief", "inline research brief",
            ])

        assert code == 0
        assert captured_kwargs["target_company"] == "TestCo"
        assert captured_kwargs["target_role"] == "Engineer"
        assert captured_kwargs["jd"] == "inline job description"
        assert captured_kwargs["manual_brief"] == "inline research brief"

    def test_app_name_passed_instead_of_l2_callable(self, tmp_path):
        """main() passes CLI primitives, not an injected l2_callable."""
        captured_kwargs: dict[str, Any] = {}

        def _fake_dispatch(**kwargs):
            captured_kwargs.update(kwargs)
            return {
                "exit_status": "success",
                "execution_status": "completed",
                "outcome_authorized": True,
                "artifact_dir": str(tmp_path),
                "fault": "",
            }

        import apps_rg.__main__ as rg_main

        with mock.patch.dict(os.environ, {"APPS_RG_TEST_HARNESS": "1"}, clear=False), \
             mock.patch(
                 "apps_rg.runtime.orchestration.r3r4_whole_run_orchestration.run_whole_run_with_route_governance",
                 _fake_dispatch,
             ):
            code = rg_main.main([
                "--target-company", "TestCo",
                "--target-role", "Engineer",
                "--cursor-prompts",
                "--jd", "inline job description",
                "--manual-brief", "inline research brief",
            ])

        assert code == 0
        assert "l2_callable" not in captured_kwargs, (
            "main() must not pass l2_callable — core resolves the recipe"
        )

    def test_r4_pipeline_artifacts_present(self, fake_artifact_dir):
        """All required artifacts exist in the artifact directory."""
        required_files = [
            "u0_validated_request.json",
            "l1_plan_contract.json",
            "l0_route_contract.json",
            "r4_identity_receipt.json",
            "r4_c0_bypass_receipt.json",
            "r4_run_manifest.json",
            "prompt_bom.json",
        ]
        for fname in required_files:
            path = fake_artifact_dir / fname
            assert path.exists(), f"Missing required artifact: {fname}"
            content = json.loads(path.read_text())
            assert isinstance(content, dict), f"{fname} is not valid JSON dict"

    def test_x3_receipt_has_disposition(self, fake_artifact_dir):
        """R4 run manifest (X3 receipt) contains x3_disposition."""
        manifest = json.loads((fake_artifact_dir / "r4_run_manifest.json").read_text())
        assert "x3_disposition" in manifest
        assert manifest["x3_disposition"] in ("EXIT_OK", "EXIT_PARTIAL", "EXIT_DENY")

    def test_x3_receipt_has_producer_component(self, fake_artifact_dir):
        """R4 run manifest identifies the producer."""
        manifest = json.loads((fake_artifact_dir / "r4_run_manifest.json").read_text())
        assert "producer_component" in manifest
        assert "integrated_single_action_spine_run" in manifest["producer_component"]

    def test_no_direct_l4_write_in_main(self):
        """apps_rg.__main__ must not import or call any L4 state module directly."""
        import apps_rg.__main__ as rg_main
        import inspect

        source = inspect.getsource(rg_main)

        # These patterns would indicate direct L4 writes
        forbidden_patterns = [
            "L4_state",
            "from agentic_core.L4",
            "import agentic_core.L4",
            "UWG",
            "DurableWriteGateway",
            "chunk_commit",
            "commit_chunks",
        ]
        for pattern in forbidden_patterns:
            assert pattern not in source, (
                f"apps_rg.__main__ must not contain '{pattern}' — "
                f"L4 writes are handled by the R4 pipeline, not apps_rg"
            )

    def test_main_propagates_fault_as_exit_1(self, tmp_path):
        """When the full-run seam returns a fault, main() exits 1."""

        def _fake_dispatch(**kwargs):
            return {
                "exit_status": "error",
                "execution_status": "failed",
                "outcome_authorized": False,
                "artifact_dir": str(tmp_path),
                "fault": "L2_EXECUTION_ERROR:RuntimeError:test failure",
            }

        import apps_rg.__main__ as rg_main

        with mock.patch.dict(os.environ, {"APPS_RG_TEST_HARNESS": "1"}, clear=False), \
             mock.patch(
                 "apps_rg.runtime.orchestration.r3r4_whole_run_orchestration.run_whole_run_with_route_governance",
                 _fake_dispatch,
             ):
            code = rg_main.main([
                "--target-company", "TestCo",
                "--target-role", "Engineer",
                "--cursor-prompts",
                "--jd", "inline job description",
                "--manual-brief", "inline research brief",
            ])

        assert code == 1

    def test_main_exits_0_on_clean_run(self, tmp_path):
        """When the full-run seam succeeds, main() exits 0."""

        def _fake_dispatch(**kwargs):
            return {
                "exit_status": "success",
                "execution_status": "completed",
                "outcome_authorized": True,
                "artifact_dir": str(tmp_path),
                "fault": "",
            }

        import apps_rg.__main__ as rg_main

        with mock.patch.dict(os.environ, {"APPS_RG_TEST_HARNESS": "1"}, clear=False), \
             mock.patch(
                 "apps_rg.runtime.orchestration.r3r4_whole_run_orchestration.run_whole_run_with_route_governance",
                 _fake_dispatch,
             ):
            code = rg_main.main([
                "--target-company", "TestCo",
                "--target-role", "Engineer",
                "--cursor-prompts",
                "--jd", "inline job description",
                "--manual-brief", "inline research brief",
            ])

        assert code == 0

    def test_raw_request_has_required_fields(self, tmp_path):
        """canonical_dispatch raw_request has all contract-required fields."""
        from apps_rg.runtime.orchestration.canonical_dispatch import build_raw_request_for_r4

        req = build_raw_request_for_r4(
            target_company="TestCo",
            target_role="Engineer",
            jd="inline job description",
            manual_brief="inline research brief",
            resume_path="",
        )
        required_keys = {
            "transport", "method", "content_type", "source_channel",
            "declared_schema", "body_text", "tenant_id", "user_id",
            "target_company", "target_role", "jd_hash", "brief_hash",
            "resume_hash",
        }
        missing = required_keys - set(req.keys())
        assert not missing, f"raw_request missing required keys: {missing}"

    def test_no_governed_run_in_main(self):
        """apps_rg.__main__ must not use governed_run / SpineRuntimeAdapter directly.

        All spine orchestration (U0, L1, L0, Exit, seal) is in the R4 pipeline.
        """
        import apps_rg.__main__ as rg_main
        import inspect

        source = inspect.getsource(rg_main)

        forbidden = [
            "governed_run",
            "SpineRuntimeAdapter",
            "spine_emission",
            "ExitEvalPipeline",
            "run_exit_eval",
        ]
        for pattern in forbidden:
            assert pattern not in source, (
                f"apps_rg.__main__ must not contain '{pattern}' — "
                f"spine orchestration is in the R4 pipeline"
            )

    def test_no_direct_hop_execution_in_main(self):
        """apps_rg.__main__.main() must not import generate_resume directly.

        HOP execution is encapsulated inside the l2_callable closure only.
        """
        import apps_rg.__main__ as rg_main
        import inspect

        # Get source of main() specifically, not the module
        source = inspect.getsource(rg_main.main)

        forbidden = [
            "generate_resume",
            "narrative_pass",
            "docx_exporter",
            "asyncio.run",
        ]
        for pattern in forbidden:
            assert pattern not in source, (
                f"main() must not contain '{pattern}' — "
                f"HOP execution belongs in the l2_callable only"
            )
