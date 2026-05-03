"""W3.4 contract tests for frontier second-judge pairing.

Covers the three W3 shipping surfaces:
  * ``generate_frontier_rationale`` (W3.1)
  * ``record_pair`` + ``watchdog_verdict`` + ``jaccard_overlap`` (W3.2)
  * ``DecisionPacketAssembler._pair_with_frontier_best_effort`` wire-in (W3.3)

The common autouse fixture in ``conftest.py`` suppresses the Qwen-first
path and keeps pairing disarmed; individual tests re-arm explicitly
and monkey-patch the frontier + tracker collaborators so no live
network I/O is exercised.

Plan: apps-underwriting-ai-activation-e8a3c5 W3.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_underwriting_ai.services import (
    AGREEMENT_THRESHOLD,
    JACCARD_AGREE_THRESHOLD,
    MIN_SAMPLES,
    generate_frontier_rationale,
    jaccard_overlap,
    record_pair,
    watchdog_verdict,
)


# --------------------------------------------------------------------- #
# Jaccard overlap — pure-function tests (deterministic).
# --------------------------------------------------------------------- #


def test_jaccard_empty_inputs_return_zero() -> None:
    assert jaccard_overlap("", "") == 0.0
    assert jaccard_overlap("verdict reflects evidence", "") == 0.0
    assert jaccard_overlap("", "verdict reflects evidence") == 0.0


def test_jaccard_identical_nontrivial_text_returns_one() -> None:
    text = "verdict reflects evidence records reconciled features"
    assert jaccard_overlap(text, text) == 1.0


def test_jaccard_disjoint_texts_return_zero() -> None:
    # Both strings contain ONLY words of length <5 or stopwords — after
    # filtering both yield an empty token set, so Jaccard is 0.0.
    a = "the cat sat on the mat"
    b = "a dog ran up the hill"
    assert jaccard_overlap(a, b) == 0.0


def test_jaccard_partial_overlap_is_between_zero_and_one() -> None:
    a = "approved because evidence records reconcile cleanly across features"
    b = "approved because features reconcile inputs against evidence"
    score = jaccard_overlap(a, b)
    assert 0.0 < score < 1.0


# --------------------------------------------------------------------- #
# generate_frontier_rationale — env-gated fail-soft paths.
# --------------------------------------------------------------------- #


def test_frontier_disabled_by_default_returns_pairing_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_UW_FRONTIER_PAIRING_ENABLED", raising=False)
    text, model, reason = generate_frontier_rationale(
        verdict_value="APPROVE",
        evidence_count=4,
        feature_count=12,
        unresolved=0,
    )
    assert text is None
    assert model == ""
    assert reason == "pairing_disabled"


def test_frontier_armed_but_env_missing_returns_env_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_UW_FRONTIER_PAIRING_ENABLED", "1")
    monkeypatch.delenv("APPS_UW_FRONTIER_JUDGE_MODEL", raising=False)
    monkeypatch.delenv("FRONTIER_API_BASE_URL", raising=False)
    text, _model, reason = generate_frontier_rationale(
        verdict_value="APPROVE",
        evidence_count=4,
        feature_count=12,
        unresolved=0,
    )
    assert text is None
    assert reason == "env_missing"


# --------------------------------------------------------------------- #
# record_pair + watchdog_verdict — rolling Wilson-CI correctness.
# --------------------------------------------------------------------- #


@pytest.fixture()
def _isolated_agreement_log(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Path:
    """Redirect the tracker JSONL to a per-test tmp file."""
    log_path = tmp_path / "rationale_agreement.jsonl"
    monkeypatch.setenv("APPS_UW_AGREEMENT_LOG_PATH", str(log_path))
    return log_path


def test_record_pair_writes_jsonl_row_with_agreed_flag(
    _isolated_agreement_log: Path,
) -> None:
    sample = record_pair(
        request_id="req-1",
        verdict_value="APPROVE",
        qwen_rationale=(
            "Approved because evidence records reconcile cleanly against "
            "derived risk features"
        ),
        frontier_rationale=(
            "Approved because the evidence records reconcile with the "
            "derived risk features"
        ),
        frontier_model="test-frontier-model",
        now=1_700_000_000.0,
    )
    # High overlap → agreed=True.
    assert sample.jaccard >= JACCARD_AGREE_THRESHOLD
    assert sample.agreed is True
    assert sample.frontier_model == "test-frontier-model"

    lines = _isolated_agreement_log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["agreed"] is True
    assert row["verdict"] == "APPROVE"
    assert row["request_id"] == "req-1"


def test_record_pair_disagreement_when_jaccard_below_threshold(
    _isolated_agreement_log: Path,
) -> None:
    sample = record_pair(
        request_id="req-2",
        verdict_value="REFER",
        qwen_rationale=(
            "Referring because several reconciliation unresolved items "
            "require analyst review"
        ),
        frontier_rationale=(
            "Approved because underwriting completed without issues"
        ),
        frontier_model="test-frontier-model",
        now=1_700_000_000.0,
    )
    assert sample.jaccard < JACCARD_AGREE_THRESHOLD
    assert sample.agreed is False


def test_watchdog_insufficient_when_empty_log(
    _isolated_agreement_log: Path,
) -> None:
    verdict = watchdog_verdict(now=1_700_000_000.0)
    assert verdict.state == "INSUFFICIENT"
    assert verdict.interval.n == 0


def test_watchdog_agree_when_all_samples_agreed(
    _isolated_agreement_log: Path,
) -> None:
    now = 1_700_000_000.0
    for i in range(MIN_SAMPLES):
        record_pair(
            request_id=f"req-{i}",
            verdict_value="APPROVE",
            qwen_rationale=(
                "Approved because evidence records reconcile cleanly "
                "against derived risk features"
            ),
            frontier_rationale=(
                "Approved because the evidence records reconcile with "
                "the derived risk features"
            ),
            frontier_model="test-frontier-model",
            now=now - i,
        )
    verdict = watchdog_verdict(now=now)
    # 30 successes / 30 samples → Wilson lower bound >= AGREEMENT_THRESHOLD.
    assert verdict.interval.n == MIN_SAMPLES
    assert verdict.interval.lower >= AGREEMENT_THRESHOLD
    assert verdict.state == "AGREE"


def test_watchdog_disagree_when_mostly_disagreed(
    _isolated_agreement_log: Path,
) -> None:
    now = 1_700_000_000.0
    for i in range(MIN_SAMPLES):
        record_pair(
            request_id=f"req-{i}",
            verdict_value="REFER",
            qwen_rationale="referring pending manual analyst review",
            frontier_rationale=(
                "approved because the underwriting completed cleanly"
            ),
            frontier_model="test-frontier-model",
            now=now - i,
        )
    verdict = watchdog_verdict(now=now)
    assert verdict.interval.n == MIN_SAMPLES
    assert verdict.state == "DISAGREE"


# --------------------------------------------------------------------- #
# Assembler wire-in — compliance-posture floor.
# --------------------------------------------------------------------- #


def test_pair_helper_noop_when_pairing_disabled(
    monkeypatch: pytest.MonkeyPatch, _isolated_agreement_log: Path
) -> None:
    """Default: no record written even after Qwen would have accepted."""
    from apps_underwriting_ai.engines import decision_packet_assembler as dpa
    from apps_underwriting_ai.types.underwriting_types import DecisionVerdict

    monkeypatch.delenv("APPS_UW_FRONTIER_PAIRING_ENABLED", raising=False)
    dpa._pair_with_frontier_best_effort(
        accepted_qwen_text="Approved because records reconcile.",
        verdict=DecisionVerdict.APPROVE,
        evidence_count=3,
        feature_count=9,
        unresolved=0,
    )
    assert not _isolated_agreement_log.exists()


def test_pair_helper_records_when_armed_and_frontier_returns_text(
    monkeypatch: pytest.MonkeyPatch, _isolated_agreement_log: Path
) -> None:
    """Armed + frontier returns text → sample recorded, verdict untouched."""
    from apps_underwriting_ai.engines import decision_packet_assembler as dpa
    from apps_underwriting_ai.types.underwriting_types import DecisionVerdict

    monkeypatch.setenv("APPS_UW_FRONTIER_PAIRING_ENABLED", "1")

    def _fake_frontier(**_kwargs: object) -> tuple[str | None, str, str]:
        return (
            "Approved because the evidence records reconcile cleanly "
            "against the derived risk features",
            "fake-frontier-model",
            "accepted",
        )

    # Patch the symbols the helper imports lazily from apps_underwriting_ai.services.
    import apps_underwriting_ai.services as services_mod

    monkeypatch.setattr(services_mod, "generate_frontier_rationale", _fake_frontier)

    dpa._pair_with_frontier_best_effort(
        accepted_qwen_text=(
            "Approved because evidence records reconcile cleanly against "
            "derived risk features"
        ),
        verdict=DecisionVerdict.APPROVE,
        evidence_count=3,
        feature_count=9,
        unresolved=0,
    )
    assert _isolated_agreement_log.exists()
    rows = [
        json.loads(line)
        for line in _isolated_agreement_log.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    assert len(rows) == 1
    assert rows[0]["agreed"] is True
    assert rows[0]["frontier_model"] == "fake-frontier-model"


def test_pair_helper_silent_when_frontier_raises(
    monkeypatch: pytest.MonkeyPatch, _isolated_agreement_log: Path
) -> None:
    """Compliance floor: frontier call raising MUST NOT propagate."""
    from apps_underwriting_ai.engines import decision_packet_assembler as dpa
    from apps_underwriting_ai.types.underwriting_types import DecisionVerdict

    monkeypatch.setenv("APPS_UW_FRONTIER_PAIRING_ENABLED", "1")

    def _raising(**_kwargs: object) -> tuple[str | None, str, str]:
        raise RuntimeError("simulated frontier gateway 503")

    import apps_underwriting_ai.services as services_mod

    monkeypatch.setattr(services_mod, "generate_frontier_rationale", _raising)

    # MUST NOT raise.
    dpa._pair_with_frontier_best_effort(
        accepted_qwen_text="Approved because records reconcile.",
        verdict=DecisionVerdict.APPROVE,
        evidence_count=3,
        feature_count=9,
        unresolved=0,
    )
    # No sample recorded because frontier errored out.
    assert not _isolated_agreement_log.exists()
