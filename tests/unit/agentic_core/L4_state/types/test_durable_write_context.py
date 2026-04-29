"""Unit tests for `agentic_core.L4_state.types.durable_write_context`.

Maps to: docs/reference/00B_L4_State_Archive_and_UWG/00B.7a_L4_UWG_Durable_Write_Context_Invariant.md
Phase 1 DATA CONTRACT.
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L4_state.types.durable_write_context import (
    DurableWriteContext,
    MutationIntentClass,
    WRITE_STAGE_ORDER,
    WriteStage,
    compute_durable_write_digest,
)


def _filler(seed: str) -> str:
    return (seed * 16)[:64]


def make_ctx(
    *,
    seed: str = "a",
    intent: MutationIntentClass = MutationIntentClass.UPDATE,
    state_diff: str | None = None,
    idempotency_key: str = "idem-1",
) -> DurableWriteContext:
    return DurableWriteContext(
        request_id="req-1",
        run_id="run-1",
        trace_id="trace-1",
        tenant_id="tenant-1",
        principal_id="prin-1",
        exit_disposition_id="x3-1",
        commit_request_id="cr-1",
        uwg_receipt_id="uwg-1",
        target_store_id="store-1",
        target_object_ref="obj-1",
        mutation_intent_class=intent,
        state_diff_candidate_hash=state_diff or _filler(seed),
        before_snapshot_hash=_filler("b"),
        after_candidate_hash=_filler("c"),
        schema_hash=_filler("s"),
        policy_hash=_filler("p"),
        blueprint_hash=_filler("u"),
        capability_scope_hash=_filler("e"),
        sandbox_envelope_hash=_filler("f"),
        l5_certification_packet_hash=_filler("L"),
        replay_key="replay-1",
        idempotency_key=idempotency_key,
        write_lock_id="lock-1",
        transaction_id="tx-1",
        audit_manifest_hash=_filler("A"),
        rollback_plan_hash=_filler("R"),
        replay_snapshot_hash=_filler("S"),
        retrieval_invalidation_plan_hash=_filler("V"),
        cache_invalidation_plan_hash=_filler("H"),
        read_surface_refresh_plan_hash=_filler("F"),
        frozen_durable_write_context_hash=_filler("Z"),
        uwg_resolver_digest=_filler("Q"),
    )


class TestDurableWriteContextConstruction:
    def test_construction_succeeds(self) -> None:
        ctx = make_ctx()
        assert ctx.request_id == "req-1"
        assert ctx.mutation_intent_class is MutationIntentClass.UPDATE

    def test_frozen_dataclass_rejects_mutation(self) -> None:
        ctx = make_ctx()
        with pytest.raises((AttributeError, TypeError)):
            ctx.request_id = "req-2"  # type: ignore[misc]

    def test_empty_required_string_rejected(self) -> None:
        with pytest.raises(ValueError, match="request_id"):
            DurableWriteContext(
                request_id="",
                run_id="run-1",
                trace_id="trace-1",
                tenant_id="tenant-1",
                principal_id="prin-1",
                exit_disposition_id="x",
                commit_request_id="c",
                uwg_receipt_id="u",
                target_store_id="s",
                target_object_ref="o",
                mutation_intent_class=MutationIntentClass.CREATE,
                state_diff_candidate_hash=_filler("a"),
                before_snapshot_hash=_filler("b"),
                after_candidate_hash=_filler("c"),
                schema_hash=_filler("s"),
                policy_hash=_filler("p"),
                blueprint_hash=_filler("u"),
                capability_scope_hash=_filler("e"),
                sandbox_envelope_hash=_filler("f"),
                l5_certification_packet_hash=_filler("L"),
                replay_key="r",
                idempotency_key="i",
                write_lock_id="l",
                transaction_id="t",
                audit_manifest_hash=_filler("A"),
                rollback_plan_hash=_filler("R"),
                replay_snapshot_hash=_filler("S"),
                retrieval_invalidation_plan_hash=_filler("V"),
                cache_invalidation_plan_hash=_filler("H"),
                read_surface_refresh_plan_hash=_filler("F"),
                frozen_durable_write_context_hash=_filler("Z"),
                uwg_resolver_digest=_filler("Q"),
            )

    def test_intent_must_be_enum(self) -> None:
        with pytest.raises(TypeError, match="MutationIntentClass"):
            DurableWriteContext(
                request_id="r",
                run_id="r",
                trace_id="t",
                tenant_id="te",
                principal_id="p",
                exit_disposition_id="x",
                commit_request_id="c",
                uwg_receipt_id="u",
                target_store_id="s",
                target_object_ref="o",
                mutation_intent_class="UPDATE",  # type: ignore[arg-type]
                state_diff_candidate_hash=_filler("a"),
                before_snapshot_hash=_filler("b"),
                after_candidate_hash=_filler("c"),
                schema_hash=_filler("s"),
                policy_hash=_filler("p"),
                blueprint_hash=_filler("u"),
                capability_scope_hash=_filler("e"),
                sandbox_envelope_hash=_filler("f"),
                l5_certification_packet_hash=_filler("L"),
                replay_key="r",
                idempotency_key="i",
                write_lock_id="l",
                transaction_id="t",
                audit_manifest_hash=_filler("A"),
                rollback_plan_hash=_filler("R"),
                replay_snapshot_hash=_filler("S"),
                retrieval_invalidation_plan_hash=_filler("V"),
                cache_invalidation_plan_hash=_filler("H"),
                read_surface_refresh_plan_hash=_filler("F"),
                frozen_durable_write_context_hash=_filler("Z"),
                uwg_resolver_digest=_filler("Q"),
            )


class TestDurableWriteContextDigest:
    def test_digest_is_64char_lowercase_hex(self) -> None:
        digest = make_ctx().digest()
        assert len(digest) == 64
        assert digest == digest.lower()
        int(digest, 16)

    def test_digest_deterministic(self) -> None:
        assert make_ctx().digest() == make_ctx().digest()

    def test_digest_changes_on_intent_change(self) -> None:
        d1 = make_ctx(intent=MutationIntentClass.UPDATE).digest()
        d2 = make_ctx(intent=MutationIntentClass.CREATE).digest()
        assert d1 != d2

    def test_digest_changes_on_state_diff_change(self) -> None:
        d1 = make_ctx(state_diff=_filler("a")).digest()
        d2 = make_ctx(state_diff=_filler("b")).digest()
        assert d1 != d2

    def test_canonical_dict_serializes_enum_value(self) -> None:
        canonical = make_ctx().to_canonical_dict()
        assert canonical["mutation_intent_class"] == "UPDATE"
        # JSON round-trippable
        json.dumps(canonical, sort_keys=True)

    def test_compute_function_matches_method(self) -> None:
        ctx = make_ctx()
        assert compute_durable_write_digest(ctx) == ctx.digest()


class TestFirstMismatchedField:
    def test_identical_contexts_no_mismatch(self) -> None:
        assert make_ctx().first_mismatched_field(make_ctx()) == ""

    def test_different_intent_surfaces_intent_field(self) -> None:
        a = make_ctx(intent=MutationIntentClass.UPDATE)
        b = make_ctx(intent=MutationIntentClass.CREATE)
        assert a.first_mismatched_field(b) == "mutation_intent_class"

    def test_different_state_diff_surfaces_state_diff_field(self) -> None:
        a = make_ctx(state_diff=_filler("a"))
        b = make_ctx(state_diff=_filler("b"))
        assert a.first_mismatched_field(b) == "state_diff_candidate_hash"


class TestWriteStageOrder:
    def test_canonical_chain_has_8_stages(self) -> None:
        assert len(WRITE_STAGE_ORDER) == 8

    def test_canonical_chain_starts_at_exit_commit_request(self) -> None:
        assert WRITE_STAGE_ORDER[0] is WriteStage.EXIT_COMMIT_REQUEST

    def test_canonical_chain_ends_at_invalidation(self) -> None:
        assert WRITE_STAGE_ORDER[-1] is WriteStage.RETRIEVAL_CACHE_INVALIDATION
