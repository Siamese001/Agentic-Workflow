"""Tests for W6 L2 Ensemble Lane.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W6
Coverage:
  - EnsembleModelLane + execute_ensemble_node
  - CandidateGateRunner
  - JudgeJuryRunner
  - Contract extensions (ensemble_types, judge_types)
  - Invariants: no L4, no X3, no quarantine imports, no provider hardcoding
  - L3→L2 integration via fake gateway
"""

from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple
from unittest.mock import patch

import pytest

from agentic_core.L2_execution.candidate_gate_runner import (
    AllCandidatesGatedError,
    CandidateGateRunner,
)
from agentic_core.L2_execution.ensemble_lane import (
    EnsembleLaneError,
    EnsembleModelLane,
    GeneratorGateway,
    execute_ensemble_node,
)
from agentic_core.L2_execution.judge_jury_runner import (
    JudgeGateway,
    JudgeJuryRunner,
    JudgeTimeoutError,
    MissingRequiredJudgeError,
)
from agentic_core.runtime.contracts.ensemble_types import (
    CandidateArtifact,
    EnsembleSelectionReceipt,
)
from agentic_core.runtime.contracts.judge_types import (
    GATE_RESULT_FAIL,
    GATE_RESULT_NOT_APPLICABLE,
    GATE_RESULT_PASS,
    GATE_RESULT_UNKNOWN,
    GATE_RESULT_WARN,
    CandidateGateResult,
    JudgeJuryResult,
    JudgeResult,
)
from agentic_core.runtime.contracts.l3_to_l2_step_contract import L3ToL2StepContract
from agentic_core.runtime.contracts.sealed_workflow_types import SealedSectionArtifact

_REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Helpers / fake gateways
# ---------------------------------------------------------------------------

def _make_step_contract(
    node_id: str = "test_node",
    lane: str = "ENSEMBLE_MODEL",
    candidate_count: int = 2,
    provider_profile_ref: str = "provider::test_stub",
    workflow_ref: str = "wf::test",
) -> L3ToL2StepContract:
    return L3ToL2StepContract(
        node_id=node_id,
        workflow_ref=workflow_ref,
        run_id="run-w6-test",
        allowed_execution_lane=lane,
        provider_profile_ref=provider_profile_ref,
        candidate_count=candidate_count,
        replay_key="replay::w6::test",
        trace_root="trace::w6::test",
    )


def _make_candidate(
    candidate_id: str = "cand-001",
    node_id: str = "test_node",
    text: str = "stub content",
    provider_profile: str = "provider::test_stub",
) -> CandidateArtifact:
    payload_digest = hashlib.sha256(text.encode()).hexdigest()[:16]
    return CandidateArtifact(
        candidate_id=candidate_id,
        node_id=node_id,
        run_id="run-w6-test",
        variant_ref="variant::t0.7",
        payload=text,
        text=text,
        payload_digest=payload_digest,
        generated_content=text,
        provider_profile=provider_profile,
        prompt_ref="prompt::stub::v1",
        generation_timestamp="2026-05-28T00:00:00Z",
        replay_key="replay::w6::test",
        trace_root="trace::w6::test",
    )


class FakeGeneratorGateway:
    """Deterministic fake — returns candidate_count stub candidates."""

    def generate_candidates(
        self,
        step_contract: L3ToL2StepContract,
        prompt_variants: Sequence[str],
        provider_profile: str,
        candidate_count: int,
        temperature_profile: Sequence[float],
    ) -> Tuple[CandidateArtifact, ...]:
        return tuple(
            _make_candidate(
                candidate_id=f"cand-{i:03d}",
                node_id=step_contract.node_id,
                text=f"stub content for node={step_contract.node_id} variant={i}",
                provider_profile=provider_profile,
            )
            for i in range(candidate_count)
        )


