"""D3 tests — Production readiness: log mining, holdout split, rubric migration.

Covers:
  D3.1 apps_qna.observability.log_miner (redact_pii, mine_run_log, LogMiner)
  D3.2 apps_qna.config.eval_set_policy (EvalSetPolicy, assign_partition, is_holdout)
  D3.3 apps_qna.config.rubric_migration (check_rubric_roster_alignment, get_judge_class_for_dim)

Plan: .windsurf/plans/apps-qna-spine-deferred-e9c5b3.md D3
"""

from __future__ import annotations

import re

import pytest


# ---------------------------------------------------------------------------
# D3.1 — Log mining + PII redaction
# ---------------------------------------------------------------------------

class TestRedactPii:
    def test_email_redacted(self) -> None:
        from apps_qna.observability.log_miner import redact_pii
        result = redact_pii("contact: user@example.com today")
        assert "[REDACTED_EMAIL]" in result
        assert "user@example.com" not in result

    def test_phone_redacted(self) -> None:
        from apps_qna.observability.log_miner import redact_pii
        result = redact_pii("call 415-555-1234 now")
        assert "415-555-1234" not in result
        assert "[REDACTED_PHONE]" in result

    def test_ssn_redacted(self) -> None:
        from apps_qna.observability.log_miner import redact_pii
        result = redact_pii("ssn: 123-45-6789")
        assert "123-45-6789" not in result
        assert "[REDACTED_SSN]" in result

    def test_no_pii_unchanged(self) -> None:
        from apps_qna.observability.log_miner import redact_pii
        clean = "The interview slug is google-swe-l5"
        assert redact_pii(clean) == clean

    def test_multiple_emails_all_redacted(self) -> None:
        from apps_qna.observability.log_miner import redact_pii
        text = "from: a@b.com to: c@d.org"
        result = redact_pii(text)
        assert "a@b.com" not in result
        assert "c@d.org" not in result

    def test_extra_pattern_applied(self) -> None:
        from apps_qna.observability.log_miner import redact_pii
        text = "employee EMP-12345 submitted"
        result = redact_pii(text, extra_patterns=[(r"EMP-\d+", "[REDACTED_EMP]")])
        assert "EMP-12345" not in result
        assert "[REDACTED_EMP]" in result

    def test_empty_string_safe(self) -> None:
        from apps_qna.observability.log_miner import redact_pii
        assert redact_pii("") == ""


class TestRedactLogRecord:
    def test_nested_email_redacted(self) -> None:
        from apps_qna.observability.log_miner import redact_log_record
        record = {"user": {"email": "x@y.com", "name": "Alice"}}
        result = redact_log_record(record)
        assert "x@y.com" not in str(result)

    def test_list_values_redacted(self) -> None:
        from apps_qna.observability.log_miner import redact_log_record
        record = {"emails": ["a@b.com", "c@d.org"]}
        result = redact_log_record(record)
        assert "a@b.com" not in str(result)

    def test_non_string_values_preserved(self) -> None:
        from apps_qna.observability.log_miner import redact_log_record
        record = {"count": 42, "flag": True, "ratio": 0.9}
        result = redact_log_record(record)
        assert result["count"] == 42
        assert result["flag"] is True


class TestMineRunLog:
    def _full_record(self) -> dict:
        return {
            "interview_slug": "google-swe-l5",
            "route_id": "build_time_compiler",
            "manifest": {"cards": ["c1", "c2", "c3"], "interview_slug": "google-swe-l5"},
            "evidence_contract": {"evidence_sufficiency": "grounded", "producer": "C0.stub"},
            "exit_packet": {"x3_disposition": "ALLOW_FINISH", "reason_codes": []},
            "dim_scores": {"context_recall": 0.9, "context_precision": 0.8},
            "latency_ms": 1234,
        }

    def test_slug_extracted(self) -> None:
        from apps_qna.observability.log_miner import mine_run_log
        m = mine_run_log(self._full_record())
        assert m.interview_slug == "google-swe-l5"

    def test_card_count(self) -> None:
        from apps_qna.observability.log_miner import mine_run_log
        m = mine_run_log(self._full_record())
        assert m.card_count == 3

    def test_latency_ms(self) -> None:
        from apps_qna.observability.log_miner import mine_run_log
        m = mine_run_log(self._full_record())
        assert m.latency_ms == 1234

    def test_dim_scores_extracted(self) -> None:
        from apps_qna.observability.log_miner import mine_run_log
        m = mine_run_log(self._full_record())
        assert m.dim_scores["context_recall"] == pytest.approx(0.9)

    def test_pii_redacted_flag(self) -> None:
        from apps_qna.observability.log_miner import mine_run_log
        m = mine_run_log(self._full_record(), redact=True)
        assert m.pii_redacted is True

    def test_pii_in_slug_redacted(self) -> None:
        from apps_qna.observability.log_miner import mine_run_log
        record = {"interview_slug": "user@email.com-slug"}
        m = mine_run_log(record)
        assert "user@email.com" not in m.interview_slug

    def test_empty_record_safe(self) -> None:
        from apps_qna.observability.log_miner import mine_run_log
        m = mine_run_log({})
        assert m.card_count == 0
        assert m.evidence_sufficiency == "empty"


