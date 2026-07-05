"""Unit tests for package-driven L2 same-authority repair."""

from __future__ import annotations

from agentic_core.L2_execution.l2_package_driven_executor import (
    ExecutionValidationReceipt,
    _perform_same_authority_repair,
)
from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
    PromptBlock,
)


def _compiled_prompt() -> CompiledPromptArtifact:
    return CompiledPromptArtifact(
        request_id="req-repair-1",
        run_id="run-repair-1",
        app_id="apps_rg",
        trace_id="trace-repair-1",
        prompt_blocks=(
            PromptBlock(role="system", content="Generate JSON only.", block_index=0),
            PromptBlock(role="user", content="Use the supplied evidence.", block_index=1),
        ),
        system_preamble="Generate JSON only.",
        user_instruction="Use the supplied evidence.",
        assembly_timestamp="2026-06-30T00:00:00Z",
        target_model="Retired/Provider-Model",
        target_provider="local_local_model_server",
        evidence_digest="sha256:evidence",
        compilation_hash="sha256:prompt-before",
        tenant_id="apps_rg",
        l5_certification_ref="l2-apps-rg-test-ref",
        replay_key="replay-repair-1",
    )


def _validation_receipt() -> ExecutionValidationReceipt:
    return ExecutionValidationReceipt(
        receipt_id="evr-repair-1",
        validation_passed=False,
        schema_compliant=False,
        required_fields_present=False,
        json_syntax_valid=True,
        citations_valid=True,
        support_status_accurate=True,
        errors=["Required field missing: executive_summary"],
        timestamp="2026-06-30T00:00:00Z",
    )


def test_same_authority_repair_returns_repaired_prompt_packet() -> None:
    prompt = _compiled_prompt()

    repaired, receipt = _perform_same_authority_repair(
        prompt,
        _validation_receipt(),
        {
            "repair_authority": {
                "same_authority_only": True,
                "cross_authority_blocked": True,
            }
        },
        attempt_number=1,
    )

    assert repaired is not prompt
    assert "H0 Bounded Repair Context" in repaired.user_instruction
    assert "H0 Bounded Repair Context" in repaired.prompt_blocks[-1].content
    assert repaired.compilation_hash != prompt.compilation_hash
    assert receipt.success is True
    assert receipt.before_prompt_hash
    assert receipt.after_prompt_hash
    assert receipt.before_prompt_hash != receipt.after_prompt_hash
    assert receipt.repaired_packet_ref == repaired.compilation_hash
