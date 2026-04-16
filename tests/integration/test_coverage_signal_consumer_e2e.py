"""Wave D5.2 end-to-end integration test.

Wires shaper output -> D5 consumer -> D4 R5-compatible outcome using the
real production modules. No production code is modified by D5.2; this file
is pure integration proof.

Scenarios (Wave D plan §3 Slice D5.2):

1. low coverage + LOW_NORMATIVE_COVERAGE signal -> consumer abstain -> D4 R5
2. adequate coverage -> consumer proceed -> D4 A/B/C/D
3. D4 compatibility -> consumer fields are sufficient to build a
   ``RoutingResult`` without recomputing the D3 abstain decision
4. frozen invariants -> ``evidence_shaper.py``, ``query_router.py``, and
   ``retrieval_eval_curated.py`` are byte-unchanged in the working tree
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path as FsPath
from types import SimpleNamespace
from typing import Any, Iterable

import pytest

from agentic_core.L0_routing.reasoning.path_router import (
    R5_ROUTE,
    Path,
    PathRouter,
    RoutingResult,
)
from agentic_core.L1_cognition.reasoning import abstain_planner as abstain_planner_module
from agentic_core.L1_cognition.reasoning.abstain_planner import (
    ACTION_CONTINUE,
    ACTION_EMIT_R5,
    DECISION_ABSTAIN,
    DECISION_PROCEED,
    DEFAULT_ABSTAIN_THRESHOLD,
)
from agentic_core.L3_orchestration.reasoning.coverage_signal_consumer import (
    ROUTE_HINT_CONTINUE,
    SIGNAL_NORMAL,
    CoverageConsumerResult,
    consume_coverage_signal,
)
from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (
    LOW_NORMATIVE_COVERAGE,
    filter_normative_sources,
)

REPO_ROOT = FsPath(__file__).resolve().parents[2]
SHAPER_PATH = REPO_ROOT / "agentic_core" / "L3_orchestration" / "reasoning" / "engines" / "evidence_shaper.py"
QUERY_ROUTER_PATH = (
    REPO_ROOT / "agentic_core" / "L3_orchestration" / "reasoning" / "engines" / "query_router.py"
)
EVAL_HARNESS_PATH = REPO_ROOT / "tools" / "eval" / "retrieval_eval_curated.py"

_CONSUMER_RESULT_FIELDS = {
    "signal",
    "decision",
    "reason",
    "confidence",
    "threshold",
    "route_hint",
    "action",
}
_ROUTING_RESULT_FIELDS = {
    "route",
    "reason",
    "confidence",
    "threshold",
    "action",
}


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------


def _make_chunk(
    *,
    source_collection: str,
    authority_tier: str,
    invalid_for_normative_use: bool,
    chunk_id: str = "chunk-x",
) -> SimpleNamespace:
    """Build a minimal chunk fixture shaped for ``filter_normative_sources``.

    The shaper only reads ``metadata.source_collection``,
    ``metadata.authority_tier``, and ``metadata.invalid_for_normative_use``
    on each result — a ``SimpleNamespace`` with a ``metadata`` dict is
    sufficient.
    """
    return SimpleNamespace(
        chunk_id=chunk_id,
        metadata={
            "source_collection": source_collection,
            "authority_tier": authority_tier,
            "invalid_for_normative_use": invalid_for_normative_use,
        },
    )


def _make_payload(**overrides: Any) -> Any:
    """Minimal ``GovernedPayload``-shaped fixture for ``PathRouter`` calls.

    ``select_path`` is never called on the R5 / abstain branch, so this
    payload only needs to satisfy the duck-typed reads on the proceed
    branch (where ``select_path`` is monkey-patched out in scenario B to
    keep the integration test hermetic).
    """
    attrs: dict[str, Any] = {
        "input_text": "integration-test",
        "check_ids": [],
        "sanitized": False,
        "d0_injections": None,
    }
    attrs.update(overrides)
    return SimpleNamespace(**attrs)


def _coverage_from_accepted(accepted: list[Any], total: int) -> float:
    """Coverage ratio — accepted / total, clamped to ``[0.0, 1.0]``."""
    if total <= 0:
        return 0.0
    return max(0.0, min(1.0, len(accepted) / total))


def _derive_signals_from_shaper(accepted: list[Any]) -> list[str]:
    """Contract: empty accepted list surfaces ``LOW_NORMATIVE_COVERAGE``.

    This mirrors the caller-side contract documented in
    ``filter_normative_sources``' docstring without editing the shaper.
    """
    return [LOW_NORMATIVE_COVERAGE] if not accepted else []


def _routing_result_from_consumer_no_recompute(
    consumer_result: CoverageConsumerResult,
    *,
    proceed_route: str | None = None,
) -> RoutingResult:
    """Adapter: consumer -> D4 RoutingResult WITHOUT recomputing plan_abstain.

    D5.2 integration proof — demonstrates that the seven consumer fields are
    sufficient to build a D4 ``RoutingResult``:

    * On the R5 branch: map ``route_hint`` ("R5") -> ``route`` and pass the
      remaining four fields through unchanged.
    * On the proceed branch: the consumer only knows "continue", not the
      actual A/B/C/D path, so the caller must supply ``proceed_route`` from
      ``PathRouter.select_path``. The remaining four fields still flow
      through unchanged.

    Crucially, this adapter does NOT call ``plan_abstain`` — proving the
    consumer output carries enough information for D4 dispatch.
    """
    if consumer_result["route_hint"] == R5_ROUTE:
        return RoutingResult(
            route=R5_ROUTE,
            reason=consumer_result["reason"],
            confidence=consumer_result["confidence"],
            threshold=consumer_result["threshold"],
            action=consumer_result["action"],
        )
    if proceed_route is None:
        raise AssertionError("proceed_route must be supplied when route_hint != R5")
    return RoutingResult(
        route=proceed_route,
        reason=consumer_result["reason"],
        confidence=consumer_result["confidence"],
        threshold=consumer_result["threshold"],
        action=consumer_result["action"],
    )


# ---------------------------------------------------------------------------
# Scenario 1 — low coverage + LOW_NORMATIVE_COVERAGE signal -> abstain -> R5
# ---------------------------------------------------------------------------


class TestLowCoverageShaperSignalYieldsR5:
    """Integration scenario 1: shaper emits LOW_NORMATIVE_COVERAGE -> R5."""

    @pytest.fixture
    def low_coverage_bundle(self) -> dict[str, Any]:
        # Build chunks where NONE satisfy the ext_authority + allowed-tier
        # + invalid=False triad, so the shaper's accepted bucket is empty.
        chunks = [
            _make_chunk(
                source_collection="repo_evidence",
                authority_tier="T4_implementation_evidence",
                invalid_for_normative_use=True,
                chunk_id="c1",
            ),
            _make_chunk(
                source_collection="ext_raw",
                authority_tier="T1_vendor",
                invalid_for_normative_use=True,
                chunk_id="c2",
            ),
        ]
        accepted, rejected = filter_normative_sources(chunks)
        signals = _derive_signals_from_shaper(accepted)
        coverage = _coverage_from_accepted(accepted, total=len(chunks))
        return {
            "chunks": chunks,
            "accepted": accepted,
            "rejected": rejected,
            "signals": signals,
            "coverage": coverage,
        }

    def test_shaper_accepts_zero_chunks(self, low_coverage_bundle: dict[str, Any]) -> None:
        assert low_coverage_bundle["accepted"] == []
        assert len(low_coverage_bundle["rejected"]) == 2

    def test_signal_surfaced_is_low_normative_coverage(self, low_coverage_bundle: dict[str, Any]) -> None:
        assert low_coverage_bundle["signals"] == [LOW_NORMATIVE_COVERAGE]

    def test_consumer_returns_abstain(self, low_coverage_bundle: dict[str, Any]) -> None:
        result = consume_coverage_signal(
            coverage=low_coverage_bundle["coverage"],
            signals=low_coverage_bundle["signals"],
        )
        assert result["signal"] == LOW_NORMATIVE_COVERAGE
        assert result["decision"] == DECISION_ABSTAIN

    def test_consumer_route_hint_is_r5(self, low_coverage_bundle: dict[str, Any]) -> None:
        result = consume_coverage_signal(
            coverage=low_coverage_bundle["coverage"],
            signals=low_coverage_bundle["signals"],
        )
        assert result["route_hint"] == R5_ROUTE
        assert result["route_hint"] == "R5"

    def test_consumer_action_is_emit_r5_candidate(self, low_coverage_bundle: dict[str, Any]) -> None:
        result = consume_coverage_signal(
            coverage=low_coverage_bundle["coverage"],
            signals=low_coverage_bundle["signals"],
        )
        assert result["action"] == ACTION_EMIT_R5

    def test_adapter_builds_r5_routing_result_without_recompute(
        self, low_coverage_bundle: dict[str, Any]
    ) -> None:
        consumer_result = consume_coverage_signal(
            coverage=low_coverage_bundle["coverage"],
            signals=low_coverage_bundle["signals"],
        )
        routing_result = _routing_result_from_consumer_no_recompute(consumer_result)
        assert routing_result["route"] == R5_ROUTE
        assert routing_result["action"] == ACTION_EMIT_R5
        assert routing_result["reason"] == consumer_result["reason"]
        assert routing_result["confidence"] == pytest.approx(consumer_result["confidence"])
        assert routing_result["threshold"] == pytest.approx(consumer_result["threshold"])
        assert set(routing_result.keys()) == _ROUTING_RESULT_FIELDS


# ---------------------------------------------------------------------------
# Scenario 2 — adequate coverage -> proceed -> A/B/C/D
# ---------------------------------------------------------------------------


class TestAdequateCoverageShaperYieldsContinue:
    """Integration scenario 2: shaper finds normative evidence -> continue."""

    @pytest.fixture
    def adequate_coverage_bundle(self) -> dict[str, Any]:
        # Build chunks where all pass the filter_normative_sources gate.
        chunks = [
            _make_chunk(
                source_collection="ext_authority",
                authority_tier="T1_vendor",
                invalid_for_normative_use=False,
                chunk_id=f"c{i}",
            )
            for i in range(3)
        ]
        accepted, rejected = filter_normative_sources(chunks)
        signals = _derive_signals_from_shaper(accepted)
        coverage = _coverage_from_accepted(accepted, total=len(chunks))
        return {
            "chunks": chunks,
            "accepted": accepted,
            "rejected": rejected,
            "signals": signals,
            "coverage": coverage,
        }

    def test_shaper_accepts_all_chunks(self, adequate_coverage_bundle: dict[str, Any]) -> None:
        assert len(adequate_coverage_bundle["accepted"]) == 3
        assert adequate_coverage_bundle["rejected"] == []

    def test_no_low_coverage_signal_surfaced(self, adequate_coverage_bundle: dict[str, Any]) -> None:
        assert adequate_coverage_bundle["signals"] == []
        assert adequate_coverage_bundle["coverage"] == pytest.approx(1.0)

    def test_consumer_returns_proceed(self, adequate_coverage_bundle: dict[str, Any]) -> None:
        result = consume_coverage_signal(
            coverage=adequate_coverage_bundle["coverage"],
            signals=adequate_coverage_bundle["signals"],
        )
        assert result["signal"] == SIGNAL_NORMAL
        assert result["decision"] == DECISION_PROCEED

    def test_consumer_route_hint_is_continue(self, adequate_coverage_bundle: dict[str, Any]) -> None:
        result = consume_coverage_signal(
            coverage=adequate_coverage_bundle["coverage"],
            signals=adequate_coverage_bundle["signals"],
        )
        assert result["route_hint"] == ROUTE_HINT_CONTINUE
        assert result["action"] == ACTION_CONTINUE

    def test_adapter_builds_proceed_routing_result_without_recompute(
        self,
        adequate_coverage_bundle: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # On the proceed branch, the caller resolves the actual Path via
        # PathRouter.select_path. We monkey-patch select_path to keep this
        # test hermetic (select_path has heavy contract/telemetry side
        # effects unrelated to the D5 integration contract).
        monkeypatch.setattr(PathRouter, "select_path", lambda self, p: Path.C)
        router = PathRouter()
        payload = _make_payload()

        consumer_result = consume_coverage_signal(
            coverage=adequate_coverage_bundle["coverage"],
            signals=adequate_coverage_bundle["signals"],
        )
        proceed_route = router.select_path(payload).value
        routing_result = _routing_result_from_consumer_no_recompute(
            consumer_result, proceed_route=proceed_route
        )

        assert routing_result["route"] == "C"
        assert routing_result["action"] == ACTION_CONTINUE
        assert routing_result["reason"] == consumer_result["reason"]
        assert routing_result["confidence"] == pytest.approx(consumer_result["confidence"])
        assert routing_result["threshold"] == pytest.approx(consumer_result["threshold"])
        assert set(routing_result.keys()) == _ROUTING_RESULT_FIELDS


# ---------------------------------------------------------------------------
# Scenario 3 — D4 compatibility: consumer fields drive R5 without recompute
# ---------------------------------------------------------------------------


class TestConsumerFieldsDriveD4WithoutRecompute:
    """Integration scenario 3: prove D4 compatibility.

    Feeding the same inputs into the consumer and into
    ``PathRouter.route_with_confidence`` must produce identical
    ``(reason, confidence, threshold, action)`` quintuples and a
    matching ``route``/``route_hint`` mapping — proving the consumer's
    output carries everything the D4 R5 branch needs.
    """

    def test_r5_branch_consumer_matches_route_with_confidence(self) -> None:
        coverage = 0.10
        threshold = 0.50

        consumer_result = consume_coverage_signal(
            coverage=coverage,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=threshold,
        )
        # On the R5 branch, route_with_confidence does NOT call select_path,
        # so no monkey-patching is required to keep this hermetic.
        router = PathRouter()
        routing_result = router.route_with_confidence(
            _make_payload(), confidence=coverage, threshold=threshold
        )

        # Consumer route_hint "R5" == router route "R5"
        assert consumer_result["route_hint"] == routing_result["route"]
        assert routing_result["route"] == R5_ROUTE
        # Action is identical verbatim.
        assert consumer_result["action"] == routing_result["action"]
        assert routing_result["action"] == ACTION_EMIT_R5
        # Numeric fields are identical (both flow from the same D3 call).
        assert consumer_result["confidence"] == pytest.approx(routing_result["confidence"])
        assert consumer_result["threshold"] == pytest.approx(routing_result["threshold"])

    def test_consumer_fields_match_d3_primitive_on_r5_branch(self) -> None:
        # When the consumer sees LOW_NORMATIVE_COVERAGE, its reason embeds
        # the signal name. Assert the other four fields still line up with
        # a direct plan_abstain call so the consumer is provably delegating.
        coverage = 0.10
        threshold = 0.50

        consumer_result = consume_coverage_signal(
            coverage=coverage,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=threshold,
        )
        direct = abstain_planner_module.plan_abstain(coverage, threshold)
        assert consumer_result["decision"] == direct["decision"]
        assert consumer_result["confidence"] == pytest.approx(direct["confidence"])
        assert consumer_result["threshold"] == pytest.approx(direct["threshold"])
        assert consumer_result["action"] == direct["action"]
        # reason differs by design (consumer embeds signal name)
        assert LOW_NORMATIVE_COVERAGE in consumer_result["reason"]
        assert LOW_NORMATIVE_COVERAGE not in direct["reason"]

    def test_adapter_does_not_call_plan_abstain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Hard proof: once the consumer has emitted its result, the D5.2
        adapter can build a D4 ``RoutingResult`` WITHOUT invoking
        ``plan_abstain`` again.

        We compute the consumer result first, then patch ``plan_abstain``
        in BOTH modules to raise. The adapter must still succeed.
        """
        consumer_result = consume_coverage_signal(
            coverage=0.10,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )

        def _explode(*args: Any, **kwargs: Any) -> Any:
            raise AssertionError("plan_abstain must not be called during D4 construction")

        # Poison both call sites so any recompute would be caught.
        from agentic_core.L0_routing.reasoning import path_router as path_router_module
        from agentic_core.L3_orchestration.reasoning import (
            coverage_signal_consumer as consumer_module,
        )

        monkeypatch.setattr(path_router_module, "plan_abstain", _explode)
        monkeypatch.setattr(consumer_module, "plan_abstain", _explode)

        # Adapter builds RoutingResult purely from the cached consumer fields.
        routing_result = _routing_result_from_consumer_no_recompute(consumer_result)
        assert routing_result["route"] == R5_ROUTE
        assert routing_result["action"] == ACTION_EMIT_R5

    def test_routing_result_is_json_serializable(self) -> None:
        consumer_result = consume_coverage_signal(
            coverage=0.10,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )
        routing_result = _routing_result_from_consumer_no_recompute(consumer_result)
        encoded = json.dumps(dict(routing_result))
        decoded = json.loads(encoded)
        assert decoded == dict(routing_result)

    def test_consumer_result_is_json_serializable(self) -> None:
        consumer_result = consume_coverage_signal(
            coverage=0.10,
            signals=[LOW_NORMATIVE_COVERAGE],
            threshold=0.50,
        )
        encoded = json.dumps(dict(consumer_result))
        decoded = json.loads(encoded)
        assert decoded == dict(consumer_result)


