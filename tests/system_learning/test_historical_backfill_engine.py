"""
test_historical_backfill_engine.py — Tests for Wave 3 historical backfill.

Covers:
- backfill_protected_root_blocks: JSONL → corpus dedup + content
- backfill_compliance_success_rates: compliance JSON → HealingSuccessRateStore
- run_backfill: sentinel idempotency, dry_run, force
- _ssot_meta_learning wiring: import + call present in source
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_records_execution_trace,
    emit_determinism_digest,
)

emit_determinism_digest("p0", "test_historical_backfill_engine")
_emit_records_execution_trace("p0", "evidence", "test_historical_backfill_engine")

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo(tmp_path):
    """Minimal fake repo root with both source artifacts."""
    # ssot_protected_root_blocks.jsonl
    blocks_dir = tmp_path / ".healing_backups" / "unmapped_drift" / "logs"
    blocks_dir.mkdir(parents=True)
    records = [
        {
            "caller": "mutation_prohibition:enforce_protected_root",
            "matched_root": "agentic_core",
            "target": "C:\\Git\\agentic_core\\test_file.py",
            "ts_utc": "2026-02-21T21:47:31+00:00",
        },
        {
            "caller": "mutation_prohibition:enforce_protected_root",
            "matched_root": "tests",
            "target": "C:\\Git\\tests\\test_file.py",
            "ts_utc": "2026-02-21T21:47:32+00:00",
        },
        {
            "caller": "mutation_prohibition:enforce_protected_root",
            "matched_root": "agentic_core",
            "target": "C:\\Git\\agentic_core\\other.py",
            "ts_utc": "2026-02-21T21:47:33+00:00",
        },
    ]
    (blocks_dir / "ssot_protected_root_blocks.jsonl").write_text(
        "\n".join(json.dumps(r) for r in records), encoding="utf-8"
    )

    # compliance_report_*.json
    reports_dir = tmp_path / ".healing_backups" / "filesystem_ssot_violations" / "logs" / "compliance_reports"
    reports_dir.mkdir(parents=True)
    for territory, total, fixed in [("agentic_core", 100, 60), ("tests", 50, 10), ("apps_lic", 0, 0)]:
        report = {
            "meta": {"territory": territory, "timestamp": "2026-03-03T12:00:00", "status": "NON-COMPLIANT"},
            "metrics": {"violation_count": total, "violations_fixed": fixed, "confidence_score": 0.5},
        }
        (reports_dir / f"compliance_report_{territory}.json").write_text(json.dumps(report), encoding="utf-8")
    # AGGREGATE should be skipped
    (reports_dir / "compliance_report_AGGREGATE.json").write_text(
        json.dumps(
            {"meta": {"territory": "ALL"}, "metrics": {"violation_count": 150, "violations_fixed": 70}}
        ),
        encoding="utf-8",
    )

    # corpus dir
    corpus_dir = tmp_path / "data" / "corpus"
    corpus_dir.mkdir(parents=True)
    (corpus_dir / "healing_contexts_corpus.jsonl").write_text("", encoding="utf-8")

    return tmp_path


# ===========================================================================
# backfill_protected_root_blocks
# ===========================================================================


class TestBackfillProtectedRootBlocks:
    def test_writes_correct_number_of_records(self, repo):
        from system_learning.engines.historical_backfill_engine import backfill_protected_root_blocks

        count = backfill_protected_root_blocks(repo)
        assert count == 3

    def test_corpus_has_expected_entries(self, repo):
        from system_learning.engines.historical_backfill_engine import backfill_protected_root_blocks

        backfill_protected_root_blocks(repo)
        corpus = (repo / "data/corpus/healing_contexts_corpus.jsonl").read_text(encoding="utf-8")
        lines = [json.loads(l) for l in corpus.strip().splitlines() if l.strip()]
        assert len(lines) == 3
        territories = {l["territory"] for l in lines}
        assert "agentic_core" in territories
        assert "tests" in territories

    def test_entry_schema_correct(self, repo):
        from system_learning.engines.historical_backfill_engine import backfill_protected_root_blocks

        backfill_protected_root_blocks(repo)
        corpus = (repo / "data/corpus/healing_contexts_corpus.jsonl").read_text(encoding="utf-8")
        entry = json.loads(corpus.strip().splitlines()[0])
        assert entry["namespace"] == "healing_contexts"
        assert entry["failure_type"] == "PROTECTED_ROOT_BLOCK"
        assert entry["outcome"] == "BLOCKED"
        assert entry["tier"] == "L5"
        assert "content_hash" in entry
        assert "healer_id" in entry

    def test_idempotent_second_run(self, repo):
        from system_learning.engines.historical_backfill_engine import backfill_protected_root_blocks

        count1 = backfill_protected_root_blocks(repo)
        count2 = backfill_protected_root_blocks(repo)
        assert count1 == 3
        assert count2 == 0  # all already present

    def test_dry_run_does_not_write(self, repo):
        from system_learning.engines.historical_backfill_engine import backfill_protected_root_blocks

        count = backfill_protected_root_blocks(repo, dry_run=True)
        assert count == 3
        corpus = (repo / "data/corpus/healing_contexts_corpus.jsonl").read_text(encoding="utf-8")
        assert corpus.strip() == ""

    def test_missing_source_returns_zero(self, tmp_path):
        from system_learning.engines.historical_backfill_engine import backfill_protected_root_blocks

        (tmp_path / "data" / "corpus").mkdir(parents=True)
        result = backfill_protected_root_blocks(tmp_path)
        assert result == 0

    def test_content_hash_stable(self, repo):
        from system_learning.engines.historical_backfill_engine import backfill_protected_root_blocks

        backfill_protected_root_blocks(repo)
        corpus = (repo / "data/corpus/healing_contexts_corpus.jsonl").read_text(encoding="utf-8")
        hashes = [json.loads(l)["content_hash"] for l in corpus.strip().splitlines()]
        # All hashes unique
        assert len(set(hashes)) == len(hashes)


# ===========================================================================
# backfill_compliance_success_rates
# ===========================================================================


class TestBackfillComplianceSuccessRates:
    def _make_store(self):
        from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore

        return HealingSuccessRateStore()

    def test_returns_territories_dict(self, repo):
        from system_learning.engines.historical_backfill_engine import backfill_compliance_success_rates

        store = self._make_store()
        result = backfill_compliance_success_rates(repo, store=store)
        assert "agentic_core" in result
        assert "tests" in result

    def test_zero_violation_territory_skipped(self, repo):
        from system_learning.engines.historical_backfill_engine import backfill_compliance_success_rates

        store = self._make_store()
        result = backfill_compliance_success_rates(repo, store=store)
        # apps_lic has 0 violations — must be skipped
        assert "apps_lic" not in result

    def test_aggregate_report_skipped(self, repo):
        from system_learning.engines.historical_backfill_engine import backfill_compliance_success_rates

        store = self._make_store()
        result = backfill_compliance_success_rates(repo, store=store)
        assert "ALL" not in result

    def test_rates_correct(self, repo):
        from system_learning.engines.historical_backfill_engine import backfill_compliance_success_rates

        store = self._make_store()
        result = backfill_compliance_success_rates(repo, store=store)
        assert abs(result["agentic_core"] - 0.60) < 1e-9
        assert abs(result["tests"] - 0.20) < 1e-9

    def test_store_has_priors_after_seeding(self, repo):
        from system_learning.engines.historical_backfill_engine import backfill_compliance_success_rates

        store = self._make_store()
        backfill_compliance_success_rates(repo, store=store)
        all_rates = store.get_all()
        assert any("agentic_core" in k for k in all_rates)

    def test_dry_run_does_not_seed_store(self, repo):
        from system_learning.engines.historical_backfill_engine import backfill_compliance_success_rates

        store = self._make_store()
        backfill_compliance_success_rates(repo, store=store, dry_run=True)
        assert store.get_all() == {}

    def test_missing_reports_dir_returns_empty(self, tmp_path):
        from system_learning.engines.historical_backfill_engine import backfill_compliance_success_rates

        store = self._make_store()
        result = backfill_compliance_success_rates(tmp_path, store=store)
        assert result == {}


# ===========================================================================
# run_backfill (orchestrator)
# ===========================================================================


class TestRunBackfill:
    def test_first_run_not_skipped(self, repo):
        from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore
        from system_learning.engines.historical_backfill_engine import run_backfill

        store = HealingSuccessRateStore()
        result = run_backfill(repo, store=store)
        assert result["skipped"] is False
        assert result["corpus_records_added"] == 3
        assert len(result["territories_seeded"]) == 2

    def test_sentinel_written_after_first_run(self, repo):
        from system_learning.engines.historical_backfill_engine import run_backfill

        run_backfill(repo)
        sentinel = repo / "data/corpus/.healing_backups_backfill_done"
        assert sentinel.exists()

    def test_second_run_skipped_via_sentinel(self, repo):
        from system_learning.engines.historical_backfill_engine import run_backfill

        run_backfill(repo)
        result2 = run_backfill(repo)
        assert result2["skipped"] is True
        assert result2["corpus_records_added"] == 0

    def test_force_reruns_despite_sentinel(self, repo):
        from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore
        from system_learning.engines.historical_backfill_engine import run_backfill

        run_backfill(repo)
        # Force re-run — corpus already has all records so count = 0
        store = HealingSuccessRateStore()
        result2 = run_backfill(repo, store=store, force=True)
        assert result2["skipped"] is False

    def test_dry_run_no_sentinel(self, repo):
        from system_learning.engines.historical_backfill_engine import run_backfill

        run_backfill(repo, dry_run=True)
        sentinel = repo / "data/corpus/.healing_backups_backfill_done"
        assert not sentinel.exists()


# ===========================================================================
# Wiring: _ssot_meta_learning imports and calls backfill engine
# ===========================================================================


class TestMetaLearningWiring:
    def test_ssot_meta_learning_imports_backfill(self):
        repo_root = Path(__file__).resolve().parents[2]
        src = (repo_root / "agentic_core/L0_routing/scripts/_ssot_meta_learning.py").read_text(
            encoding="utf-8"
        )
        assert "historical_backfill_engine" in src, (
            "_ssot_meta_learning.py must import historical_backfill_engine"
        )
        assert "run_backfill" in src, "_ssot_meta_learning.py must call run_backfill"

    def test_backfill_call_is_sentinel_guarded(self):
        repo_root = Path(__file__).resolve().parents[2]
        src = (repo_root / "system_learning/engines/historical_backfill_engine.py").read_text(
            encoding="utf-8"
        )
        assert "_SENTINEL_PATH" in src, (
            "historical_backfill_engine.py must define _SENTINEL_PATH for idempotency"
        )
        assert "sentinel.exists()" in src, "run_backfill must check sentinel before running"

    def test_backfill_degradation_is_silent(self):
        repo_root = Path(__file__).resolve().parents[2]
        src = (repo_root / "agentic_core/L0_routing/scripts/_ssot_meta_learning.py").read_text(
            encoding="utf-8"
        )
        assert "allow-silent-degradation" in src, (
            "backfill call in _ssot_meta_learning.py must have guardian allow-silent-degradation"
        )