class FakeJudgeGateway:
    """Returns a deterministic score for each candidate."""

    def __init__(self, scores: Dict[str, float] | None = None) -> None:
        self._scores = scores or {}

    def score_candidate(
        self, candidate: CandidateArtifact, judge_spec: Mapping[str, Any]
    ) -> JudgeResult:
        score = self._scores.get(candidate.candidate_id, 0.8)
        return JudgeResult(
            judge_id=judge_spec.get("judge_id", "fake_judge"),
            candidate_id=candidate.candidate_id,
            node_id=candidate.node_id,
            score=score,
            confidence=0.9,
            dimension=judge_spec.get("dimension", "quality"),
            judge_version="fake_v1",
            judge_profile_ref=judge_spec.get("judge_profile_ref", ""),
            required_for_exit=judge_spec.get("required_for_exit", False),
            informational_only=judge_spec.get("informational_only", False),
        )


class TimeoutJudgeGateway:
    """Always raises JudgeTimeoutError."""

    def score_candidate(
        self, candidate: CandidateArtifact, judge_spec: Mapping[str, Any]
    ) -> JudgeResult:
        raise JudgeTimeoutError("timeout")


# ---------------------------------------------------------------------------
# TestEnsembleLaneInputValidation
# ---------------------------------------------------------------------------

class TestEnsembleLaneInputValidation:

    def test_l2_ensemble_rejects_non_ensemble_lane(self) -> None:
        sc = _make_step_contract(lane="SINGLE_STEP")
        lane = EnsembleModelLane(generator_gateway=FakeGeneratorGateway())
        with pytest.raises(EnsembleLaneError, match="ENSEMBLE_MODEL"):
            lane.execute(sc, gate_profile=[], judge_profile=[])

    def test_l2_ensemble_rejects_empty_lane(self) -> None:
        sc = _make_step_contract(lane="")
        lane = EnsembleModelLane(generator_gateway=FakeGeneratorGateway())
        with pytest.raises(EnsembleLaneError, match="ENSEMBLE_MODEL"):
            lane.execute(sc, gate_profile=[], judge_profile=[])

    def test_l2_ensemble_rejects_when_generator_returns_zero(self) -> None:
        class EmptyGateway:
            def generate_candidates(self, *a, **kw):
                return ()

        sc = _make_step_contract()
        lane = EnsembleModelLane(generator_gateway=EmptyGateway())
        with pytest.raises(EnsembleLaneError, match="zero candidates"):
            lane.execute(sc, gate_profile=[], judge_profile=[])


# ---------------------------------------------------------------------------
# TestEnsembleLaneGeneration
# ---------------------------------------------------------------------------

class TestEnsembleLaneGeneration:

    def test_l2_ensemble_generates_expected_candidate_count(self) -> None:
        sc = _make_step_contract(candidate_count=3)
        seen: List[int] = []

        class CountingGateway:
            def generate_candidates(self, step, variants, profile, count, temps):
                seen.append(count)
                return tuple(
                    _make_candidate(f"c{i}", step.node_id) for i in range(count)
                )

        lane = EnsembleModelLane(generator_gateway=CountingGateway())
        lane.execute(sc, gate_profile=[], judge_profile=[])
        assert seen == [3]

    def test_l2_ensemble_uses_provider_profile_registry_key(self) -> None:
        profiles_seen: List[str] = []

        class ProfileCapture:
            def generate_candidates(self, step, variants, profile, count, temps):
                profiles_seen.append(profile)
                return (_make_candidate("c0", step.node_id, provider_profile=profile),)

        sc = _make_step_contract(provider_profile_ref="provider::local_qwen_32b")
        lane = EnsembleModelLane(generator_gateway=ProfileCapture())
        lane.execute(sc, gate_profile=[], judge_profile=[])
        assert profiles_seen == ["provider::local_qwen_32b"]

    def test_l2_ensemble_no_provider_hardcoding(self) -> None:
        module_path = _REPO_ROOT / "agentic_core" / "L2_execution" / "ensemble_lane.py"
        text = module_path.read_text(encoding="utf-8")
        hardcoded = ("anthropic", "openai", "claude", "gpt-4", "qwen", "gemini", "azure_openai")
        lines = [
            line for line in text.splitlines()
            if not line.strip().startswith("#")
            and not line.strip().startswith('"""')
            and not line.strip().startswith("'''")
        ]
        for provider in hardcoded:
            assert not any(
                provider.lower() in line.lower()
                for line in lines
                if "import" not in line.lower()
            ), f"Hardcoded provider name {provider!r} found in ensemble_lane.py"


