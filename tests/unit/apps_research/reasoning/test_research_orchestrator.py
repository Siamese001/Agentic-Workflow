"""Unit tests for the provider-neutral apps_research orchestrator."""

from __future__ import annotations

import asyncio
from unittest.mock import Mock, patch

from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
from apps_research.types.research_types import ResearchRequest, ResearchResult


def _make_request() -> ResearchRequest:
    return ResearchRequest(topic="AI safety in autonomous systems", dry_run=True)


def _patch_runtime(*, sections: list | None = None, gate_passed: bool = True):
    assembly = Mock(
        execute=Mock(
            return_value=Mock(
                sections=sections if sections is not None else [],
                comparison_matrix=[],
                source_register=[],
            )
        )
    )
    gate = Mock(
        validate=Mock(
            return_value=Mock(
                passed=gate_passed,
                quality_score=0.9 if gate_passed else 0.4,
                violations=[] if gate_passed else [Mock(rule_id="R1", severity="HIGH", message="bad")],
            )
        )
    )
    return (
        patch(
            "apps_research.engines.research_assembly_engine.ResearchAssemblyEngine",
            Mock(return_value=assembly),
        ),
        patch(
            "apps_research.validators.research_gate_validator.ResearchGateValidator",
            Mock(return_value=gate),
        ),
        assembly,
        gate,
    )


def test_orchestrator_exposes_no_local_model_runtime_surface() -> None:
    orch = ResearchOrchestrator(dry_run=True)
    removed = ("q" + "wen_enabled", "_q" + "wen_gateway", "_q" + "wen_init_error")

    assert all(not hasattr(orch, name) for name in removed)
    assert not hasattr(orch, "synthesize_research_with_" + "q" + "wen")


def test_research_result_schema_has_no_local_model_fields() -> None:
    result = ResearchResult()
    payload = result.model_dump()

    assert "q" + "wen_inference_result" not in payload
    assert "local_first_disposition" not in payload


def test_run_executes_assembly_and_gate_without_provider_setup() -> None:
    asm_patch, gate_patch, assembly, gate = _patch_runtime()
    with asm_patch, gate_patch:
        orch = ResearchOrchestrator(dry_run=True)
        result = asyncio.run(orch.run(_make_request()))

    assembly.execute.assert_called_once()
    gate.validate.assert_called_once()
    assert result.status == "dry_run"
    assert result.quality_score == 0.9
    assert result.passed_gate is True


def test_gate_failure_records_failed_status_in_hard_fail_mode() -> None:
    asm_patch, gate_patch, _assembly, _gate = _patch_runtime(gate_passed=False)
    with asm_patch, gate_patch:
        orch = ResearchOrchestrator(dry_run=True, gate_mode="HARD_FAIL")
        result = asyncio.run(orch.run(_make_request()))

    assert result.status == "failed"
    assert result.passed_gate is False
    assert result.gate_violations == ["[R1:HIGH] bad"]
