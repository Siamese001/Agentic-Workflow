"""Integration test: Gap 4 activation path end-to-end.

Seeds a real SQLite HITL ledger with synthetic escalations, invokes the
CLI-exposed `run()` helper, and asserts that:

  1. The pipeline runs without raising
  2. The returned summary reports at least one bucket
  3. At least one `DraftProposal` is written to the sink directory
  4. Each written draft is a valid JSON file with the expected fields

Plan: `.windsurf/plans/system-learning-activation-path-a5e2f1.md`
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    RuntimeHitlLedger,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass
from tools.meta_learning.run_hitl_consumer import run


_SEED_RUN_ID = "test-run-seed"


def _seed_ledger_with_fallback_heavy_pool(
    ledger: RuntimeHitlLedger,
    n_escalations: int = 8,
) -> None:
    """Seed N escalations in a single class/pool, all timed out under one run_id.

    A high timeout rate in one bucket should trigger the consumer to emit
    a TIMEOUT_TIGHTEN and/or FALLBACK_REVIEW draft. All entries share
    `_SEED_RUN_ID` so the engine's `list_by_run` path sees them even after
    resolution (the no-filter path only returns pending entries).
    """
    for i in range(n_escalations):
        entry = ledger.record_escalation(
            run_id=_SEED_RUN_ID,
            trace_id=f"trace-{i:04d}",
            hitl_class=HitlClass.SAFETY,
            approver_pool="test_pool_alpha",
            timeout_s=1800,
            policy_snapshot="policy-v1",
            envelope={"reason": f"test escalation {i}"},
        )
        # Time out every entry to maximize the timeout_rate signal.
        ledger.record_timeout(entry.ledger_id, reason_code="TEST_TIMEOUT")


class TestActivationPipeline:
    def test_run_on_empty_ledger_returns_ok_with_zero_drafts(
        self, tmp_path: Path
    ) -> None:
        ledger_path = tmp_path / "empty_ledger.db"
        draft_dir = tmp_path / "drafts"
        # Touch the ledger by constructing (which creates the DB).
        RuntimeHitlLedger(path=ledger_path)

        summary = run(
            ledger_path=ledger_path,
            draft_dir=draft_dir,
            dry_run=False,
        )
        assert summary["ok"] is True
        assert summary["total_ledger_entries"] == 0
        assert summary["drafts_produced"] == 0
        assert summary["drafts_written"] == 0

    def test_run_on_missing_ledger_returns_ok_false(
        self, tmp_path: Path
    ) -> None:
        summary = run(
            ledger_path=tmp_path / "does_not_exist.db",
            draft_dir=tmp_path / "drafts",
        )
        assert summary["ok"] is False
        assert "ledger_not_found" in summary["reason"]

    def test_seeded_ledger_produces_drafts(self, tmp_path: Path) -> None:
        ledger_path = tmp_path / "seeded_ledger.db"
        draft_dir = tmp_path / "drafts"

        ledger = RuntimeHitlLedger(path=ledger_path)
        _seed_ledger_with_fallback_heavy_pool(ledger, n_escalations=10)

        summary = run(
            ledger_path=ledger_path,
            draft_dir=draft_dir,
            run_id=_SEED_RUN_ID,
            dry_run=False,
        )
        assert summary["ok"] is True
        assert summary["total_ledger_entries"] == 10, summary
        assert summary["resolved_entries"] == 10  # all timed out = resolved
        assert summary["bucket_count"] >= 1
        assert summary["drafts_produced"] >= 1, (
            "high timeout rate should trigger at least one draft proposal"
        )
        assert summary["drafts_written"] == summary["drafts_produced"]

        # Verify draft files exist and are valid JSON with expected shape.
        draft_files = list(draft_dir.glob("*.json"))
        assert len(draft_files) >= 1, f"no draft files written to {draft_dir}"
        for draft_file in draft_files:
            data = json.loads(draft_file.read_text(encoding="utf-8"))
            # Draft JSON must carry the identifying fields the UWG expects.
            assert "draft_id" in data
            assert "kind" in data
            assert "target" in data
            assert "rationale" in data

    def test_dry_run_produces_drafts_without_writing(
        self, tmp_path: Path
    ) -> None:
        ledger_path = tmp_path / "dryrun_ledger.db"
        draft_dir = tmp_path / "drafts"

        ledger = RuntimeHitlLedger(path=ledger_path)
        _seed_ledger_with_fallback_heavy_pool(ledger, n_escalations=10)

        summary = run(
            ledger_path=ledger_path,
            draft_dir=draft_dir,
            run_id=_SEED_RUN_ID,
            dry_run=True,
        )
        assert summary["ok"] is True
        assert summary["drafts_produced"] >= 1
        assert summary["drafts_written"] == 0
        # Dry-run MUST NOT leave JSON artifacts.
        draft_files = list(draft_dir.glob("*.json")) if draft_dir.exists() else []
        assert len(draft_files) == 0


class TestCliMain:
    def test_cli_main_exits_cleanly(self, tmp_path: Path, capsys) -> None:
        """Invoke main() with a seeded ledger; should exit 0 and print a summary."""
        from tools.meta_learning.run_hitl_consumer import main

        ledger_path = tmp_path / "cli_ledger.db"
        draft_dir = tmp_path / "drafts"
        ledger = RuntimeHitlLedger(path=ledger_path)
        _seed_ledger_with_fallback_heavy_pool(ledger, n_escalations=8)

        argv = [
            "--ledger", str(ledger_path),
            "--draft-dir", str(draft_dir),
            "--run-id", _SEED_RUN_ID,
            "--json",
        ]
        rc = main(argv)
        captured = capsys.readouterr()
        assert rc == 0, f"stderr: {captured.err}"
        summary = json.loads(captured.out)
        assert summary["ok"] is True
        assert summary["drafts_produced"] >= 1

    def test_cli_main_missing_ledger_returns_2(
        self, tmp_path: Path, capsys
    ) -> None:
        from tools.meta_learning.run_hitl_consumer import main

        rc = main(["--ledger", str(tmp_path / "nope.db")])
        captured = capsys.readouterr()
        assert rc == 2
        assert "FAIL" in captured.err
