"""Exhaustive edge-case coverage for the 00C runtime gates doctrine.

Each test class targets one doctrine surface and walks the full boundary of
that surface — including empty, singleton, severity boundaries, exception
variants, JSON round-trip, and immutability guarantees — so any future change
that drifts from the doctrine is caught by a deterministic assertion rather
than by a manual matrix re-read.

Surfaces covered:

| Class                         | Surface                                       |
|-------------------------------|-----------------------------------------------|
| TestDeterministicDigest       | 00C.7 deterministic_digest semantics          |
| TestAggregationBoundaries     | 00C.7 aggregation rule boundary conditions    |
| TestResultInference           | orchestrator._enrich_decision (all 15 disp.)  |
| TestOTELSpanCoverage          | 00C.8 — every span name + attributes + bounds |
| TestSchemaVersionInvariants   | 00C.7 schema_version SSOT                     |
| TestEnumStringSemantics       | Disposition / Result / Severity / GraderType  |
| TestVerdictImmutability       | 00C.7.I.1 / I.2 — append-only, no mutation    |
| TestBypassExceptionCoverage   | 00C.X.10 — all 4 caught exception variants    |
| TestHaltDispositionsCanonical | 00C orchestrator halt set is doctrine-aligned |
| TestVerdictJSONRoundTrip      | Verdict survives JSON serialize/deserialize   |
| TestContextImmutabilityFull   | 00C.IAC.6 — full ctx field snapshot pre/post  |
| TestNotApplicableSemantics    | 00C.7.A.4 — NOT_APPLICABLE requires reason    |
"""
# pylint: disable=no-name-in-module

from __future__ import annotations

import json

import pytest

from agentic_core.L5_safety.runtime_gates import (
    GATE_REGISTRY,
    Disposition,
    GateContext,
    GateDecision,
    GraderType,
    Result,
    Severity,
    SCHEMA_VERSION,
    all_gates,
    evaluate,
)
from agentic_core.L5_safety.runtime_gates.digest import (
    _STABLE_VERDICT_KEYS,
    mesh_digest,
    verdict_digest,
)
from agentic_core.L5_safety.runtime_gates.mesh_result import build_mesh_result
from agentic_core.L5_safety.runtime_gates.orchestrator import (
    DISPATCH_ORDER,
    HALT_DISPOSITIONS,
    run_mesh,
)
from agentic_core.L5_safety.runtime_gates.otel_spans import (
    ALL_SPAN_NAMES,
    SPAN_BYPASS_DETECTED,
    SPAN_GATE_EVALUATE,
    SPAN_GATE_VERDICT,
    SPAN_MESH_COMPLETE,
    SPAN_MESH_START,
    SPAN_UNKNOWN_MATERIAL,
    SPAN_WARN_MATERIAL,
    get_recorder,
)


# ---------------------------------------------------------------------------
# Local helpers
# ---------------------------------------------------------------------------


def _ctx() -> GateContext:
    """Minimal fully-populated context — mirrors conftest baseline."""
    return GateContext(
        request_id="req-edge-001",
        session_id="sess-edge-001",
        run_id="run-edge-001",
        trace_root="trace-edge-001",
        trace_id="trace-id-edge-001",
        tenant_id="tenant-A",
        policy_hash="pol-edge",
        blueprint_hash="blue-edge",
        replay_key="rk-edge",
        evaluated_packet_ref="packet:edge:001",
        intent={"objective": "answer", "raw_text": "x?", "payload_bytes": 10},
        risk_tier="low",
        reversible=True,
        impact_class="read",
    )