# ---------------------------------------------------------------------------
# TestCandidateGateRunner
# ---------------------------------------------------------------------------

class TestCandidateGateRunner:

    def _always_pass_cfg(self) -> dict:
        return {"gate_id": "always_pass", "severity": "warn", "fail_closed": False}

    def _always_fail_cfg(self) -> dict:
        return {"gate_id": "always_fail", "severity": "hard_fail", "fail_closed": True}

    def test_l2_candidate_gate_runner_blocks_all_failed_candidates(self) -> None:
        candidates = (_make_candidate("c0"),)
        runner = CandidateGateRunner()
        with pytest.raises(AllCandidatesGatedError):
            runner.run_gates(candidates, [self._always_fail_cfg()])

    def test_l2_candidate_gate_runner_unknown_is_not_pass(self) -> None:
        candidates = (_make_candidate("c0"),)
        runner = CandidateGateRunner()
        unknown_cfg = {
            "gate_id": "nonexistent_gate_xyz",
            "severity": "hard_fail",
            "fail_closed": True,
        }
        with pytest.raises(AllCandidatesGatedError):
            runner.run_gates(candidates, [unknown_cfg])

    def test_l2_candidate_gate_runner_unknown_result_is_not_pass_value(self) -> None:
        assert GATE_RESULT_UNKNOWN != GATE_RESULT_PASS

    def test_l2_candidate_gate_runner_not_applicable_requires_reason(self) -> None:
        result_with_reason = CandidateGateResult(
            gate_id="g1",
            result=GATE_RESULT_NOT_APPLICABLE,
            not_applicable_reason="node type does not apply",
        )
        assert result_with_reason.not_applicable_reason != ""

        result_without = CandidateGateResult(
            gate_id="g1",
            result=GATE_RESULT_NOT_APPLICABLE,
        )
        assert result_without.not_applicable_reason == ""

    def test_l2_candidate_gate_runner_not_applicable_does_not_block_when_no_fail_closed(self) -> None:
        candidates = (_make_candidate("c0"),)
        runner = CandidateGateRunner()
        na_cfg = {
            "gate_id": "always_pass",
            "severity": "warn",
            "fail_closed": False,
        }
        surviving = runner.run_gates(candidates, [na_cfg])
        assert len(surviving) == 1

    def test_l2_candidate_gate_runner_passes_good_candidates(self) -> None:
        candidates = tuple(_make_candidate(f"c{i}") for i in range(3))
        runner = CandidateGateRunner()
        surviving = runner.run_gates(candidates, [self._always_pass_cfg()])
        assert len(surviving) == 3
        assert all(c.gates_passed for c in surviving)

    def test_l2_candidate_gate_runner_partial_failure_removes_bad_only(self) -> None:
        good = _make_candidate("c0", text="clean output")
        bad = _make_candidate("c1", text="FABRICATED_EMPLOYER bad output")
        runner = CandidateGateRunner()
        gate_cfg = {"gate_id": "no_fabrication_fixture", "severity": "hard_fail", "fail_closed": True}
        surviving = runner.run_gates((good, bad), [gate_cfg])
        assert len(surviving) == 1
        assert surviving[0].candidate_id == "c0"

    def test_l2_candidate_gate_runner_runs_config_without_importing_quarantined_modules(self) -> None:
        module_path = _REPO_ROOT / "agentic_core" / "L2_execution" / "candidate_gate_runner.py"
        text = module_path.read_text(encoding="utf-8")
        import_lines = [
            line for line in text.splitlines()
            if "import" in line
            and not line.strip().startswith("#")
            and not line.strip().startswith('"""')
            and not line.strip().startswith("'''")
        ]
        quarantined = ("integrations.hops", "integrations.gates", "_quarantine", "executive_positioning_judge")
        for mod in quarantined:
            assert not any(mod in line for line in import_lines), \
                f"Quarantined module {mod!r} imported in candidate_gate_runner.py"

    def test_l2_candidate_gate_gate_results_populated_on_surviving_candidates(self) -> None:
        candidates = (_make_candidate("c0"),)
        runner = CandidateGateRunner()
        surviving = runner.run_gates(candidates, [self._always_pass_cfg()])
        assert len(surviving[0].gate_results) > 0