class TestLogMiner:
    def test_ingest_and_summarise(self) -> None:
        from apps_qna.observability.log_miner import LogMiner
        miner = LogMiner()
        miner.ingest({"exit_packet": {"x3_disposition": "ALLOW_FINISH"}, "latency_ms": 100})
        miner.ingest({"exit_packet": {"x3_disposition": "SAFE_ABSTAIN"}, "latency_ms": 200})
        summary = miner.summarise()
        assert summary.total == 2
        assert summary.allow_finish_count == 1
        assert summary.abstain_count == 1
        assert summary.avg_latency_ms == pytest.approx(150.0)

    def test_empty_batch_summary(self) -> None:
        from apps_qna.observability.log_miner import LogMiner
        miner = LogMiner()
        summary = miner.summarise()
        assert summary.total == 0

    def test_ingest_batch(self) -> None:
        from apps_qna.observability.log_miner import LogMiner
        miner = LogMiner()
        records = [{"latency_ms": i * 10} for i in range(5)]
        metrics = miner.ingest_batch(records)
        assert len(metrics) == 5

    def test_dim_score_means(self) -> None:
        from apps_qna.observability.log_miner import LogMiner
        miner = LogMiner()
        miner.ingest({"dim_scores": {"context_recall": 0.8}})
        miner.ingest({"dim_scores": {"context_recall": 1.0}})
        summary = miner.summarise()
        assert summary.dim_score_means["context_recall"] == pytest.approx(0.9)

    def test_sufficiency_counts(self) -> None:
        from apps_qna.observability.log_miner import LogMiner
        miner = LogMiner()
        for _ in range(3):
            miner.ingest({"evidence_contract": {"evidence_sufficiency": "grounded"}})
        miner.ingest({"evidence_contract": {"evidence_sufficiency": "empty"}})
        summary = miner.summarise()
        assert summary.evidence_sufficiency_counts.get("grounded") == 3
        assert summary.evidence_sufficiency_counts.get("empty") == 1

    def test_records_property(self) -> None:
        from apps_qna.observability.log_miner import LogMiner
        miner = LogMiner()
        miner.ingest({"interview_slug": "test-slug"})
        assert miner.records[0].interview_slug == "test-slug"


# ---------------------------------------------------------------------------
# D3.2 — Holdout eval-set separation
# ---------------------------------------------------------------------------

class TestEvalSetPolicy:
    def test_importable(self) -> None:
        from apps_qna.config.eval_set_policy import EvalSetPolicy, EvalPartition
        p = EvalSetPolicy()
        assert p.dev_ratio + p.holdout_ratio + p.test_ratio == pytest.approx(1.0)

    def test_deterministic_same_slug_same_partition(self) -> None:
        from apps_qna.config.eval_set_policy import EvalSetPolicy
        p = EvalSetPolicy()
        slug = "google-swe-l5"
        assert p.assign(slug) is p.assign(slug)

    def test_all_slugs_get_a_partition(self) -> None:
        from apps_qna.config.eval_set_policy import EvalSetPolicy, EvalPartition
        p = EvalSetPolicy()
        slugs = [f"slug-{i}" for i in range(100)]
        partitions = {p.assign(s) for s in slugs}
        assert all(part in EvalPartition for part in partitions)

    def test_ratio_distribution_roughly_correct(self) -> None:
        from apps_qna.config.eval_set_policy import EvalSetPolicy, EvalPartition
        p = EvalSetPolicy()
        slugs = [f"interview-slug-{i:04d}" for i in range(500)]
        counts = p.partition_counts(slugs)
        dev_fraction = counts["dev"] / 500
        # Allow ±15% tolerance for hash distribution
        assert 0.55 <= dev_fraction <= 0.85

    def test_custom_ratios(self) -> None:
        from apps_qna.config.eval_set_policy import EvalSetPolicy
        p = EvalSetPolicy(dev_ratio=0.5, holdout_ratio=0.3, test_ratio=0.2)
        assert p.dev_ratio == pytest.approx(0.5)

    def test_invalid_ratios_raise(self) -> None:
        from apps_qna.config.eval_set_policy import EvalSetPolicy
        with pytest.raises(ValueError, match="sum to 1.0"):
            EvalSetPolicy(dev_ratio=0.5, holdout_ratio=0.5, test_ratio=0.5)

    def test_negative_ratio_raises(self) -> None:
        from apps_qna.config.eval_set_policy import EvalSetPolicy
        with pytest.raises(ValueError):
            EvalSetPolicy(dev_ratio=-0.1, holdout_ratio=0.6, test_ratio=0.5)

    def test_filter_partition(self) -> None:
        from apps_qna.config.eval_set_policy import EvalSetPolicy, EvalPartition
        p = EvalSetPolicy()
        slugs = [f"s-{i}" for i in range(50)]
        holdout_slugs = p.filter_partition(slugs, EvalPartition.HOLDOUT)
        assert all(p.assign(s) is EvalPartition.HOLDOUT for s in holdout_slugs)

    def test_is_holdout_guard(self) -> None:
        from apps_qna.config.eval_set_policy import EvalSetPolicy, EvalPartition, is_holdout
        p = EvalSetPolicy()
        slugs = [f"check-{i}" for i in range(100)]
        holdout = [s for s in slugs if p.assign(s) is EvalPartition.HOLDOUT]
        for s in holdout:
            assert is_holdout(s, policy=p)
        non_holdout = [s for s in slugs if p.assign(s) is not EvalPartition.HOLDOUT]
        for s in non_holdout:
            assert not is_holdout(s, policy=p)

    def test_assign_partition_convenience(self) -> None:
        from apps_qna.config.eval_set_policy import assign_partition, EvalPartition
        result = assign_partition("any-slug-here")
        assert result in EvalPartition

    def test_salt_change_changes_assignment(self) -> None:
        from apps_qna.config.eval_set_policy import EvalSetPolicy
        p1 = EvalSetPolicy(salt="salt-v1")
        p2 = EvalSetPolicy(salt="salt-v2")
        slugs = [f"slug-{i}" for i in range(50)]
        # At least some slugs should map to different partitions
        diffs = sum(1 for s in slugs if p1.assign(s) != p2.assign(s))
        assert diffs > 0


