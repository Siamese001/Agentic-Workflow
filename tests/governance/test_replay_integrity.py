"""Wave 5.2: Replay artifact sealing tests.

Validates:
- replay_hash computed on create
- integrity_verified set True on create
- Tampered raw_response_bytes fails integrity check
- Tampered model_version fails integrity check
- Valid bundle passes integrity check
- verify_replay_integrity function
"""

import pytest

from agentic_core.L2_execution.types.llm_replay_types import (
    ReplayBundle,
    verify_replay_integrity,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_replay_integrity")
_emit_applies_guardrail("p0", "test_replay_integrity", "p0_governance")
_emit_reads_policy_state("p0", "test_replay_integrity", "policy_binding")
_emit_snapshots_state("p0", "test_replay_integrity", "state_snapshot")
emit_replay_key("p0", "test_replay_integrity")
emit_determinism_digest("p0", "test_replay_integrity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_replay_integrity", "execution_auth")
_emit_validates_capability("p2", "test_replay_integrity", "capability_check")
_emit_routes_to_capability("p2", "test_replay_integrity", "capability_route")
_emit_writes_via_uwg("p2", "test_replay_integrity", "uwg_write")
_emit_blocks_direct_write("p2", "test_replay_integrity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_replay_integrity", "tool_invocation")
_emit_captures_execution_output("p2", "test_replay_integrity", "exec_output")
_emit_dispatches_agent("p3", "test_replay_integrity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_replay_integrity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_replay_integrity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_replay_integrity", "healing_outcome")
_emit_escalates_failure("p3", "test_replay_integrity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_replay_integrity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_replay_integrity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_replay_integrity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_replay_integrity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_replay_integrity", "eval_metric")
_emit_stores_embedding("p4", "test_replay_integrity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_replay_integrity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_replay_integrity", "exec_snapshot_link")

pytestmark = pytest.mark.governance

PROMPT = b"test prompt"
RESPONSE = b"test response"


class TestReplayHashComputed:
    """replay_hash must be set on create."""

    def test_replay_hash_is_sha256(self):
        bundle = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        assert len(bundle.replay_hash) == 64
        assert all(c in "0123456789abcdef" for c in bundle.replay_hash)

    def test_integrity_verified_true_on_create(self):
        bundle = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        assert bundle.integrity_verified is True

    def test_replay_hash_deterministic(self):
        a = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        b = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        assert a.replay_hash == b.replay_hash


class TestTamperDetection:
    """Tampered bundles must fail integrity check."""

    def test_tampered_response_fails(self):
        good = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        tampered = ReplayBundle(
            model_version=good.model_version,
            tokenizer_version=good.tokenizer_version,
            raw_prompt_bytes=good.raw_prompt_bytes,
            raw_response_bytes=b"TAMPERED",
            provider_checksum=good.provider_checksum,
            replay_hash=good.replay_hash,
            integrity_verified=good.integrity_verified,
        )
        assert not verify_replay_integrity(tampered)

    def test_tampered_model_version_fails(self):
        good = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        tampered = ReplayBundle(
            model_version="TAMPERED",
            tokenizer_version=good.tokenizer_version,
            raw_prompt_bytes=good.raw_prompt_bytes,
            raw_response_bytes=good.raw_response_bytes,
            provider_checksum=good.provider_checksum,
            replay_hash=good.replay_hash,
            integrity_verified=good.integrity_verified,
        )
        assert not verify_replay_integrity(tampered)

    def test_valid_bundle_passes(self):
        bundle = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        assert verify_replay_integrity(bundle)
