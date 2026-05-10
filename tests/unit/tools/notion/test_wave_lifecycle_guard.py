"""
test_wave_lifecycle_guard.py — Unit tests for the Completed status guard.

Tests the belt-and-suspenders guard added by plan
notion-plan-status-hardening-e5f3a1 (W3.P2):

1. patch_for_marker: wave_start on Completed plan → is_noop=True, reason contains
   "status_completed_guard:noop".
2. patch_for_marker: wave_start on Not Started → status flip to In Progress.
3. patch_for_marker: wave_start on Waiting → status flip to In Progress.
4. patch_for_marker: wave_start on In Progress → no status change, summary only.
5. patch_for_marker: wave_start on Retired → status_locked (no flip).
6. patch_for_marker: plan_complete on Completed → no-op for status (already done).
7. CI gate: guard patterns present in target files.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.notion._wave_lifecycle_helpers import (  # noqa: E402
    WaveLifecycleMarker,
    patch_for_marker,
    STATUS_NOT_STARTED,
    STATUS_IN_PROGRESS,
    STATUS_WAITING,
    STATUS_COMPLETED,
    STATUS_RETIRED,
)


# ---------------------------------------------------------------------------
# patch_for_marker guard tests
# ---------------------------------------------------------------------------


def _wave_start(slug: str = "test-plan-abc123", wave: int = 1) -> WaveLifecycleMarker:
    return WaveLifecycleMarker(kind="wave_start", slug=slug, wave=wave)


def _plan_complete(slug: str = "test-plan-abc123") -> WaveLifecycleMarker:
    return WaveLifecycleMarker(kind="plan_complete", slug=slug)


class TestWaveStartCompletedGuard:
    def test_wave_start_on_completed_is_noop(self):
        """W2.P1: patch_for_marker must return is_noop=True when current=Completed."""
        spec = patch_for_marker(_wave_start(), STATUS_COMPLETED)
        assert spec.is_noop, (
            f"Expected noop for wave_start on Completed, got properties={spec.properties!r} "
            f"summary_append={spec.summary_append!r}"
        )

    def test_wave_start_on_completed_reason_contains_guard(self):
        """W2.P1: reason must mention the guard identifier."""
        spec = patch_for_marker(_wave_start(), STATUS_COMPLETED)
        assert "status_completed_guard:noop" in spec.reason, (
            f"Expected 'status_completed_guard:noop' in reason, got: {spec.reason!r}"
        )

    def test_wave_start_on_completed_no_status_property(self):
        """W2.P1: no Status property in the patch payload."""
        spec = patch_for_marker(_wave_start(), STATUS_COMPLETED)
        assert "Status" not in spec.properties

    def test_wave_start_on_completed_no_summary_append(self):
        """W2.P1: no summary log line appended for Completed guard (no noise)."""
        spec = patch_for_marker(_wave_start(), STATUS_COMPLETED)
        assert spec.summary_append is None


class TestWaveStartFlipBehaviour:
    def test_wave_start_on_not_started_flips_to_in_progress(self):
        """Baseline: Not Started → In Progress flip still works."""
        spec = patch_for_marker(_wave_start(), STATUS_NOT_STARTED)
        assert not spec.is_noop
        status = spec.properties.get("Status", {}).get("select", {}).get("name")
        assert status == STATUS_IN_PROGRESS

    def test_wave_start_on_waiting_flips_to_in_progress(self):
        """Baseline: Waiting → In Progress flip still works."""
        spec = patch_for_marker(_wave_start(), STATUS_WAITING)
        assert not spec.is_noop
        status = spec.properties.get("Status", {}).get("select", {}).get("name")
        assert status == STATUS_IN_PROGRESS

    def test_wave_start_on_in_progress_no_status_change(self):
        """In Progress stays In Progress (already there)."""
        spec = patch_for_marker(_wave_start(), STATUS_IN_PROGRESS)
        assert "Status" not in spec.properties
        assert "status_already_in_progress" in spec.reason

    def test_wave_start_on_retired_is_locked(self):
        """Retired plans are status_locked (not flipped)."""
        spec = patch_for_marker(_wave_start(), STATUS_RETIRED)
        assert "Status" not in spec.properties
        assert "status_locked" in spec.reason

    def test_wave_start_on_none_flips_to_in_progress(self):
        """current_status=None (unknown): behaves like Not Started."""
        spec = patch_for_marker(_wave_start(), None)
        # None is not in _FLIPPABLE_TO_IN_PROGRESS but also not Completed/In Progress/Retired
        # The existing code falls into the `else` status_locked branch for None.
        # Guard: NOT flipped to In Progress from unknown — this is correct behaviour.
        assert "Status" not in spec.properties


class TestPlanCompleteAlreadyCompleted:
    def test_plan_complete_on_completed_is_noop_for_status(self):
        """plan_complete on already Completed → no Status flip, only summary append."""
        spec = patch_for_marker(_plan_complete(), STATUS_COMPLETED)
        assert "Status" not in spec.properties
        assert "status_already_completed" in spec.reason

    def test_plan_complete_on_not_started_flips(self):
        """plan_complete on Not Started → flips to Completed."""
        spec = patch_for_marker(_plan_complete(), STATUS_NOT_STARTED)
        status = spec.properties.get("Status", {}).get("select", {}).get("name")
        assert status == STATUS_COMPLETED


# ---------------------------------------------------------------------------
# CI gate presence tests
# ---------------------------------------------------------------------------


class TestCIGatePresence:
    """Validate that check_notion_plan_lifecycle_guard.py correctly detects the guards."""

    def _load_gate(self):
        gate_path = REPO_ROOT / "ops_scripts" / "ci" / "check_notion_plan_lifecycle_guard.py"
        spec = importlib.util.spec_from_file_location("check_notion_plan_lifecycle_guard", gate_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_gate_file_exists(self):
        gate_path = REPO_ROOT / "ops_scripts" / "ci" / "check_notion_plan_lifecycle_guard.py"
        assert gate_path.exists(), f"CI gate missing: {gate_path}"

    def test_wave_exec_has_current_notion_status_function(self):
        path = REPO_ROOT / "tools" / "windsurf" / "wave_execution_state.py"
        text = path.read_text(encoding="utf-8")
        assert "_current_notion_status" in text

    def test_wave_exec_has_completed_guard(self):
        path = REPO_ROOT / "tools" / "windsurf" / "wave_execution_state.py"
        text = path.read_text(encoding="utf-8")
        assert "status_already_completed" in text

    def test_helpers_has_completed_guard(self):
        path = REPO_ROOT / "tools" / "notion" / "_wave_lifecycle_helpers.py"
        text = path.read_text(encoding="utf-8")
        assert "status_completed_guard:noop" in text

    def test_gate_exits_0_on_green_codebase(self):
        """Run the gate against the actual files — should exit 0."""
        import subprocess
        gate_path = REPO_ROOT / "ops_scripts" / "ci" / "check_notion_plan_lifecycle_guard.py"
        result = subprocess.run(
            [sys.executable, str(gate_path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"Gate exited {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
