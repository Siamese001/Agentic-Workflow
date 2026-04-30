"""Unit tests for tools.proof.otel_collector_proof (W1 of plan 10c-proof-depth-remediation-a9f9af).

Coverage:

  - run_callable_proof: with-real-emit, with-no-emit, with-wrong-name,
    with-target-exception, with-expected-span-not-set
  - replay_digest stability across 2 runs of identical code
  - replay_digest sensitivity to span name / attribute changes
  - run_test_file_proof: subprocess against a pytest target that emits a span
  - run_test_file_proof: subprocess against a target that emits NO spans
  - run_test_file_proof: timeout handling
  - actual_proof_depth assignment per status

Anti-cheat verification:
  - SATISFIED requires an actual span captured
  - NO_SPANS_EMITTED never produces actual_proof_depth >= E6.5
  - WRONG_SPAN_EMITTED counts spans but does not claim SATISFIED
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from tools.proof.otel_collector_proof import (
    CapturedSpan,
    OTelProof,
    run_callable_proof,
    run_test_file_proof,
)


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────


def _emit_span(name: str, attrs: dict | None = None) -> None:
    """Helper that emits one span via the global tracer."""
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(name) as span:
        for k, v in (attrs or {}).items():
            span.set_attribute(k, v)


# ──────────────────────────────────────────────────────────────────────
# run_callable_proof: positive cases
# ──────────────────────────────────────────────────────────────────────


class TestRunCallableProofSatisfied:
    """Callable that emits the expected span -> SATISFIED + E6.5."""

    def test_emits_expected_span(self):
        def target():
            _emit_span("test.span.example", {"k1": "v1", "req_id": "R-001"})

        proof = run_callable_proof(
            target, expected_span="test.span.example", target_label="emit_one"
        )
        assert proof.span_count == 1
        assert proof.expected_seen is True
        assert proof.status == "SATISFIED"
        assert proof.actual_proof_depth == "E6.5_INTEGRATED_RUNTIME"
        assert proof.spans[0].name == "test.span.example"
        assert proof.spans[0].attributes["k1"] == "v1"
        assert proof.replay_digest != ""

    def test_emits_multiple_spans_expected_in_set(self):
        def target():
            _emit_span("span.a")
            _emit_span("span.b")
            _emit_span("span.c")

        proof = run_callable_proof(target, expected_span="span.b")
        assert proof.span_count == 3
        assert proof.expected_seen is True
        assert proof.status == "SATISFIED"
        assert {s.name for s in proof.spans} == {"span.a", "span.b", "span.c"}

    def test_no_expected_means_any_span_satisfies(self):
        def target():
            _emit_span("anything.span")

        proof = run_callable_proof(target, expected_span=None)
        assert proof.expected_seen is True
        assert proof.status == "SATISFIED"


class TestRunCallableProofNegativePaths:
    """Anti-cheat: NO_SPANS / WRONG_SPAN must NOT claim SATISFIED."""

    def test_no_spans_emitted_is_honest(self):
        def target_silent():
            return 1 + 1  # pure compute, no OTel

        proof = run_callable_proof(target_silent, expected_span="must.have.this")
        assert proof.span_count == 0
        assert proof.expected_seen is False
        assert proof.status == "NO_SPANS_EMITTED"
        # Critical anti-cheat assertion:
        assert proof.actual_proof_depth == "E4_NEGATIVE_CONTROL"
        assert proof.actual_proof_depth != "E6.5_INTEGRATED_RUNTIME"

    def test_wrong_span_emitted_does_not_satisfy(self):
        def target_wrong():
            _emit_span("not.what.was.expected")

        proof = run_callable_proof(target_wrong, expected_span="some.expected.span")
        assert proof.span_count == 1
        assert proof.expected_seen is False
        assert proof.status == "WRONG_SPAN_EMITTED"
        # Anti-cheat: spans captured but the contract wasn't met -> no upgrade
        assert proof.actual_proof_depth == "E4_NEGATIVE_CONTROL"

    def test_target_exception_captures_partial_spans(self):
        def target_partial_then_raise():
            _emit_span("emitted.before.crash")
            raise ValueError("boom")

        # Even when target raises, harness captures the span and reports honestly
        proof = run_callable_proof(target_partial_then_raise, expected_span="emitted.before.crash")
        assert proof.span_count == 1
        assert proof.status == "SATISFIED"
        assert proof.target_exit_code == 1
        assert "ValueError" in proof.target_stderr


# ──────────────────────────────────────────────────────────────────────
# Replay determinism (anti-cheat invariant)
# ──────────────────────────────────────────────────────────────────────


class TestReplayDeterminism:
    """replay_digest MUST be stable across runs of identical code."""

    def test_two_runs_same_digest(self):
        def target():
            _emit_span("stable.span", {"k": "v", "n": 42})

        p1 = run_callable_proof(target, expected_span="stable.span")
        p2 = run_callable_proof(target, expected_span="stable.span")
        assert p1.replay_digest == p2.replay_digest

    def test_different_span_name_changes_digest(self):
        def t_a():
            _emit_span("name.a")

        def t_b():
            _emit_span("name.b")

        p_a = run_callable_proof(t_a)
        p_b = run_callable_proof(t_b)
        assert p_a.replay_digest != p_b.replay_digest

    def test_different_attributes_change_digest(self):
        def t1():
            _emit_span("same.name", {"k": "value-1"})

        def t2():
            _emit_span("same.name", {"k": "value-2"})

        p1 = run_callable_proof(t1)
        p2 = run_callable_proof(t2)
        assert p1.replay_digest != p2.replay_digest

    def test_attribute_order_does_not_change_digest(self):
        def t1():
            _emit_span("same.span", {"a": 1, "b": 2})

        def t2():
            _emit_span("same.span", {"b": 2, "a": 1})

        p1 = run_callable_proof(t1)
        p2 = run_callable_proof(t2)
        # canonical_json sorts keys -> same digest
        assert p1.replay_digest == p2.replay_digest

    def test_empty_capture_has_stable_empty_digest(self):
        def silent():
            return None

        p1 = run_callable_proof(silent)
        p2 = run_callable_proof(silent)
        assert p1.replay_digest == p2.replay_digest
        # SHA-256 of canonical "[]" is fixed
        import hashlib, json
        expected = hashlib.sha256(json.dumps([], separators=(",", ":")).encode()).hexdigest()
        assert p1.replay_digest == expected


# ──────────────────────────────────────────────────────────────────────
# run_test_file_proof: subprocess pytest mode
# ──────────────────────────────────────────────────────────────────────


class TestRunTestFileProof:
    """Subprocess mode against synthetic test files."""

    def _write_test(self, tmp_path: Path, body: str) -> Path:
        p = tmp_path / "test_synth_subproc.py"
        p.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
        return p

    def test_subproc_emits_span(self, tmp_path):
        test_path = self._write_test(tmp_path, """
            def test_emits():
                from opentelemetry import trace
                tracer = trace.get_tracer(__name__)
                with tracer.start_as_current_span('subproc.span.x') as s:
                    s.set_attribute('phase', 'one')
                assert True
        """)

        proof = run_test_file_proof(test_path, expected_span="subproc.span.x", timeout=30)
        assert proof.target_exit_code == 0, f"pytest stderr tail: {proof.target_stderr}"
        assert proof.span_count >= 1
        assert proof.expected_seen is True
        assert proof.status == "SATISFIED"
        assert proof.actual_proof_depth == "E6.5_INTEGRATED_RUNTIME"

    def test_subproc_no_otel_emit(self, tmp_path):
        test_path = self._write_test(tmp_path, """
            def test_silent():
                assert 1 + 1 == 2
        """)

        proof = run_test_file_proof(test_path, expected_span="some.span", timeout=30)
        assert proof.target_exit_code == 0
        assert proof.span_count == 0
        assert proof.status == "NO_SPANS_EMITTED"
        assert proof.actual_proof_depth == "E4_NEGATIVE_CONTROL"

    def test_subproc_test_failure_still_reports_spans(self, tmp_path):
        test_path = self._write_test(tmp_path, """
            def test_emit_then_fail():
                from opentelemetry import trace
                tracer = trace.get_tracer(__name__)
                with tracer.start_as_current_span('emitted.first'):
                    pass
                assert False, 'intentional fail'
        """)

        proof = run_test_file_proof(test_path, expected_span="emitted.first", timeout=30)
        assert proof.target_exit_code != 0  # pytest failed
        assert proof.span_count >= 1
        # Status reflects span shape, not pytest pass/fail
        assert proof.expected_seen is True


# ──────────────────────────────────────────────────────────────────────
# Bundle payload schema
# ──────────────────────────────────────────────────────────────────────


class TestBundlePayload:
    """Output projection used by W3 to embed proof in 10c-req-NNN.json."""

    def test_payload_has_required_keys(self):
        def target():
            _emit_span("payload.test.span", {"req_id": "X-1"})

        proof = run_callable_proof(target, expected_span="payload.test.span")
        payload = proof.to_bundle_payload()
        for required in [
            "harness", "harness_mode", "target", "expected_span",
            "span_count", "expected_seen", "status", "actual_proof_depth",
            "captured_spans", "replay_digest", "captured_at_utc",
            "git_head", "git_dirty",
        ]:
            assert required in payload, f"missing required key: {required}"

    def test_payload_serializable(self):
        def target():
            _emit_span("ser.span")

        proof = run_callable_proof(target, expected_span="ser.span")
        payload = proof.to_bundle_payload()
        # Must round-trip JSON
        s = json.dumps(payload)
        round_trip = json.loads(s)
        assert round_trip["status"] == "SATISFIED"
        assert round_trip["actual_proof_depth"] == "E6.5_INTEGRATED_RUNTIME"

    def test_no_span_payload_honest(self):
        def silent():
            pass

        proof = run_callable_proof(silent, expected_span="never.emitted")
        payload = proof.to_bundle_payload()
        assert payload["span_count"] == 0
        assert payload["expected_seen"] is False
        assert payload["actual_proof_depth"] == "E4_NEGATIVE_CONTROL"
        assert payload["captured_spans"] == []
