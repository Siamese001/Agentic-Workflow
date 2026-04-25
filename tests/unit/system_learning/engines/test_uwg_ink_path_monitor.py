"""W9 tests for ``system_learning.engines.uwg_ink_path_monitor``."""

from __future__ import annotations

from pathlib import Path

import pytest

from system_learning.engines.uwg_ink_path_monitor import (
    detect_non_uwg_writers,
    publish_uwg_uniqueness_kpi,
)
from system_learning.engines.v6_kpi_board import V6KPIBoard, V6KPIName


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    (tmp_path / "system_learning" / "engines").mkdir(parents=True)
    (tmp_path / "system_learning" / "engines" / "l4_state_writer.py").write_text(
        "# canonical UWG writer\n", encoding="utf-8"
    )
    return tmp_path


class TestDetectNonUwgWriters:
    def test_canonical_only_returns_empty(self, fake_repo: Path):
        assert detect_non_uwg_writers(fake_repo) == ()

    def test_offender_in_other_layer_detected(self, fake_repo: Path):
        offender_dir = fake_repo / "agentic_core" / "L4_state"
        offender_dir.mkdir(parents=True)
        (offender_dir / "l4_state_writer_shadow.py").write_text("# rogue\n")
        result = detect_non_uwg_writers(fake_repo)
        assert result == ("agentic_core/L4_state/l4_state_writer_shadow.py",)

    def test_archives_excluded(self, fake_repo: Path):
        archive_dir = fake_repo / "archives" / "old"
        archive_dir.mkdir(parents=True)
        (archive_dir / "l4_state_writer_v1.py").write_text("# archived\n")
        assert detect_non_uwg_writers(fake_repo) == ()

    def test_tests_excluded(self, fake_repo: Path):
        test_dir = fake_repo / "tests" / "unit"
        test_dir.mkdir(parents=True)
        (test_dir / "l4_state_writer_stub.py").write_text("# stub\n")
        assert detect_non_uwg_writers(fake_repo) == ()

    def test_multiple_offenders_sorted(self, fake_repo: Path):
        (fake_repo / "apps_eval").mkdir()
        (fake_repo / "apps_eval" / "l4_state_writer_eval.py").write_text("")
        (fake_repo / "tools").mkdir()
        (fake_repo / "tools" / "l4_state_writer_tool.py").write_text("")
        result = detect_non_uwg_writers(fake_repo)
        assert result == (
            "apps_eval/l4_state_writer_eval.py",
            "tools/l4_state_writer_tool.py",
        )

    def test_nonexistent_repo_returns_empty(self, tmp_path: Path):
        ghost = tmp_path / "does_not_exist"
        assert detect_non_uwg_writers(ghost) == ()

    def test_custom_exclude_prefixes(self, fake_repo: Path):
        custom_dir = fake_repo / "custom_archive"
        custom_dir.mkdir()
        (custom_dir / "l4_state_writer_legacy.py").write_text("")
        # Default excludes don't cover custom_archive — must be detected.
        assert "custom_archive/l4_state_writer_legacy.py" in detect_non_uwg_writers(
            fake_repo
        )
        # With custom exclude prefix — filtered out.
        assert (
            detect_non_uwg_writers(
                fake_repo, exclude_prefixes=("custom_archive/",)
            )
            == ()
        )


class TestPublishKpi:
    def test_clean_repo_records_zero(self, fake_repo: Path):
        board = V6KPIBoard()
        count = publish_uwg_uniqueness_kpi(fake_repo, board)
        assert count == 0
        sample = board.latest(V6KPIName.UWG_INK_PATH_UNIQUENESS)
        assert sample is not None
        assert sample.value == 0.0

    def test_offender_records_correct_count(self, fake_repo: Path):
        (fake_repo / "shadow").mkdir()
        (fake_repo / "shadow" / "l4_state_writer_rogue.py").write_text("")
        board = V6KPIBoard()
        count = publish_uwg_uniqueness_kpi(fake_repo, board)
        assert count == 1
        sample = board.latest(V6KPIName.UWG_INK_PATH_UNIQUENESS)
        assert sample.value == 1.0
        assert sample.source == "surface_isolation_validator"

    def test_real_repo_is_clean(self):
        """Sanity: the actual repo must currently report zero offenders.

        This is the runtime mirror of the W2 invariant test; both must
        agree at all times.
        """
        repo_root = Path(__file__).resolve().parents[4]
        offenders = detect_non_uwg_writers(repo_root)
        assert offenders == (), (
            f"UWG sole-ink-path invariant breached: {offenders}"
        )