# ---------------------------------------------------------------------------
# D3.3 — Rubric migration
# ---------------------------------------------------------------------------

class TestRubricMigration:
    def test_importable(self) -> None:
        from apps_qna.config.rubric_migration import (
            check_rubric_roster_alignment,
            get_judge_class_for_dim,
            MigrationReport,
            RubricDimEntry,
        )
        assert callable(check_rubric_roster_alignment)
        assert callable(get_judge_class_for_dim)

    def test_alignment_check_runs(self) -> None:
        from apps_qna.config.rubric_migration import check_rubric_roster_alignment
        report = check_rubric_roster_alignment()
        assert report is not None
        assert isinstance(report.aligned, bool)

    def test_roster_now_aligned_with_rubric(self) -> None:
        from apps_qna.config.rubric_migration import check_rubric_roster_alignment
        report = check_rubric_roster_alignment()
        assert report.aligned, (
            f"Rubric↔roster misaligned. "
            f"missing_in_roster={report.missing_in_roster}, "
            f"missing_in_rubric={report.missing_in_rubric}"
        )

    def test_three_llm_dims_detected(self) -> None:
        from apps_qna.config.rubric_migration import check_rubric_roster_alignment
        report = check_rubric_roster_alignment()
        dim_ids = {d.dimension_id for d in report.llm_dims}
        assert "context_recall" in dim_ids
        assert "context_precision" in dim_ids
        assert "answer_relevancy" in dim_ids

    def test_three_judges_registered(self) -> None:
        from apps_qna.config.rubric_migration import check_rubric_roster_alignment
        report = check_rubric_roster_alignment()
        assert len(report.registered_judges) == 3

    def test_get_judge_class_context_recall(self) -> None:
        from apps_qna.config.rubric_migration import get_judge_class_for_dim
        from apps_qna.engines.judges import ContextRecallJudge
        cls = get_judge_class_for_dim("context_recall")
        assert cls is ContextRecallJudge

    def test_get_judge_class_context_precision(self) -> None:
        from apps_qna.config.rubric_migration import get_judge_class_for_dim
        from apps_qna.engines.judges import ContextPrecisionJudge
        cls = get_judge_class_for_dim("context_precision")
        assert cls is ContextPrecisionJudge

    def test_get_judge_class_answer_relevancy(self) -> None:
        from apps_qna.config.rubric_migration import get_judge_class_for_dim
        from apps_qna.engines.judges import AnswerRelevancyJudge
        cls = get_judge_class_for_dim("answer_relevancy")
        assert cls is AnswerRelevancyJudge

    def test_get_judge_class_unknown_returns_none(self) -> None:
        from apps_qna.config.rubric_migration import get_judge_class_for_dim
        assert get_judge_class_for_dim("nonexistent_dim") is None

    def test_all_dims_present_in_report(self) -> None:
        from apps_qna.config.rubric_migration import check_rubric_roster_alignment
        report = check_rubric_roster_alignment()
        all_ids = {d.dimension_id for d in report.all_dims}
        assert "route_fit" in all_ids
        assert "context_recall" in all_ids

    def test_grader_roster_yaml_updated(self) -> None:
        from pathlib import Path
        roster = Path("apps_qna/config/domain_contract/grader_roster.yaml").read_text()
        assert "context_recall_judge" in roster
        assert "context_precision_judge" in roster
        assert "answer_relevancy_judge" in roster