# ---------------------------------------------------------------------------
# Scenario 4 — frozen invariants
# ---------------------------------------------------------------------------


class TestFrozenInvariants:
    """Integration scenario 4: prove frozen modules unchanged in the
    working tree as a result of the D5 work.

    Per Wave D plan §2d, §2c, §2e:
    - evidence_shaper.py is frozen
    - query_router.py is frozen
    - retrieval_eval_curated.py is frozen
    """

    @pytest.mark.parametrize(
        "frozen_path",
        [SHAPER_PATH, QUERY_ROUTER_PATH, EVAL_HARNESS_PATH],
        ids=["evidence_shaper", "query_router", "retrieval_eval_curated"],
    )
    def test_frozen_file_has_no_uncommitted_diff(self, frozen_path: FsPath) -> None:
        assert frozen_path.exists(), f"frozen path not found: {frozen_path}"
        proc = subprocess.run(
            [
                "git",
                "diff",
                "--exit-code",
                "--",
                str(frozen_path),
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert proc.returncode == 0, (
            f"{frozen_path.name} has uncommitted changes; D5.2 must not "
            f"edit it.\nstdout=\n{proc.stdout}\nstderr=\n{proc.stderr}"
        )

    def test_shaper_file_stable_across_two_reads(self) -> None:
        # Belt-and-suspenders: guarantees the file isn't being mutated
        # concurrently during the integration run.
        data_a = SHAPER_PATH.read_bytes()
        data_b = SHAPER_PATH.read_bytes()
        assert hashlib.sha256(data_a).hexdigest() == hashlib.sha256(data_b).hexdigest()

    def test_consumer_uses_shaper_constant_identity(self) -> None:
        # Sanity: the consumer and the real shaper module share the
        # SAME LOW_NORMATIVE_COVERAGE constant object — proving there is
        # no shadow copy in the consumer module.
        from agentic_core.L3_orchestration.reasoning import (
            coverage_signal_consumer as consumer_module,
        )
        from agentic_core.L3_orchestration.reasoning.engines import (
            evidence_shaper as shaper_module,
        )

        assert consumer_module.LOW_NORMATIVE_COVERAGE is shaper_module.LOW_NORMATIVE_COVERAGE


# ---------------------------------------------------------------------------
# Scenario 5 — full end-to-end smoke (real shaper -> real consumer -> real D4)
# ---------------------------------------------------------------------------


class TestFullEndToEndSmoke:
    """Integration scenario 5: single-call full-pipeline smoke test.

    Starts from raw chunks, runs the real shaper, derives the signal +
    coverage, calls the real consumer, and finally hands the result to
    the real D4 ``PathRouter.route_with_confidence`` entry point. Asserts
    the R5 outcome surfaces end-to-end.
    """

    def test_full_pipeline_low_coverage_yields_r5(self) -> None:
        chunks = [
            _make_chunk(
                source_collection="ext_raw",
                authority_tier="T1_vendor",
                invalid_for_normative_use=True,
                chunk_id="smoke-c1",
            ),
        ]

        # Stage 1 — real shaper
        accepted, _rejected = filter_normative_sources(chunks)
        signals: Iterable[str] = [LOW_NORMATIVE_COVERAGE] if not accepted else []
        coverage = len(accepted) / max(1, len(chunks))

        # Stage 2 — real consumer
        consumer_result = consume_coverage_signal(
            coverage=coverage,
            signals=signals,
        )
        assert consumer_result["signal"] == LOW_NORMATIVE_COVERAGE
        assert consumer_result["route_hint"] == R5_ROUTE

        # Stage 3 — real D4 entry point (R5 branch never touches select_path)
        router = PathRouter()
        routing_result = router.route_with_confidence(
            _make_payload(),
            confidence=consumer_result["confidence"],
            threshold=consumer_result["threshold"],
        )

        # End-to-end assertions: shaper signal propagated to a D4 R5 outcome.
        assert routing_result["route"] == R5_ROUTE
        assert routing_result["action"] == ACTION_EMIT_R5
        assert routing_result["confidence"] == pytest.approx(consumer_result["confidence"])
        assert routing_result["threshold"] == pytest.approx(consumer_result["threshold"])
        # The full D4 payload is JSON-round-trippable for telemetry.
        encoded = json.dumps(dict(routing_result))
        assert json.loads(encoded) == dict(routing_result)

    def test_full_pipeline_adequate_coverage_stays_in_continue_branch(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        chunks = [
            _make_chunk(
                source_collection="ext_authority",
                authority_tier="T2_standard",
                invalid_for_normative_use=False,
                chunk_id=f"smoke-hi-{i}",
            )
            for i in range(2)
        ]

        accepted, _rejected = filter_normative_sources(chunks)
        signals = [LOW_NORMATIVE_COVERAGE] if not accepted else []
        coverage = len(accepted) / max(1, len(chunks))
        assert accepted and coverage == pytest.approx(1.0)

        consumer_result = consume_coverage_signal(
            coverage=coverage,
            signals=signals,
        )
        assert consumer_result["route_hint"] == ROUTE_HINT_CONTINUE
        assert consumer_result["action"] == ACTION_CONTINUE

        # On the continue branch route_with_confidence delegates to
        # select_path — keep that hermetic.
        monkeypatch.setattr(PathRouter, "select_path", lambda self, p: Path.A)
        router = PathRouter()
        routing_result = router.route_with_confidence(
            _make_payload(),
            confidence=consumer_result["confidence"],
            threshold=consumer_result["threshold"],
        )
        assert routing_result["route"] in {"A", "B", "C", "D"}
        assert routing_result["route"] != R5_ROUTE
        assert routing_result["action"] == ACTION_CONTINUE