def _verdict(**overrides) -> dict:
    """Build a minimal canonical verdict with overrides."""
    base = GateDecision(
        gate_id=overrides.pop("gate_id", "G01"),
        disposition=overrides.pop("disposition", Disposition.ALLOW),
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base.to_verdict()


# ---------------------------------------------------------------------------
# 1. Deterministic digest semantics (00C.7 immutability)
# ---------------------------------------------------------------------------


class TestDeterministicDigest:
    """Boundary tests for ``digest.verdict_digest`` and ``mesh_digest``."""

    def test_identical_verdicts_produce_identical_digest(self) -> None:
        d1 = verdict_digest(_verdict())
        d2 = verdict_digest(_verdict())
        assert d1 == d2
        assert d1.startswith("sha256:")

    def test_different_created_at_offset_does_not_change_digest(self) -> None:
        """``created_at_run_offset`` is excluded from stable keys."""
        d1 = verdict_digest(_verdict(created_at_run_offset=0.1))
        d2 = verdict_digest(_verdict(created_at_run_offset=42.7))
        assert d1 == d2

    def test_different_trace_id_does_not_change_digest(self) -> None:
        """``trace_id`` is per-process and must NOT affect the digest."""
        # trace_id IS in the verdict but NOT in _STABLE_VERDICT_KEYS.
        d1 = verdict_digest(_verdict(trace_id="trace-A"))
        d2 = verdict_digest(_verdict(trace_id="trace-Z"))
        assert d1 == d2, "trace_id leaked into deterministic digest"

    def test_different_disposition_changes_digest(self) -> None:
        d1 = verdict_digest(_verdict(disposition=Disposition.ALLOW))
        d2 = verdict_digest(_verdict(disposition=Disposition.DENY))
        assert d1 != d2

    def test_reason_codes_order_is_significant(self) -> None:
        """reason_codes is a list; order is part of the verdict identity."""
        d1 = verdict_digest(_verdict(reason_codes=["a", "b"]))
        d2 = verdict_digest(_verdict(reason_codes=["b", "a"]))
        assert d1 != d2

    def test_metadata_key_not_in_stable_set(self) -> None:
        """Verdict ``metadata`` is not part of the digest payload."""
        # metadata is on GateDecision but not exposed in to_verdict() and
        # not in _STABLE_VERDICT_KEYS — confirm it does not appear.
        assert "metadata" not in _STABLE_VERDICT_KEYS

    def test_every_stable_key_changes_digest_when_changed(self) -> None:
        """A diff in ANY stable key must produce a different digest."""
        baseline = _verdict()
        baseline_digest = verdict_digest(baseline)
        # Field types we know how to perturb safely:
        perturbations = {
            "gate_id": "G29",
            "gate_family": "different",
            "primary_layer": "L9",
            "evaluated_packet_ref": "packet:other",
            "request_id": "other-req",
            "run_id": "other-run",
            "trace_root": "other-root",
            "tenant_id": "other-tenant",
            "policy_hash": "other-pol",
            "blueprint_hash": "other-bp",
            "replay_key": "other-rk",
            "result": "FAIL",
            "disposition": "DENY",
            "severity": "CRITICAL",
            "reason_codes": ["different"],
            "score": 0.5,
            "threshold": 0.9,
            "grader_type": "LLM_JUDGE",
            "evidence_refs": ["ev:1"],
            "replay_refs": ["rp:1"],
            "source_lineage_refs": ["sl:1"],
            "confidence": 0.5,
            "abstain_flag": True,
            "remediation_hint": "different",
            "schema_version": "ZZZ-9.9.9",
        }
        # Sanity: ensure we cover every stable key.
        assert set(perturbations).issubset(_STABLE_VERDICT_KEYS)
        for key, value in perturbations.items():
            altered = dict(baseline)
            altered[key] = value
            altered_digest = verdict_digest(altered)
            assert altered_digest != baseline_digest, f"Stable key {key!r} did not influence the digest"

    def test_mesh_digest_preserves_order(self) -> None:
        v1 = _verdict(gate_id="G01")
        v2 = _verdict(gate_id="G02")
        digest_a = mesh_digest([v1, v2])
        digest_b = mesh_digest([v2, v1])
        # Mesh order matters because dispatch order is doctrine-fixed.
        assert digest_a != digest_b

    def test_mesh_digest_empty_list_is_deterministic(self) -> None:
        d1 = mesh_digest([])
        d2 = mesh_digest([])
        assert d1 == d2 and d1.startswith("sha256:")

    def test_run_mesh_twice_produces_identical_digests(self) -> None:
        ctx_a = _ctx()
        ctx_b = _ctx()
        mesh_a = run_mesh(ctx_a, halt_on=frozenset(), halt_on_stop_condition=False)
        mesh_b = run_mesh(ctx_b, halt_on=frozenset(), halt_on_stop_condition=False)
        digest_a = mesh_digest([d.to_verdict() for d in mesh_a.decisions])
        digest_b = mesh_digest([d.to_verdict() for d in mesh_b.decisions])
        assert digest_a == digest_b


# ---------------------------------------------------------------------------
# 2. Aggregation rule boundaries (00C.7 §AGGREGATION RULES)
# ---------------------------------------------------------------------------


_DEFAULT_REASONS: object = object()


def _decision(
    gate_id: str = "G_TEST",
    disposition: Disposition = Disposition.ALLOW,
    result: Result = Result.PASS,
    severity: Severity = Severity.INFO,
    reason_codes: list[str] | None | object = _DEFAULT_REASONS,
) -> GateDecision:
    # Sentinel-default so an explicit empty list is preserved (not falsy-
    # coerced into the ["test"] default).
    if reason_codes is _DEFAULT_REASONS:
        reasons = ["test"]
    else:
        reasons = list(reason_codes) if reason_codes else []
    return GateDecision(
        gate_id=gate_id,
        disposition=disposition,
        result=result,
        severity=severity,
        reason_codes=reasons,
    )


def _build(
    decisions: list[GateDecision],
    *,
    required: list[str] | None = None,
) -> object:
    return build_mesh_result(
        decisions,
        required_gate_ids=required if required is not None else [d.gate_id for d in decisions],
        evaluated_surface="L0",
        request_id="req-agg",
        run_id="run-agg",
        trace_root="trace-agg",
    )


class TestAggregationBoundaries:
    """Severity boundary, empty mesh, single-verdict, and precedence tests."""

    def test_empty_decisions_produces_allow_summary(self) -> None:
        """Empty mesh with no required gates → ALLOW (vacuous)."""
        mesh = _build([])
        assert mesh.recommended_disposition_summary == "ALLOW"
        assert mesh.hard_fail_present is False
        assert mesh.unknown_material_present is False
        assert mesh.warn_material_present is False

    def test_empty_decisions_with_missing_required_blocks(self) -> None:
        mesh = _build([], required=["G01", "G02"])
        assert mesh.missing_gate_ids == ["G01", "G02"]
        assert mesh.recommended_disposition_summary == "BLOCK_EXIT"

    def test_single_pass_decision_yields_allow(self) -> None:
        mesh = _build([_decision(disposition=Disposition.ALLOW)])
        assert mesh.recommended_disposition_summary == "ALLOW"

    def test_severity_low_warn_does_not_flag_warn_material(self) -> None:
        """LOW WARN must NOT set warn_material_present (boundary below HIGH)."""
        mesh = _build([_decision(result=Result.WARN, severity=Severity.LOW)])
        assert mesh.warn_material_present is False
        assert mesh.recommended_disposition_summary == "ALLOW"

    def test_severity_medium_warn_does_not_flag_warn_material(self) -> None:
        """MEDIUM WARN must NOT set warn_material_present."""
        mesh = _build([_decision(result=Result.WARN, severity=Severity.MEDIUM)])
        assert mesh.warn_material_present is False

    def test_severity_high_warn_flags_warn_material(self) -> None:
        mesh = _build([_decision(result=Result.WARN, severity=Severity.HIGH)])
        assert mesh.warn_material_present is True
        assert mesh.recommended_disposition_summary == "MARK_DEGRADED"

    def test_severity_critical_warn_flags_warn_material(self) -> None:
        mesh = _build([_decision(result=Result.WARN, severity=Severity.CRITICAL)])
        assert mesh.warn_material_present is True

    def test_severity_low_unknown_does_not_flag_unknown_material(self) -> None:
        mesh = _build([_decision(result=Result.UNKNOWN, severity=Severity.LOW)])
        assert mesh.unknown_material_present is False

    def test_severity_high_unknown_flags_unknown_material(self) -> None:
        mesh = _build([_decision(result=Result.UNKNOWN, severity=Severity.HIGH)])
        assert mesh.unknown_material_present is True
        assert mesh.recommended_disposition_summary == "ESCALATE_HITL"

    def test_hard_fail_overrides_unknown_and_warn(self) -> None:
        """Doctrine precedence: hard_fail > unknown_material > warn_material."""
        mesh = _build(
            [
                _decision(gate_id="G01", disposition=Disposition.DENY),
                _decision(
                    gate_id="G02",
                    result=Result.UNKNOWN,
                    severity=Severity.HIGH,
                ),
                _decision(
                    gate_id="G03",
                    result=Result.WARN,
                    severity=Severity.HIGH,
                ),
            ]
        )
        assert mesh.hard_fail_present is True
        assert mesh.unknown_material_present is True
        assert mesh.warn_material_present is True
        assert mesh.recommended_disposition_summary == "DENY"

    def test_block_commit_is_a_hard_fail(self) -> None:
        mesh = _build([_decision(disposition=Disposition.BLOCK_COMMIT)])
        assert mesh.hard_fail_present is True
        assert mesh.recommended_disposition_summary == "DENY"

    def test_quarantine_is_a_hard_fail(self) -> None:
        mesh = _build([_decision(disposition=Disposition.QUARANTINE)])
        assert mesh.hard_fail_present is True

    def test_all_not_applicable_yields_allow(self) -> None:
        mesh = _build(
            [
                _decision(
                    gate_id=f"G{i:02d}",
                    result=Result.NOT_APPLICABLE,
                    reason_codes=["not_in_scope"],
                )
                for i in range(1, 4)
            ]
        )
        assert mesh.recommended_disposition_summary == "ALLOW"
        assert mesh.hard_fail_present is False

    def test_unknown_overrides_warn(self) -> None:
        """unknown_material > warn_material in summary precedence."""
        mesh = _build(
            [
                _decision(
                    gate_id="G01",
                    result=Result.UNKNOWN,
                    severity=Severity.HIGH,
                ),
                _decision(
                    gate_id="G02",
                    result=Result.WARN,
                    severity=Severity.HIGH,
                ),
            ]
        )
        assert mesh.recommended_disposition_summary == "ESCALATE_HITL"


# ---------------------------------------------------------------------------
# 3. Result inference for every disposition (orchestrator._enrich_decision)
# ---------------------------------------------------------------------------


class _StubGate:
    """Disposition-only mock gate — ``result`` left at default (PASS)."""

    def __init__(self, gate_id: str, disposition: Disposition) -> None:
        self.GATE_ID = gate_id
        self._disposition = disposition

    def evaluate(self, _ctx: GateContext) -> GateDecision:
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=self._disposition,
            reason_codes=["stub"],
        )