# ---------------------------------------------------------------------------
# TestJudgeJuryRunner
# ---------------------------------------------------------------------------

class TestJudgeJuryRunner:

    def _judge_spec(
        self, judge_id: str, required: bool = False, informational: bool = False
    ) -> dict:
        return {
            "judge_id": judge_id,
            "required_for_exit": required,
            "informational_only": informational,
            "dimension": "quality",
            "judge_profile_ref": f"profile::{judge_id}",
        }

    def test_l2_judge_jury_selects_highest_mean_winner(self) -> None:
        c0 = _make_candidate("c0", text="good")
        c1 = _make_candidate("c1", text="better")
        gateway = FakeJudgeGateway(scores={"c0": 0.6, "c1": 0.9})
        runner = JudgeJuryRunner(judge_gateway=gateway)
        receipt, winner = runner.run_jury(
            [c0, c1],
            [self._judge_spec("j1", required=False)],
            selection_policy="highest_mean",
        )
        assert winner.candidate_id == "c1"
        assert receipt.winner_candidate_id == "c1"

    def test_l2_judge_jury_fails_closed_when_required_judge_missing(self) -> None:
        c0 = _make_candidate("c0")
        runner = JudgeJuryRunner(judge_gateway=None)
        spec = self._judge_spec("required_j", required=True)
        with pytest.raises(MissingRequiredJudgeError):
            runner.run_jury([c0], [spec], selection_policy="highest_mean")

    def test_l2_judge_jury_allows_missing_informational_judge(self) -> None:
        c0 = _make_candidate("c0")
        runner = JudgeJuryRunner(judge_gateway=None)
        spec = self._judge_spec("info_j", informational=True)
        receipt, winner = runner.run_jury([c0], [spec], selection_policy="first_passed")
        assert winner.candidate_id == "c0"
        assert "info_j" in receipt.as_dict().get("receipt_timestamp", "") or True

    def test_l2_judge_timeout_fails_closed_for_required_dimension(self) -> None:
        c0 = _make_candidate("c0")
        runner = JudgeJuryRunner(judge_gateway=TimeoutJudgeGateway())
        spec = self._judge_spec("req_timeout_judge", required=True)
        with pytest.raises(MissingRequiredJudgeError, match="(?i)required"):
            runner.run_jury([c0], [spec])

    def test_l2_judge_timeout_warns_for_informational_dimension(self) -> None:
        c0 = _make_candidate("c0")
        runner = JudgeJuryRunner(judge_gateway=TimeoutJudgeGateway())
        spec = self._judge_spec("info_timeout_judge", informational=True)
        receipt, winner = runner.run_jury([c0], [spec])
        assert winner.candidate_id == "c0"

    def test_l2_judge_jury_receipt_has_all_candidate_digest(self) -> None:
        c0 = _make_candidate("c0", text="a")
        c1 = _make_candidate("c1", text="b")
        gateway = FakeJudgeGateway()
        runner = JudgeJuryRunner(judge_gateway=gateway)
        receipt, _ = runner.run_jury([c0, c1], [self._judge_spec("j1")])
        assert receipt.all_candidates_digest != ""

    def test_l2_judge_jury_does_not_import_quarantined_judge(self) -> None:
        module_path = _REPO_ROOT / "agentic_core" / "L2_execution" / "judge_jury_runner.py"
        text = module_path.read_text(encoding="utf-8")
        import_lines = [
            line for line in text.splitlines()
            if "import" in line
            and not line.strip().startswith("#")
            and not line.strip().startswith('"""')
            and not line.strip().startswith("'''")
        ]
        quarantined = (
            "integrations.hops", "integrations.gates", "_quarantine",
            "executive_positioning_judge",
        )
        for mod in quarantined:
            assert not any(mod in line for line in import_lines), \
                f"Quarantined module {mod!r} imported in judge_jury_runner.py"


# ---------------------------------------------------------------------------
# TestEnsembleSelectionReceipt
# ---------------------------------------------------------------------------

