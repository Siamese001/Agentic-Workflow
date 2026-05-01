"""Phase D.1 schema unit tests — ADR-080 §0 / §5 / §11.

Schema-only. No ledger writes, no evaluator calls, no scanner state. Every
test asserts ``runtime_certification_status_after == NOT_CERTIFIED``.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json

import pytest

from tools.runtime_cert.decisions.cert_decision_record import (
    CertificationDecisionRecord,
    DECISION_ID_ALGORITHM,
    EVIDENCE_KIND_BTC,
    EVIDENCE_KIND_FORMAL_EXCEPTION,
    EVIDENCE_KIND_R3,
    EVIDENCE_KIND_SKIPPED,
    EVIDENCE_KINDS,
    NOT_CERTIFIED,
    VERDICTS,
    VERDICT_CERTIFY,
    VERDICT_HOLD,
    VERDICT_REJECT,
    compute_decision_id,
    make_certification_decision_record,
)


# ---------------------------------------------------------------------------
# Helpers — all hashes are 64-hex SHA-256 so __post_init__ accepts them.
# ---------------------------------------------------------------------------


def _h(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


_VALID_KW = dict(
    generated_at_utc="2026-05-01T12:00:00Z",
    app_name="apps_research",
    route_shape="R3_grounded_read",
    manifest_hash=_h("manifest"),
    evidence_kind=EVIDENCE_KIND_R3,
    closeout_report_id="phase_c_closeout/2026-W18.md",
    closeout_report_hash=_h("closeout"),
    trace_observed_n=42,
    trace_observed_success_n=40,
    evidence_rate=40 / 42,
    wilson_lower=0.78,
    z_score=2.1,
    uplift=0.05,
    verdict=VERDICT_CERTIFY,
    failure_reasons=(),
    next_review_utc="2026-05-31T12:00:00Z",
)


def _record(**overrides):
    kw = dict(_VALID_KW)
    kw.update(overrides)
    return make_certification_decision_record(**kw)


# ---------------------------------------------------------------------------
# Constants sanity.
# ---------------------------------------------------------------------------


def test_constants_shape():
    assert NOT_CERTIFIED == "NOT_CERTIFIED"
    assert VERDICTS == frozenset({"certify", "reject", "hold"})
    assert {VERDICT_CERTIFY, VERDICT_REJECT, VERDICT_HOLD} == VERDICTS
    assert EVIDENCE_KINDS == frozenset({"r3", "btc", "formal_exception", "skipped"})
    assert EVIDENCE_KIND_R3 in EVIDENCE_KINDS
    assert EVIDENCE_KIND_BTC in EVIDENCE_KINDS
    assert EVIDENCE_KIND_FORMAL_EXCEPTION in EVIDENCE_KINDS
    assert EVIDENCE_KIND_SKIPPED in EVIDENCE_KINDS
    assert DECISION_ID_ALGORITHM == "sha256-canonical-json-v1"


# ---------------------------------------------------------------------------
# compute_decision_id behavior.
# ---------------------------------------------------------------------------


def test_compute_decision_id_deterministic():
    a = compute_decision_id("apps_research", _h("m"), _h("c"))
    b = compute_decision_id("apps_research", _h("m"), _h("c"))
    assert a == b
    assert len(a) == 64
    assert all(ch in "0123456789abcdef" for ch in a)


def test_compute_decision_id_changes_when_app_name_changes():
    a = compute_decision_id("apps_research", _h("m"), _h("c"))
    b = compute_decision_id("apps_eval", _h("m"), _h("c"))
    assert a != b


def test_compute_decision_id_changes_when_manifest_hash_changes():
    a = compute_decision_id("apps_research", _h("m1"), _h("c"))
    b = compute_decision_id("apps_research", _h("m2"), _h("c"))
    assert a != b


def test_compute_decision_id_changes_when_closeout_hash_changes():
    a = compute_decision_id("apps_research", _h("m"), _h("c1"))
    b = compute_decision_id("apps_research", _h("m"), _h("c2"))
    assert a != b


@pytest.mark.parametrize(
    "args",
    [
        ("", _h("m"), _h("c")),
        ("apps_research", "", _h("c")),
        ("apps_research", _h("m"), ""),
    ],
)
def test_compute_decision_id_rejects_empty(args):
    with pytest.raises(ValueError):
        compute_decision_id(*args)


def test_compute_decision_id_rejects_non_str():
    with pytest.raises(TypeError):
        compute_decision_id(123, _h("m"), _h("c"))  # type: ignore[arg-type]


def test_compute_decision_id_matches_adr_080_canonical_form():
    # Golden vector matching the §0 reference implementation exactly.
    app = "apps_research"
    mh = _h("m")
    ch = _h("c")
    payload = json.dumps(
        {"app_name": app, "manifest_hash": mh, "closeout_report_hash": ch},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    expected = hashlib.sha256(payload).hexdigest()
    assert compute_decision_id(app, mh, ch) == expected


# ---------------------------------------------------------------------------
# CertificationDecisionRecord — happy paths.
# ---------------------------------------------------------------------------


def test_record_accepts_valid_input():
    rec = _record()
    assert isinstance(rec, CertificationDecisionRecord)
    assert rec.runtime_certification_status_before == NOT_CERTIFIED
    assert rec.runtime_certification_status_after == NOT_CERTIFIED
    assert rec.decision_id == compute_decision_id(
        rec.app_name, rec.manifest_hash, rec.closeout_report_hash
    )


def test_record_is_frozen():
    rec = _record()
    with pytest.raises(dataclasses.FrozenInstanceError):
        rec.verdict = VERDICT_REJECT  # type: ignore[misc]


def test_verdict_certify_keeps_status_after_not_certified():
    rec = _record(verdict=VERDICT_CERTIFY)
    assert rec.verdict == VERDICT_CERTIFY
    # ADR-080 §0 invariant — Phase D records decisions, Phase F promotes.
    assert rec.runtime_certification_status_after == NOT_CERTIFIED


@pytest.mark.parametrize("kind", sorted(EVIDENCE_KINDS))
def test_record_accepts_each_evidence_kind(kind):
    rec = _record(evidence_kind=kind)
    assert rec.evidence_kind == kind


@pytest.mark.parametrize("verdict", sorted(VERDICTS))
def test_record_accepts_each_verdict(verdict):
    failure = ("blocker",) if verdict != VERDICT_CERTIFY else ()
    rec = _record(verdict=verdict, failure_reasons=failure)
    assert rec.verdict == verdict


def test_record_accepts_zero_n_zero_success():
    rec = _record(
        trace_observed_n=0,
        trace_observed_success_n=0,
        evidence_rate=0.0,
        wilson_lower=0.0,
        verdict=VERDICT_HOLD,
        failure_reasons=("insufficient_n",),
    )
    assert rec.trace_observed_n == 0


# ---------------------------------------------------------------------------
# Validation — failure cases.
# ---------------------------------------------------------------------------


def test_record_rejects_wrong_decision_id():
    kw = dict(_VALID_KW)
    with pytest.raises(ValueError, match="decision_id"):
        CertificationDecisionRecord(decision_id="0" * 64, **kw)


def test_record_rejects_non_apps_app_name():
    with pytest.raises(ValueError, match="app_name"):
        _record(app_name="research")


def test_record_rejects_invalid_manifest_hash():
    with pytest.raises(ValueError, match="manifest_hash"):
        _record(manifest_hash="not-a-hash")


def test_record_rejects_uppercase_manifest_hash():
    with pytest.raises(ValueError, match="manifest_hash"):
        _record(manifest_hash=_h("m").upper())


def test_record_rejects_invalid_closeout_report_hash():
    with pytest.raises(ValueError, match="closeout_report_hash"):
        _record(closeout_report_hash="abc123")


def test_record_rejects_invalid_verdict():
    with pytest.raises(ValueError, match="verdict"):
        _record(verdict="approve")


def test_record_rejects_invalid_evidence_kind():
    with pytest.raises(ValueError, match="evidence_kind"):
        _record(evidence_kind="static")


def test_record_rejects_success_greater_than_n():
    with pytest.raises(ValueError, match="trace_observed_success_n"):
        _record(trace_observed_n=10, trace_observed_success_n=11)


def test_record_rejects_negative_n():
    with pytest.raises(ValueError, match="trace_observed_n"):
        _record(trace_observed_n=-1, trace_observed_success_n=0)


def test_record_rejects_negative_success_n():
    with pytest.raises(ValueError, match="trace_observed_success_n"):
        _record(trace_observed_n=10, trace_observed_success_n=-1)


@pytest.mark.parametrize("rate", [-0.01, 1.01, 2.0, -1.0])
def test_record_rejects_evidence_rate_out_of_range(rate):
    with pytest.raises(ValueError, match="evidence_rate"):
        _record(evidence_rate=rate)


@pytest.mark.parametrize("wl", [-0.01, 1.01, 2.0, -1.0])
def test_record_rejects_wilson_lower_out_of_range(wl):
    with pytest.raises(ValueError, match="wilson_lower"):
        _record(wilson_lower=wl)


def test_record_rejects_negative_z_score():
    with pytest.raises(ValueError, match="z_score"):
        _record(z_score=-0.01)


def test_record_rejects_failure_reasons_not_tuple():
    # Construct the dataclass directly — the helper coerces list→tuple
    # for ergonomic callers, so we must bypass it to exercise the type
    # invariant on the dataclass itself.
    kw = dict(_VALID_KW)
    kw["failure_reasons"] = ["blocker"]  # type: ignore[assignment]
    decision_id = compute_decision_id(
        kw["app_name"], kw["manifest_hash"], kw["closeout_report_hash"]
    )
    with pytest.raises(TypeError, match="failure_reasons"):
        CertificationDecisionRecord(decision_id=decision_id, **kw)


def test_record_rejects_failure_reasons_non_str_element():
    with pytest.raises(TypeError, match="failure_reasons"):
        _record(failure_reasons=("ok", 7))  # type: ignore[arg-type]


def test_helper_coerces_list_failure_reasons_to_tuple():
    # Ergonomic affordance — list inputs to the helper become tuples.
    rec = _record(
        verdict=VERDICT_REJECT, failure_reasons=["a", "b"]  # type: ignore[arg-type]
    )
    assert rec.failure_reasons == ("a", "b")
    assert isinstance(rec.failure_reasons, tuple)


def test_record_rejects_status_after_not_not_certified():
    with pytest.raises(ValueError, match="runtime_certification_status_after"):
        _record(runtime_certification_status_after="RUNTIME_CERTIFIED")


def test_record_rejects_status_before_not_not_certified():
    with pytest.raises(ValueError, match="runtime_certification_status_before"):
        _record(runtime_certification_status_before="RUNTIME_CERTIFIED")


def test_record_rejects_empty_route_shape():
    with pytest.raises(ValueError, match="route_shape"):
        _record(route_shape="")


def test_record_rejects_empty_generated_at_utc():
    with pytest.raises(ValueError, match="generated_at_utc"):
        _record(generated_at_utc="")


def test_record_rejects_empty_next_review_utc():
    with pytest.raises(ValueError, match="next_review_utc"):
        _record(next_review_utc="")


def test_record_rejects_empty_closeout_report_id():
    with pytest.raises(ValueError, match="closeout_report_id"):
        _record(closeout_report_id="")


# ---------------------------------------------------------------------------
# Serializers.
# ---------------------------------------------------------------------------


def test_to_dict_round_trip_json_safe():
    rec = _record()
    d = rec.to_dict()
    # Must be JSON-encodable as-is.
    blob = json.dumps(d)
    parsed = json.loads(blob)
    assert parsed["decision_id"] == rec.decision_id
    assert parsed["app_name"] == rec.app_name
    assert parsed["runtime_certification_status_after"] == NOT_CERTIFIED
    # failure_reasons must serialise as a list (tuple is not JSON-native).
    assert isinstance(d["failure_reasons"], list)


def test_to_dict_contains_all_19_fields():
    rec = _record()
    d = rec.to_dict()
    expected = {
        "decision_id",
        "generated_at_utc",
        "app_name",
        "route_shape",
        "manifest_hash",
        "evidence_kind",
        "closeout_report_id",
        "closeout_report_hash",
        "trace_observed_n",
        "trace_observed_success_n",
        "evidence_rate",
        "wilson_lower",
        "z_score",
        "uplift",
        "verdict",
        "failure_reasons",
        "next_review_utc",
        "runtime_certification_status_before",
        "runtime_certification_status_after",
    }
    assert set(d.keys()) == expected


def test_to_json_is_deterministic_sorted():
    rec = _record()
    s1 = rec.to_json()
    s2 = rec.to_json()
    assert s1 == s2
    parsed = json.loads(s1)
    assert parsed["decision_id"] == rec.decision_id
    # sort_keys → keys appear in lexicographic order in the raw text.
    keys_in_order = [
        s1[i + 1 : s1.index('"', i + 2)]
        for i in range(len(s1))
        if s1[i] == "," and s1[i + 1] == '"'
    ]
    # Cheap-but-sufficient check: extracted keys are sorted.
    assert keys_in_order == sorted(keys_in_order)


# ---------------------------------------------------------------------------
# make_certification_decision_record helper.
# ---------------------------------------------------------------------------


def test_helper_computes_decision_id_internally():
    rec = _record()
    expected = compute_decision_id(
        rec.app_name, rec.manifest_hash, rec.closeout_report_hash
    )
    assert rec.decision_id == expected


def test_helper_does_not_evaluate_certification():
    # Caller supplies a clearly-failing metric set with verdict=certify;
    # the helper must still construct without "fixing" the verdict — it's
    # a schema constructor, not an evaluator.
    rec = _record(
        trace_observed_n=10,
        trace_observed_success_n=0,
        evidence_rate=0.0,
        wilson_lower=0.0,
        z_score=0.0,
        uplift=-0.5,
        verdict=VERDICT_CERTIFY,
        failure_reasons=(),
    )
    assert rec.verdict == VERDICT_CERTIFY
    assert rec.evidence_rate == 0.0
    # And status_after is still NOT_CERTIFIED — Phase D never promotes.
    assert rec.runtime_certification_status_after == NOT_CERTIFIED
