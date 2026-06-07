"""D2 tests — UWG durable write path and Prompt Assembly adapter.

Covers:
  D2.1 emit_uwg_pack_record() in apps_qna.exit_wiring
  D2.2 run_pa_for_card_context() in apps_qna.card_context.pa_adapter

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-deferred-e9c5b3.md D2
"""

from __future__ import annotations

import pytest

from apps_qna.types.spine_contracts import (
    CardPackManifestExtended,
    ExitReviewPacket,
    X3Disposition,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _manifest(slug: str = "google-swe-l5", cards: int = 3) -> CardPackManifestExtended:
    return CardPackManifestExtended(
        interview_slug=slug,
        built_at="2026-05-05T00:00:00Z",
        builder_version="1.0",
        cards=tuple(f"card_{i}" for i in range(cards)),
        routes_covered=("build_time_compiler",),
    )


def _allow_packet(manifest: CardPackManifestExtended) -> ExitReviewPacket:
    return ExitReviewPacket(
        x3_disposition=X3Disposition.ALLOW_FINISH,
        final_evidence_contract={"evidence_sufficiency": "grounded"},
        manifest=manifest,
    )


def _abstain_packet(manifest: CardPackManifestExtended) -> ExitReviewPacket:
    return ExitReviewPacket(
        x3_disposition=X3Disposition.SAFE_ABSTAIN,
        final_evidence_contract={"evidence_sufficiency": "empty"},
        manifest=manifest,
        reason_codes=("no_cards_rendered",),
    )


# ---------------------------------------------------------------------------
# D2.1 — UWG write path
# ---------------------------------------------------------------------------

class TestUWGWriteResult:
    def test_importable(self) -> None:
        from apps_qna.exit_wiring import UWGWriteResult
        r = UWGWriteResult()
        assert not r.committed
        assert not r.skipped
        assert not r.blocked

    def test_disabled_returns_skipped(self) -> None:
        from apps_qna.exit_wiring import emit_uwg_pack_record
        m = _manifest()
        pkt = _allow_packet(m)
        result = emit_uwg_pack_record(manifest=m, exit_packet=pkt, enabled=False)
        assert result.skipped
        assert result.reason == "disabled_by_caller"
        assert not result.committed

    def test_non_allow_finish_skipped(self) -> None:
        from apps_qna.exit_wiring import emit_uwg_pack_record
        m = _manifest()
        pkt = _abstain_packet(m)
        result = emit_uwg_pack_record(manifest=m, exit_packet=pkt)
        assert result.skipped
        assert "SAFE_ABSTAIN" in result.reason
        assert not result.committed

    def test_allow_finish_commits_or_blocks(self) -> None:
        from apps_qna.exit_wiring import emit_uwg_pack_record
        m = _manifest()
        pkt = _allow_packet(m)
        result = emit_uwg_pack_record(
            manifest=m,
            exit_packet=pkt,
            policy_hash="test-policy-hash",
            blueprint_hash="test-blueprint-hash",
            replay_key="test-replay-key",
            request_id="req-001",
            run_id="run-001",
            trace_root="trace-001",
        )
        # Either committed or blocked — never raises
        assert result.committed or result.blocked or result.skipped

    def test_committed_has_receipt_id(self) -> None:
        from apps_qna.exit_wiring import emit_uwg_pack_record
        m = _manifest()
        pkt = _allow_packet(m)
        result = emit_uwg_pack_record(
            manifest=m,
            exit_packet=pkt,
            policy_hash="ph-abc",
            blueprint_hash="bh-abc",
            replay_key="rk-abc",
            request_id="req-abc",
            run_id="run-abc",
            trace_root="tr-abc",
        )
        if result.committed:
            assert result.commit_receipt_id
        elif result.blocked:
            assert result.blocked_receipt_id or result.reason

    def test_error_is_fail_open(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from apps_qna import exit_wiring

        def _bad_gateway(*args: object, **kwargs: object) -> None:
            raise RuntimeError("simulated UWG failure")

        monkeypatch.setattr(
            "apps_qna.exit_wiring.DurableWriteGateway",
            _bad_gateway,
            raising=False,
        )
        from apps_qna.exit_wiring import emit_uwg_pack_record
        m = _manifest()
        pkt = _allow_packet(m)

        try:
            result = emit_uwg_pack_record(
                manifest=m,
                exit_packet=pkt,
                policy_hash="ph",
                blueprint_hash="bh",
                replay_key="rk",
                request_id="req",
                run_id="run",
                trace_root="tr",
            )
            assert result.skipped or result.error or result.committed or result.blocked
        except Exception:
            pytest.fail("emit_uwg_pack_record must not raise — fail-open contract violated")

    def test_empty_manifest_is_handled(self) -> None:
        from apps_qna.exit_wiring import emit_uwg_pack_record
        m = CardPackManifestExtended()
        pkt = ExitReviewPacket(
            x3_disposition=X3Disposition.ALLOW_FINISH,
            final_evidence_contract={"evidence_sufficiency": "grounded"},
            manifest=m,
        )
        result = emit_uwg_pack_record(manifest=m, exit_packet=pkt)
        assert result.committed or result.blocked or result.skipped

    def test_all_three_dispositions_skipped_except_allow(self) -> None:
        from apps_qna.exit_wiring import emit_uwg_pack_record
        m = _manifest()
        for disposition in (
            X3Disposition.SAFE_ABSTAIN,
            X3Disposition.REROUTE,
            X3Disposition.ESCALATE_HITL,
            X3Disposition.SAFE_FALLBACK,
        ):
            pkt = ExitReviewPacket(x3_disposition=disposition, manifest=m)
            result = emit_uwg_pack_record(manifest=m, exit_packet=pkt)
            assert result.skipped, f"Expected skipped for {disposition}"


# ---------------------------------------------------------------------------
# D2.2 — Prompt Assembly adapter
# ---------------------------------------------------------------------------

class TestPAAdapter:
    def test_importable(self) -> None:
        from apps_qna.card_context.pa_adapter import PAAdapterResult, run_pa_for_card_context
        assert callable(run_pa_for_card_context)
        r = PAAdapterResult()
        assert r.pipeline is None

    def test_grounded_context_passes_pa(self) -> None:
        from apps_qna.card_context.pa_adapter import run_pa_for_card_context
        ctx = {
            "interview_slug": "google-swe-l5",
            "route_id": "build_time_compiler",
            "grounded": True,
            "evidence_sufficiency": "grounded",
            "retrieval_sources": [{"source_id": "src-001"}],
            "company_name": "Google",
            "role_title": "SWE L5",
        }
        result = run_pa_for_card_context(
            card_context=ctx,
            interview_slug="google-swe-l5",
            route_id="build_time_compiler",
            policy_hash="ph-test",
            blueprint_hash="bh-test",
            request_id="req-test",
            run_id="run-test",
        )
        assert result.pipeline is not None
        assert result.error == ""
        assert result.dispatch_disposition != ""

    def test_empty_context_does_not_raise(self) -> None:
        from apps_qna.card_context.pa_adapter import run_pa_for_card_context
        result = run_pa_for_card_context(
            card_context={},
            interview_slug="",
            route_id="",
        )
        assert result.pipeline is not None or result.error != ""

    def test_dispatchable_when_pa_passes(self) -> None:
        from apps_qna.card_context.pa_adapter import run_pa_for_card_context
        from agentic_core.prompt_governance.prompt_assembly.pa7_dispatch_states import (
            DispatchDisposition,
        )
        ctx = {
            "grounded": False,
            "evidence_sufficiency": "template_only",
            "retrieval_sources": [],
            "interview_slug": "test-slug",
            "route_id": "build_time_compiler",
        }
        result = run_pa_for_card_context(
            card_context=ctx,
            interview_slug="test-slug",
            route_id="build_time_compiler",
        )
        assert result.pipeline is not None
        if result.dispatchable:
            assert result.dispatch_disposition == DispatchDisposition.PASS.value
            assert result.reason == ""

    def test_blocked_has_non_empty_reason(self) -> None:
        from apps_qna.card_context.pa_adapter import run_pa_for_card_context
        ctx = {
            "grounded": False,
            "evidence_sufficiency": "empty",
            "retrieval_sources": [],
        }
        result = run_pa_for_card_context(
            card_context=ctx,
            interview_slug="blocked-slug",
            route_id="build_time_compiler",
        )
        if not result.dispatchable and result.error == "":
            assert result.reason != "" or result.dispatch_disposition != ""

    def test_pipeline_result_has_events(self) -> None:
        from apps_qna.card_context.pa_adapter import run_pa_for_card_context
        ctx = {
            "grounded": False,
            "evidence_sufficiency": "template_only",
            "retrieval_sources": [],
        }
        result = run_pa_for_card_context(
            card_context=ctx,
            interview_slug="test",
            route_id="build_time_compiler",
        )
        if result.pipeline is not None:
            assert isinstance(result.pipeline.events, tuple)
            assert len(result.pipeline.events) >= 1

    def test_large_context_handled_without_raise(self) -> None:
        from apps_qna.card_context.pa_adapter import run_pa_for_card_context
        ctx = {
            "grounded": True,
            "evidence_sufficiency": "grounded",
            "retrieval_sources": [{"source_id": f"src-{i}"} for i in range(50)],
            "company_name": "BigCorp",
            "role_title": "Principal Engineer",
            "cards": ["card text " * 100] * 20,
        }
        result = run_pa_for_card_context(
            card_context=ctx,
            interview_slug="large-slug",
            route_id="build_time_compiler",
            model_context_window=1_000_000,
        )
        assert result.pipeline is not None or result.error != ""

    def test_error_path_returns_adapter_result(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from apps_qna.card_context import pa_adapter

        def _explode(*args: object, **kwargs: object) -> None:
            raise RuntimeError("simulated PA failure")

        monkeypatch.setattr(pa_adapter, "run_prompt_assembly_pipeline", _explode)

        result = pa_adapter.run_pa_for_card_context(
            card_context={"grounded": False},
            interview_slug="err-slug",
            route_id="build_time_compiler",
        )
        assert result.error != ""
        assert not result.dispatchable
        assert result.dispatch_disposition == "error"