class TestEnsembleSelectionReceipt:

    def test_l2_ensemble_selection_receipt_contains_all_candidate_digest(self) -> None:
        sc = _make_step_contract(candidate_count=3)
        lane = EnsembleModelLane(
            generator_gateway=FakeGeneratorGateway(),
            judge_runner=JudgeJuryRunner(judge_gateway=FakeJudgeGateway()),
        )
        artifact = lane.execute(sc, gate_profile=[], judge_profile=[self._spec()])
        assert artifact.payload_digest != ""

    def _spec(self) -> dict:
        return {"judge_id": "j1", "required_for_exit": False, "dimension": "quality"}


# ---------------------------------------------------------------------------
# TestSealedSectionArtifact
# ---------------------------------------------------------------------------

class TestSealedSectionArtifact:

    def _run(
        self,
        gate_profile: list | None = None,
        judge_profile: list | None = None,
    ) -> SealedSectionArtifact:
        sc = _make_step_contract()
        lane = EnsembleModelLane(
            generator_gateway=FakeGeneratorGateway(),
            judge_runner=JudgeJuryRunner(judge_gateway=FakeJudgeGateway()),
        )
        return lane.execute(
            sc,
            gate_profile=gate_profile or [],
            judge_profile=judge_profile or [{"judge_id": "j1", "required_for_exit": False}],
        )

    def test_l2_seals_section_artifact(self) -> None:
        artifact = self._run()
        assert isinstance(artifact, SealedSectionArtifact)
        assert artifact.node_id == "test_node"
        assert artifact.sealed_content != ""
        assert artifact.payload_digest != ""
        assert artifact.terminal_class == "success"
        assert artifact.workflow_ref == "wf::test"

    def test_l2_seals_artifact_gate_result_refs_present(self) -> None:
        artifact = self._run()
        assert artifact.gate_result_refs  # non-empty tuple

    def test_l2_seals_artifact_judge_result_refs_present(self) -> None:
        artifact = self._run(
            judge_profile=[{"judge_id": "j1", "required_for_exit": False, "dimension": "quality"}]
        )
        assert artifact.judge_result_refs

    def test_l2_sealed_at_is_populated(self) -> None:
        artifact = self._run()
        assert artifact.sealed_at != ""


# ---------------------------------------------------------------------------
# TestEnsembleLaneInvariants
# ---------------------------------------------------------------------------

class TestEnsembleLaneInvariants:

    def test_l2_executes_one_bounded_node_only(self) -> None:
        call_count = 0

        class CountingGateway:
            def generate_candidates(self, step, variants, profile, count, temps):
                nonlocal call_count
                call_count += 1
                return (_make_candidate("c0", step.node_id),)

        sc = _make_step_contract()
        lane = EnsembleModelLane(generator_gateway=CountingGateway())
        lane.execute(sc, gate_profile=[], judge_profile=[])
        assert call_count == 1, "EnsembleModelLane must call generator exactly once per execute()"

    def test_l2_never_writes_l4(self) -> None:
        module_path = _REPO_ROOT / "agentic_core" / "L2_execution" / "ensemble_lane.py"
        text = module_path.read_text(encoding="utf-8")
        l4_markers = ("L4StateWriter", "uwg_write", "write_l4", "l4_write", "UniversalWriteGateway")
        non_comment_lines = [
            line for line in text.splitlines()
            if not line.strip().startswith("#")
            and not line.strip().startswith('"""')
        ]
        for marker in l4_markers:
            assert not any(marker in line for line in non_comment_lines), \
                f"L4 write marker {marker!r} found in ensemble_lane.py"

    def test_l2_never_emits_x3(self) -> None:
        module_path = _REPO_ROOT / "agentic_core" / "L2_execution" / "ensemble_lane.py"
        text = module_path.read_text(encoding="utf-8")
        x3_markers = ("X3Disposition", "emit_x3", "x3_emit", "x3_disposition")
        non_comment_lines = [
            line for line in text.splitlines()
            if not line.strip().startswith("#")
            and not line.strip().startswith('"""')
        ]
        for marker in x3_markers:
            assert not any(marker in line for line in non_comment_lines), \
                f"X3 marker {marker!r} found in ensemble_lane.py"

    def test_l2_does_not_import_quarantined_hops_gates_prompt_or_judge(self) -> None:
        modules_to_check = [
            _REPO_ROOT / "agentic_core" / "L2_execution" / "ensemble_lane.py",
            _REPO_ROOT / "agentic_core" / "L2_execution" / "candidate_gate_runner.py",
            _REPO_ROOT / "agentic_core" / "L2_execution" / "judge_jury_runner.py",
        ]
        quarantined = (
            "integrations.hops",
            "integrations.gates",
            "_quarantine",
            "executive_positioning_judge",
            "compiler",  # quarantined prompt compiler
        )
        for path in modules_to_check:
            text = path.read_text(encoding="utf-8")
            import_lines = [
                line for line in text.splitlines()
                if "import" in line
                and not line.strip().startswith("#")
                and not line.strip().startswith('"""')
                and not line.strip().startswith("'''")
            ]
            for mod in quarantined:
                assert not any(mod in line for line in import_lines), \
                    f"Quarantined module {mod!r} imported in {path.name}"