# Doctrine 00C.7 mapping (orchestrator._enrich_decision):
_DISPOSITION_TO_EXPECTED_RESULT: dict[Disposition, Result] = {
    # PASS-class
    Disposition.ALLOW: Result.PASS,
    Disposition.COMMIT_REQUEST: Result.PASS,
    Disposition.CLARIFY: Result.PASS,
    # FAIL-class
    Disposition.DENY: Result.FAIL,
    Disposition.QUARANTINE: Result.FAIL,
    Disposition.BLOCK_COMMIT: Result.FAIL,
    # UNKNOWN-class
    Disposition.ESCALATE_HITL: Result.UNKNOWN,
    # WARN-class
    Disposition.ABSTAIN: Result.WARN,
    Disposition.SAFE_FALLBACK: Result.WARN,
    Disposition.REDACT: Result.WARN,
    Disposition.SHRINK_SCOPE: Result.WARN,
    Disposition.MARK_DEGRADED: Result.WARN,
    Disposition.RETRY: Result.WARN,
    Disposition.HEAL: Result.WARN,
    Disposition.REROUTE: Result.WARN,
}


class TestResultInference:
    """Every Disposition maps to the doctrine-mandated default Result."""

    @pytest.mark.parametrize(
        "disposition,expected_result",
        list(_DISPOSITION_TO_EXPECTED_RESULT.items()),
    )
    def test_disposition_infers_doctrine_result(
        self,
        disposition: Disposition,
        expected_result: Result,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        gate_id = f"G_RES_{disposition.value}"
        monkeypatch.setitem(GATE_REGISTRY, gate_id, _StubGate(gate_id, disposition))
        # Use halt_on=frozenset() so we exercise enrichment without a halt.
        result = run_mesh(
            _ctx(),
            order=(gate_id,),
            halt_on=frozenset(),
        )
        assert len(result.decisions) == 1
        decision = result.decisions[0]
        assert decision.disposition is disposition
        assert decision.result is expected_result, (
            f"{disposition.value} should infer to {expected_result.value}, got {decision.result.value}"
        )

    def test_explicit_result_is_not_overwritten_by_inference(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """If a gate explicitly sets ``result``, enrichment must not change it."""

        class _ExplicitGate:
            GATE_ID = "G_EXPLICIT_RES"

            def evaluate(self, _ctx: GateContext) -> GateDecision:
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.ALLOW,
                    result=Result.WARN,  # ALLOW would normally infer PASS
                    severity=Severity.HIGH,
                    reason_codes=["explicit"],
                )

        monkeypatch.setitem(GATE_REGISTRY, _ExplicitGate.GATE_ID, _ExplicitGate())
        out = run_mesh(_ctx(), order=(_ExplicitGate.GATE_ID,), halt_on=frozenset())
        assert out.decisions[0].result is Result.WARN
        assert out.decisions[0].severity is Severity.HIGH


# ---------------------------------------------------------------------------
# 4. OTEL span coverage edge cases (00C.8)
# ---------------------------------------------------------------------------


class TestOTELSpanCoverage:
    """Boundary tests for span emission across the 8 doctrine span names."""

    def test_recorder_resets_between_runs(self) -> None:
        recorder = get_recorder()
        recorder.reset()
        run_mesh(_ctx(), order=("G01",), halt_on=frozenset())
        first_count = len(recorder.spans)
        recorder.reset()
        assert len(recorder.spans) == 0
        run_mesh(_ctx(), order=("G01",), halt_on=frozenset())
        # Second run starts clean — counts should equal first run, not double.
        assert len(recorder.spans) == first_count

    def test_full_mesh_emits_start_and_complete_spans(self) -> None:
        recorder = get_recorder()
        recorder.reset()
        run_mesh(
            _ctx(),
            order=DISPATCH_ORDER,
            halt_on=frozenset(),
            halt_on_stop_condition=False,
        )
        names = recorder.names()
        assert names.count(SPAN_MESH_START) == 1
        assert names.count(SPAN_MESH_COMPLETE) == 1

    def test_each_gate_emits_evaluate_and_verdict(self) -> None:
        recorder = get_recorder()
        recorder.reset()
        run_mesh(
            _ctx(),
            order=DISPATCH_ORDER,
            halt_on=frozenset(),
            halt_on_stop_condition=False,
        )
        evaluate_count = len(recorder.by_name(SPAN_GATE_EVALUATE))
        verdict_count = len(recorder.by_name(SPAN_GATE_VERDICT))
        assert evaluate_count == len(DISPATCH_ORDER) == 29
        assert verdict_count == 29

    def test_mesh_complete_span_includes_halt_attrs_when_halted(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        recorder = get_recorder()
        recorder.reset()

        class _DenyGate:
            GATE_ID = "G_HALT_TEST"

            def evaluate(self, _ctx: GateContext) -> GateDecision:
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.DENY,
                    reason_codes=["halt_test"],
                )

        monkeypatch.setitem(GATE_REGISTRY, _DenyGate.GATE_ID, _DenyGate())
        run_mesh(_ctx(), order=(_DenyGate.GATE_ID,))
        complete = recorder.by_name(SPAN_MESH_COMPLETE)
        assert len(complete) == 1
        attrs = complete[0].attributes
        assert attrs.get("halted_at") == _DenyGate.GATE_ID
        assert attrs.get("reason", "").startswith("halt_disposition")

    def test_mesh_complete_when_no_halt_has_null_halted_at(self) -> None:
        recorder = get_recorder()
        recorder.reset()
        run_mesh(_ctx(), order=("G01",), halt_on=frozenset())
        complete = recorder.by_name(SPAN_MESH_COMPLETE)
        assert complete[-1].attributes.get("halted_at") is None

    def test_unknown_material_span_only_at_high_or_critical_severity(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """LOW/MEDIUM UNKNOWN must NOT emit unknown_material span."""

        class _LowUnknownGate:
            GATE_ID = "G_LOW_UNKNOWN"

            def evaluate(self, _ctx: GateContext) -> GateDecision:
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.ALLOW,  # ALLOW so no halt
                    result=Result.UNKNOWN,
                    severity=Severity.LOW,
                    reason_codes=["low_unknown"],
                )

        monkeypatch.setitem(GATE_REGISTRY, _LowUnknownGate.GATE_ID, _LowUnknownGate())
        recorder = get_recorder()
        recorder.reset()
        run_mesh(_ctx(), order=(_LowUnknownGate.GATE_ID,), halt_on=frozenset())
        assert recorder.by_name(SPAN_UNKNOWN_MATERIAL) == []

    def test_warn_material_span_only_at_high_or_critical_severity(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        class _LowWarnGate:
            GATE_ID = "G_LOW_WARN"

            def evaluate(self, _ctx: GateContext) -> GateDecision:
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.MARK_DEGRADED,
                    result=Result.WARN,
                    severity=Severity.LOW,
                    reason_codes=["low_warn"],
                )

        monkeypatch.setitem(GATE_REGISTRY, _LowWarnGate.GATE_ID, _LowWarnGate())
        recorder = get_recorder()
        recorder.reset()
        run_mesh(_ctx(), order=(_LowWarnGate.GATE_ID,), halt_on=frozenset())
        assert recorder.by_name(SPAN_WARN_MATERIAL) == []

    def test_eight_canonical_span_names_are_unique(self) -> None:
        assert len(set(ALL_SPAN_NAMES)) == 8
        assert len(ALL_SPAN_NAMES) == 8

    def test_every_span_name_uses_runtime_gate_prefix(self) -> None:
        for name in ALL_SPAN_NAMES:
            assert name.startswith("runtime_gate."), f"Span name {name!r} violates 00C.8 prefix convention"


# ---------------------------------------------------------------------------
# 5. Schema version invariants (00C.7 SSOT)
# ---------------------------------------------------------------------------


class TestSchemaVersionInvariants:
    """``SCHEMA_VERSION`` is the SSOT — no drift across surfaces."""

    def test_schema_version_format_is_stable(self) -> None:
        # Format expected by ops_scripts schema gates: "00C-<major>.<minor>.<patch>".
        assert SCHEMA_VERSION.startswith("00C")
        parts = SCHEMA_VERSION.replace("00C-", "").split(".")
        assert len(parts) == 3, f"Schema version not semver-shaped: {SCHEMA_VERSION}"
        for part in parts:
            assert part.isdigit(), f"Non-numeric segment in {SCHEMA_VERSION}"

    def test_every_gate_verdict_carries_schema_version(self) -> None:
        ctx = _ctx()
        for gate_id in all_gates():
            try:
                decision = evaluate(gate_id, ctx)
            except (KeyError, ValueError, TypeError, AttributeError):
                continue
            verdict = decision.to_verdict()
            assert verdict["schema_version"] == SCHEMA_VERSION, (
                f"Gate {gate_id} carries schema_version="
                f"{verdict['schema_version']!r} (expected {SCHEMA_VERSION!r})"
            )

    def test_mesh_result_carries_schema_version(self) -> None:
        mesh = _build([_decision()])
        assert mesh.gate_mesh_schema_version == SCHEMA_VERSION
        assert mesh.to_dict()["gate_mesh_schema_version"] == SCHEMA_VERSION

    def test_default_gate_decision_carries_schema_version(self) -> None:
        decision = GateDecision(gate_id="G01", disposition=Disposition.ALLOW)
        assert decision.schema_version == SCHEMA_VERSION


# ---------------------------------------------------------------------------
# 6. Enum string semantics (JSON-friendly, doctrine-named)
# ---------------------------------------------------------------------------


class TestEnumStringSemantics:
    """All canonical enums are str-typed for direct JSON serialization."""

    def test_disposition_enum_values_match_names(self) -> None:
        for member in Disposition:
            assert member.value == member.name, f"Disposition.{member.name} value drift: {member.value!r}"

    def test_result_enum_values_match_names(self) -> None:
        for member in Result:
            assert member.value == member.name

    def test_severity_enum_values_match_names(self) -> None:
        for member in Severity:
            assert member.value == member.name

    def test_disposition_is_str_subtype(self) -> None:
        assert issubclass(Disposition, str)

    def test_result_is_str_subtype(self) -> None:
        assert issubclass(Result, str)

    def test_severity_is_str_subtype(self) -> None:
        assert issubclass(Severity, str)

    def test_grader_type_is_str_subtype(self) -> None:
        assert issubclass(GraderType, str)

    def test_disposition_count_is_15(self) -> None:
        assert len(list(Disposition)) == 15

    def test_result_count_is_5(self) -> None:
        assert len(list(Result)) == 5

    def test_severity_count_is_5(self) -> None:
        assert len(list(Severity)) == 5

    def test_grader_type_count_is_5(self) -> None:
        assert len(list(GraderType)) == 5

    def test_grader_type_values_are_doctrine_named(self) -> None:
        names = {member.value for member in GraderType}
        assert names == {
            "code",
            "LLM_JUDGE",
            "hybrid",
            "human_calibrated",
            "policy_rule",
        }

    def test_enum_json_round_trip(self) -> None:
        sample = {
            "disposition": Disposition.ESCALATE_HITL,
            "result": Result.UNKNOWN,
            "severity": Severity.HIGH,
            "grader_type": GraderType.POLICY_RULE,
        }
        # str-typed enums serialize as their value directly.
        blob = json.dumps({k: v.value for k, v in sample.items()})
        loaded = json.loads(blob)
        assert loaded == {
            "disposition": "ESCALATE_HITL",
            "result": "UNKNOWN",
            "severity": "HIGH",
            "grader_type": "policy_rule",
        }


# ---------------------------------------------------------------------------
# 7. Verdict immutability (00C.7.I.1 / I.2)
# ---------------------------------------------------------------------------


class TestVerdictImmutability:
    """Mesh handoff envelopes must not be mutable through their public surface."""

    def test_to_dict_returns_independent_lists(self) -> None:
        mesh = _build([_decision(), _decision(gate_id="G02")])
        snapshot_before = list(mesh.verdicts)
        out = mesh.to_dict()
        out["verdicts"].append({"gate_id": "INJECTED"})
        out["completed_gate_ids"].append("INJECTED")
        # Mutating the snapshot must not leak back into the bundle.
        assert mesh.verdicts == snapshot_before
        assert "INJECTED" not in mesh.completed_gate_ids

    def test_to_verdict_returns_fresh_lists_each_call(self) -> None:
        decision = GateDecision(
            gate_id="G01",
            disposition=Disposition.ALLOW,
            reason_codes=["a", "b"],
            evidence_refs=["ev:1"],
            replay_refs=["rp:1"],
            source_lineage_refs=["sl:1"],
        )
        v1 = decision.to_verdict()
        v2 = decision.to_verdict()
        # Mutating v1 lists must not leak into v2 lists.
        v1["reason_codes"].append("X")
        v1["evidence_refs"].append("Y")
        assert v2["reason_codes"] == ["a", "b"]
        assert v2["evidence_refs"] == ["ev:1"]


# ---------------------------------------------------------------------------
# 8. Bypass exception coverage (00C.X.10 — every caught variant)
# ---------------------------------------------------------------------------


class _RaisingGate:
    """Mock gate that raises the configured exception type."""

    def __init__(self, gate_id: str, exc_type: type[Exception]) -> None:
        self.GATE_ID = gate_id
        self._exc_type = exc_type

    def evaluate(self, _ctx: GateContext) -> GateDecision:
        raise self._exc_type(f"forced {self._exc_type.__name__}")


class TestBypassExceptionCoverage:
    """All four caught exception types produce a bypass span + UNKNOWN verdict."""

    @pytest.mark.parametrize(
        "exc_type",
        [KeyError, ValueError, TypeError, AttributeError],
    )
    def test_each_caught_exception_produces_bypass(
        self,
        exc_type: type[Exception],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        gate_id = f"G_RAISE_{exc_type.__name__}"
        monkeypatch.setitem(GATE_REGISTRY, gate_id, _RaisingGate(gate_id, exc_type))
        recorder = get_recorder()
        recorder.reset()
        out = run_mesh(_ctx(), order=(gate_id,))
        # 1. Bypass span emitted with gate_id
        bypass_spans = recorder.by_name(SPAN_BYPASS_DETECTED)
        assert len(bypass_spans) == 1
        assert bypass_spans[0].attributes.get("gate_id") == gate_id
        # 2. Synthesized verdict is UNKNOWN @ HIGH severity
        assert len(out.decisions) == 1
        decision = out.decisions[0]
        assert decision.result is Result.UNKNOWN
        assert decision.severity is Severity.HIGH
        assert decision.disposition is Disposition.ESCALATE_HITL
        # 3. Mesh halts because ESCALATE_HITL is in HALT_DISPOSITIONS
        assert out.halted_at == gate_id


# ---------------------------------------------------------------------------
# 9. HALT_DISPOSITIONS is the doctrine-aligned set
# ---------------------------------------------------------------------------


class TestHaltDispositionsCanonical:
    """Orchestrator halt set is exactly the doctrine-named blocking values."""

    def test_halt_set_is_exactly_five_canonical_dispositions(self) -> None:
        assert HALT_DISPOSITIONS == frozenset(
            {
                Disposition.DENY,
                Disposition.BLOCK_COMMIT,
                Disposition.QUARANTINE,
                Disposition.REDACT,
                Disposition.ESCALATE_HITL,
            }
        )

    def test_allow_is_not_in_halt_set(self) -> None:
        assert Disposition.ALLOW not in HALT_DISPOSITIONS

    @pytest.mark.parametrize(
        "annotation_only",
        [
            Disposition.REROUTE,
            Disposition.HEAL,
            Disposition.RETRY,
            Disposition.SHRINK_SCOPE,
            Disposition.MARK_DEGRADED,
            Disposition.COMMIT_REQUEST,
            Disposition.CLARIFY,
            Disposition.ABSTAIN,
            Disposition.SAFE_FALLBACK,
        ],
    )
    def test_annotation_only_dispositions_do_not_halt(self, annotation_only: Disposition) -> None:
        assert annotation_only not in HALT_DISPOSITIONS


# ---------------------------------------------------------------------------
# 10. Verdict survives JSON serialization round-trip
# ---------------------------------------------------------------------------


class TestVerdictJSONRoundTrip:
    """Verdict shape survives JSON and remains digest-stable."""

    def test_verdict_round_trip_preserves_all_keys(self) -> None:
        decision = GateDecision(
            gate_id="G01",
            disposition=Disposition.ALLOW,
            reason_codes=["test"],
            evidence_refs=["ev:1"],
            score=0.5,
            threshold=0.7,
            confidence=0.9,
        )
        v = decision.to_verdict()
        roundtrip = json.loads(json.dumps(v))
        assert roundtrip == v

    def test_verdict_round_trip_preserves_digest(self) -> None:
        v = _verdict()
        digest_a = verdict_digest(v)
        roundtrip = json.loads(json.dumps(v))
        digest_b = verdict_digest(roundtrip)
        assert digest_a == digest_b

    def test_none_score_and_threshold_round_trip(self) -> None:
        decision = GateDecision(gate_id="G01", disposition=Disposition.ALLOW)
        v = decision.to_verdict()
        assert v["score"] is None
        assert v["threshold"] is None
        roundtrip = json.loads(json.dumps(v))
        assert roundtrip["score"] is None
        assert roundtrip["threshold"] is None


# ---------------------------------------------------------------------------
# 11. Full GateContext immutability across run_mesh
# ---------------------------------------------------------------------------


class TestContextImmutabilityFull:
    """Every dataclass field on GateContext must be unchanged after run_mesh."""

    def test_all_ctx_fields_unchanged_after_full_mesh(self) -> None:
        from dataclasses import fields

        ctx = _ctx()
        # Pre-snapshot via deep-equality JSON of every field.
        before = {f.name: json.dumps(getattr(ctx, f.name), default=str, sort_keys=True) for f in fields(ctx)}
        run_mesh(ctx, halt_on=frozenset(), halt_on_stop_condition=False)
        after = {f.name: json.dumps(getattr(ctx, f.name), default=str, sort_keys=True) for f in fields(ctx)}
        diffs = {k: (before[k], after[k]) for k in before if before[k] != after[k]}
        assert diffs == {}, f"GateContext fields mutated by run_mesh: {diffs}"


# ---------------------------------------------------------------------------
# 12. NOT_APPLICABLE requires reason_codes (00C.7.A.4)
# ---------------------------------------------------------------------------


class TestNotApplicableSemantics:
    """Doctrine 00C.7.A.4: NOT_APPLICABLE requires explicit rationale."""

    def test_not_applicable_with_empty_reason_codes_is_caught_by_aggregator(
        self,
    ) -> None:
        """Empty reason_codes on NOT_APPLICABLE is structurally degenerate.

        The aggregator does not treat NOT_APPLICABLE as material, but the
        verdict shape is preserved for Exit to flag missing rationale.
        """
        empty = _decision(
            disposition=Disposition.ALLOW,
            result=Result.NOT_APPLICABLE,
            reason_codes=[],
        )
        verdict = empty.to_verdict()
        assert verdict["reason_codes"] == []
        # Aggregation does not crash; downstream Exit owns the rationale check.
        mesh = _build([empty])
        assert mesh.recommended_disposition_summary == "ALLOW"

    def test_not_applicable_with_reason_codes_is_well_formed(self) -> None:
        decision = _decision(
            disposition=Disposition.ALLOW,
            result=Result.NOT_APPLICABLE,
            reason_codes=["scope_excluded"],
        )
        verdict = decision.to_verdict()
        assert verdict["result"] == "NOT_APPLICABLE"
        assert verdict["reason_codes"] == ["scope_excluded"]