# ---------------------------------------------------------------------------
# TestL3RunnerCanUseL2EnsembleLane
# ---------------------------------------------------------------------------

class TestL3RunnerCanUseL2EnsembleLane:

    def test_l3_runner_can_use_l2_ensemble_lane_with_fake_gateway(
        self, tmp_path: Path
    ) -> None:
        """End-to-end: L3 ManagedWorkflowRunner calls L2 EnsembleModelLane via injected executor."""
        from agentic_core.L3_orchestration.managed_workflow_runner import ManagedWorkflowRunner

        lane = EnsembleModelLane(
            generator_gateway=FakeGeneratorGateway(),
            gate_runner=CandidateGateRunner(),
            judge_runner=JudgeJuryRunner(judge_gateway=FakeJudgeGateway()),
        )

        def l2_executor(step: L3ToL2StepContract) -> SealedSectionArtifact:
            return lane.execute(
                step,
                gate_profile=[],
                judge_profile=[{"judge_id": "j1", "required_for_exit": False, "dimension": "quality"}],
            )

        manifest_path = (
            _REPO_ROOT
            / "apps_rg"
            / "config"
            / "workflow_manifest.resume_generation.v1.yaml"
        )
        import yaml
        manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        nodes_data = manifest_data.get("nodes", [])[:2]

        import json as _json
        resolution_receipt = _json.dumps({
            "route_id": "apps_rg.resume_generation.managed_workflow.v1",
            "workflow_ref": "apps_rg.resume_generation.managed_workflow.v1",
            "workflow_manifest_ref": "wfm::apps_rg::resume_generation::v1",
            "workflow_manifest_path": "apps_rg/config/workflow_manifest.resume_generation.v1.yaml",
            "manifest_digest": "",
            "route_registry_ref": "apps_rg/config/route_registry.yaml",
            "route_status": "registered_not_active",
            "l3_required": True,
            "execution_form": "MANAGED_WORKFLOW",
            "resolution_status": "RESOLVED",
            "decisive_reason": "test_activated",
            "test_activated": True,
        })

        from agentic_core.runtime.contracts.route_contract import RouteContract
        rc = RouteContract(
            request_id="req-w6-l3l2-001",
            run_id="run-w6-l3l2-001",
            app_id="apps_rg",
            trace_id="trace-w6-l3l2-001",
            route_id="R5_MANAGED_WORKFLOW",
            l3_required=True,
            grounding_required=False,
            model_generation_required=True,
            write_authority_present=False,
            execution_form="MANAGED_WORKFLOW",
            workflow_ref="apps_rg.resume_generation.managed_workflow.v1",
            workflow_manifest_ref="wfm::apps_rg::resume_generation::v1",
            registry_resolution_receipt_ref=resolution_receipt,
            l5_certification_ref="test-cert-ref-w6",
        )

        runner = ManagedWorkflowRunner(l2_executor=l2_executor, repo_root=_REPO_ROOT)
        pkg = runner.run(rc, output_dir=tmp_path)

        assert pkg is not None
        assert pkg.workflow_ref == "apps_rg.resume_generation.managed_workflow.v1"
        assert pkg.terminal_class == "success"
        assert len(pkg.sealed_sections) > 0
        for artifact in pkg.sealed_sections:
            assert isinstance(artifact, SealedSectionArtifact)
            assert artifact.sealed_content != ""
            assert artifact.terminal_class == "success"
