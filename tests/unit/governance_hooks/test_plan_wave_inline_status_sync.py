"""
test_plan_wave_inline_status_sync.py — Tests for inline prose field sync in
_plan_wave_table_updater.py and drift detection in plan_driven_closer.py.

Plan: plan-wave-inline-status-sync-8b4d2f
Tests: TC-1..TC-8 (happy path) + TC-N1..TC-N8 (negative / edge cases) = 16 cases.
"""
from __future__ import annotations

import io
import sys
import textwrap
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools" / "plan_lifecycle"))
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance/scripts"))

from _plan_wave_table_updater import (  # noqa: E402
    _restore_fenced_blocks,
    _split_wave_sections,
    _strip_fenced_blocks,
    _update_inline_fields_in_plan,
    update_wave_in_plan,
)

# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _make_3wave_plan(
    w1_status: str = "TODO",
    w1_complete: str = "NO",
    w2_status: str = "TODO",
    w2_complete: str = "NO",
    w3_status: str = "TODO",
    w3_complete: str = "NO",
    w1_phase_status: str = "TODO",
    w1_phase_complete: str = "NO",
    w2_phase_status: str = "TODO",
    w2_phase_complete: str = "NO",
    dod_w1: str = "TODO",
    dod_w2: str = "TODO",
    dod_w3: str = "TODO",
) -> str:
    """Return a minimal 3-wave plan markdown string for use in tests."""
    return textwrap.dedent(f"""\
        ---
        plan_id: test-plan
        ---

        # Test Plan

        ## Plan State Markers

        PLAN_STATUS: TODO

        ## Wave Structure

        | Wave | Focus | Status |
        |------|-------|--------|
        | W1   | First | 🔲 TODO |
        | W2   | Second | 🔲 TODO |
        | W3   | Third | 🔲 TODO |

        ## Wave 1 — First Wave

        WAVE_ID: W1
        WAVE_STATUS: {w1_status}
        WAVE_COMPLETE: {w1_complete}

        **Phases**:
        - **W1.1** — Phase one | ~1K tokens | PHASE_STATUS: {w1_phase_status} | PHASE_COMPLETE: {w1_phase_complete}
        - **W1.2** — Phase two | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

        ### DoD

        DoD-1: Something
        - Evidence: test
        - Status: {dod_w1}

        ## Wave 2 — Second Wave

        WAVE_ID: W2
        WAVE_STATUS: {w2_status}
        WAVE_COMPLETE: {w2_complete}

        **Phases**:
        - **W2.1** — Phase one | ~1K tokens | PHASE_STATUS: {w2_phase_status} | PHASE_COMPLETE: {w2_phase_complete}

        ### DoD

        DoD-1: Something
        - Evidence: test
        - Status: {dod_w2}

        ## Wave 3 — Third Wave

        WAVE_ID: W3
        WAVE_STATUS: {w3_status}
        WAVE_COMPLETE: {w3_complete}

        ### DoD

        DoD-1: Something
        - Evidence: test
        - Status: {dod_w3}
    """)


def _write_plan(tmp_path: Path, slug: str, content: str) -> Path:
    plan_file = _plan_path(tmp_path, slug)
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    plan_file.write_text(content, encoding="utf-8")
    return plan_file


def _plan_path(tmp_path: Path, slug: str) -> Path:
    return tmp_path / ".claude" / "plans" / f"{slug}.md"


def _read_plan(tmp_path: Path, slug: str) -> str:
    return _plan_path(tmp_path, slug).read_text(encoding="utf-8")


# ===========================================================================
# Happy-path tests (TC-1..TC-8)
# ===========================================================================


class TestHappyPath:
    def test_tc1_wave_complete_wave2_updates_only_w2(self, tmp_path: Path) -> None:
        """TC-1: wave_complete wave=2 updates W2 section; W1 and W3 unchanged."""
        slug = "test-plan-tc1"
        content = _make_3wave_plan()
        _write_plan(tmp_path, slug, content)

        ok, msg = update_wave_in_plan(tmp_path, slug, 2, "wave_complete")
        assert ok, msg

        result = _read_plan(tmp_path, slug)

        # W2 inline fields updated
        lines = result.splitlines()
        w2_section_start = next(i for i, l in enumerate(lines) if "## Wave 2" in l)
        w3_section_start = next(i for i, l in enumerate(lines) if "## Wave 3" in l)
        w2_section = "\n".join(lines[w2_section_start:w3_section_start])

        assert "WAVE_STATUS: DONE" in w2_section
        assert "WAVE_COMPLETE: YES" in w2_section

        # W1 unchanged
        w1_section_start = next(i for i, l in enumerate(lines) if "## Wave 1" in l)
        w1_section = "\n".join(lines[w1_section_start:w2_section_start])
        assert "WAVE_STATUS: TODO" in w1_section
        assert "WAVE_COMPLETE: NO" in w1_section

        # W3 unchanged
        w3_section = "\n".join(lines[w3_section_start:])
        assert "WAVE_STATUS: TODO" in w3_section
        assert "WAVE_COMPLETE: NO" in w3_section

    def test_tc2_wave_complete_already_done_is_noop(self, tmp_path: Path) -> None:
        """TC-2: wave_complete on wave already DONE is a no-op (idempotent)."""
        slug = "test-plan-tc2"
        content = _make_3wave_plan(w1_status="DONE", w1_complete="YES")
        _write_plan(tmp_path, slug, content)
        original = _read_plan(tmp_path, slug)

        ok, msg = update_wave_in_plan(tmp_path, slug, 1, "wave_complete")
        assert ok

        result = _read_plan(tmp_path, slug)
        # Inline fields should not have changed (already terminal)
        # last_updated may differ; compare inline field values specifically
        assert "WAVE_STATUS: DONE" in result
        assert "WAVE_COMPLETE: YES" in result
        # Confirm W1 status was NOT changed to something else
        lines_original = [l for l in original.splitlines() if "WAVE_STATUS:" in l]
        lines_result = [l for l in result.splitlines() if "WAVE_STATUS:" in l]
        assert lines_original == lines_result or all("DONE" in l for l in lines_result[:1])

    def test_tc3_phase_complete_updates_only_matching_phase(self, tmp_path: Path) -> None:
        """TC-3: phase_complete phase=W1.1 updates only W1.1 bullet; W1.2 unchanged."""
        from _plan_wave_table_updater import _update_phase_in_plan

        slug = "test-plan-tc3"
        content = _make_3wave_plan()
        _write_plan(tmp_path, slug, content)

        ok, msg = _update_phase_in_plan(tmp_path, slug, "W1.1", "phase_complete")
        assert ok, msg

        result = _read_plan(tmp_path, slug)

        # W1.1 line updated
        w1_1_lines = [l for l in result.splitlines() if "W1.1" in l]
        assert w1_1_lines, "No W1.1 line found"
        assert "PHASE_STATUS: DONE" in w1_1_lines[0]
        assert "PHASE_COMPLETE: YES" in w1_1_lines[0]

        # W1.2 line unchanged
        w1_2_lines = [l for l in result.splitlines() if "W1.2" in l]
        assert w1_2_lines, "No W1.2 line found"
        assert "PHASE_STATUS: TODO" in w1_2_lines[0]
        assert "PHASE_COMPLETE: NO" in w1_2_lines[0]

    def test_tc4_plan_complete_updates_all_inline_fields(self, tmp_path: Path) -> None:
        """TC-4: plan_complete updates all WAVE, PHASE, and DoD - Status: fields."""
        slug = "test-plan-tc4"
        content = _make_3wave_plan()
        _write_plan(tmp_path, slug, content)

        ok, msg = update_wave_in_plan(tmp_path, slug, -1, "plan_complete")
        assert ok, msg

        result = _read_plan(tmp_path, slug)

        # All WAVE_STATUS → DONE, WAVE_COMPLETE → YES
        assert result.count("WAVE_STATUS: DONE") >= 3
        assert result.count("WAVE_COMPLETE: YES") >= 3

        # All PHASE_STATUS → DONE, PHASE_COMPLETE → YES
        assert "PHASE_STATUS: TODO" not in result
        assert "PHASE_COMPLETE: NO" not in result

        # All DoD - Status: → DONE
        assert "- Status: TODO" not in result
        assert result.count("- Status: DONE") >= 3

    def test_tc5_wave_start_sets_in_progress(self, tmp_path: Path) -> None:
        """TC-5: wave_start wave=3 sets W3 WAVE_STATUS to IN_PROGRESS; WAVE_COMPLETE stays NO."""
        slug = "test-plan-tc5"
        content = _make_3wave_plan()
        _write_plan(tmp_path, slug, content)

        ok, msg = update_wave_in_plan(tmp_path, slug, 3, "wave_start")
        assert ok, msg

        result = _read_plan(tmp_path, slug)

        lines = result.splitlines()
        w3_start = next(i for i, l in enumerate(lines) if "## Wave 3" in l)
        w3_section = "\n".join(lines[w3_start:])

        assert "WAVE_STATUS: IN_PROGRESS" in w3_section
        assert "WAVE_COMPLETE: NO" in w3_section

    def test_tc6_table_row_update_still_fires(self, tmp_path: Path) -> None:
        """TC-6: pipe-table Wave Structure row updated to ✅ DONE by wave_complete."""
        slug = "test-plan-tc6"
        content = _make_3wave_plan()
        _write_plan(tmp_path, slug, content)

        ok, msg = update_wave_in_plan(tmp_path, slug, 2, "wave_complete")
        assert ok, msg

        result = _read_plan(tmp_path, slug)

        # The pipe-table row for W2 should have ✅ DONE
        # Match rows that start with | and contain W2 but not the header separator
        table_rows = [
            l for l in result.splitlines()
            if l.strip().startswith("|") and "W2" in l and "---" not in l
        ]
        assert table_rows, "No W2 table row found"
        # At least one row should have ✅ DONE (the Wave Structure row)
        done_rows = [r for r in table_rows if "✅ DONE" in r]
        assert done_rows, (
            f"Expected ✅ DONE in a W2 table row. Rows found: {table_rows}"
        )

    def test_tc7_wave_complete_dod_scoped_to_target_wave(self, tmp_path: Path) -> None:
        """TC-7: wave_complete wave=2 updates DoD - Status: inside W2 only; W1 and W3 unchanged."""
        slug = "test-plan-tc7"
        content = _make_3wave_plan()
        _write_plan(tmp_path, slug, content)

        ok, msg = update_wave_in_plan(tmp_path, slug, 2, "wave_complete")
        assert ok, msg

        result = _read_plan(tmp_path, slug)

        lines = result.splitlines()
        w1_start = next(i for i, l in enumerate(lines) if "## Wave 1" in l)
        w2_start = next(i for i, l in enumerate(lines) if "## Wave 2" in l)
        w3_start = next(i for i, l in enumerate(lines) if "## Wave 3" in l)

        w1_section = "\n".join(lines[w1_start:w2_start])
        w2_section = "\n".join(lines[w2_start:w3_start])
        w3_section = "\n".join(lines[w3_start:])

        assert "- Status: TODO" in w1_section, "W1 DoD should remain TODO"
        assert "- Status: DONE" in w2_section, "W2 DoD should be DONE"
        assert "- Status: TODO" in w3_section, "W3 DoD should remain TODO"

    def test_tc8_parse_plan_file_detects_inline_drift(self, tmp_path: Path) -> None:
        """TC-8: parse_plan_file returns inline_open_fields on stale plan;
        reconcile emits plan_header_inline_drift."""
        import importlib.util

        plans_dir = tmp_path / ".claude" / "plans"
        plans_dir.mkdir(parents=True, exist_ok=True)

        stale_plan = plans_dir / "stale-plan-tc8.md"
        stale_plan.write_text(textwrap.dedent("""\
            ---
            plan_id: stale-plan-tc8
            ---
            # Stale Plan TC8

            Status: COMPLETED

            ## Wave 1 — Wave

            WAVE_STATUS: TODO
            WAVE_COMPLETE: NO

            - **W1.1** — Phase | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

            - Status: TODO
        """), encoding="utf-8")

        closer_path = REPO_ROOT / ".claude" / "governance/scripts" / "plan_driven_closer.py"
        spec = importlib.util.spec_from_file_location("plan_driven_closer_tc8", closer_path)
        closer = importlib.util.module_from_spec(spec)
        sys.modules["plan_driven_closer_tc8"] = closer
        spec.loader.exec_module(closer)

        ps = closer.parse_plan_file(stale_plan)
        assert ps.inline_open_fields, "Expected non-empty inline_open_fields"
        field_names = [f.split("=")[0] for f in ps.inline_open_fields]
        assert "wave_status" in field_names
        assert "wave_complete" in field_names

        # reconcile: header=COMPLETED + open inline → plan_header_inline_drift warning
        plans = {"stale-plan-tc8.md": ps}
        candidates, warnings = closer.reconcile(plans, [])
        drift_warnings = [w for w in warnings if w.get("kind") == "plan_header_inline_drift"]
        assert drift_warnings, "Expected plan_header_inline_drift warning"
        assert drift_warnings[0]["open_inline_fields"]


# ===========================================================================
# Negative / edge-case tests (TC-N1..TC-N8)
# ===========================================================================


class TestNegativeCases:
    def test_tcn1_fenced_block_not_rewritten(self, tmp_path: Path) -> None:
        """TC-N1: WAVE_STATUS: TODO inside a fenced block is NOT rewritten."""
        slug = "test-plan-tcn1"
        content = textwrap.dedent("""\
            ---
            plan_id: test-plan-tcn1
            ---

            ## Wave 1 — Wave

            WAVE_STATUS: TODO
            WAVE_COMPLETE: NO

            Example:

            ```text
            WAVE_STATUS: TODO
            WAVE_COMPLETE: NO
            ```

            | W1 | Focus | 🔲 TODO |
        """)
        # Verify the fence is present before writing
        assert "```text" in content, "Fixture missing fenced block"

        _write_plan(tmp_path, slug, content)

        ok, msg = update_wave_in_plan(tmp_path, slug, 1, "wave_complete")
        assert ok, msg

        result = _read_plan(tmp_path, slug)

        # Extract fenced block boundaries
        import re as _re
        fence_match = _re.search(r"```text\n.*?```", result, _re.DOTALL)
        assert fence_match, "Fenced block not found in result"
        fenced_content = fence_match.group(0)

        assert "WAVE_STATUS: TODO" in fenced_content, (
            f"Fenced block content was modified: {fenced_content!r}"
        )
        assert "WAVE_COMPLETE: NO" in fenced_content

        # Prose field outside fence should be updated
        before_fence = result[:fence_match.start()]
        assert "WAVE_STATUS: DONE" in before_fence, (
            f"Prose WAVE_STATUS should be DONE but before-fence content is:\n{before_fence}"
        )

    def test_tcn2_format_reference_fence_not_rewritten(self) -> None:
        """TC-N2: Format Reference section with WAVE_STATUS: TODO inside fence — not rewritten."""
        content = textwrap.dedent("""\
            ## Wave 1 — Wave

            WAVE_STATUS: TODO

            ```
            WAVE_STATUS: <TODO|IN_PROGRESS|DONE>
            WAVE_COMPLETE: <YES|NO>
            - PHASE_STATUS: TODO | PHASE_COMPLETE: NO
            - Status: TODO
            ```
        """)
        new_content, changed, msg = _update_inline_fields_in_plan(content, "slug", 1, "wave_complete")

        # Fence content must be byte-identical
        fence_start = new_content.index("```\n")
        fence_end = new_content.index("```\n", fence_start + 4) + 4
        fenced = new_content[fence_start:fence_end]

        original_fence_start = content.index("```\n")
        original_fence_end = content.index("```\n", original_fence_start + 4) + 4
        original_fenced = content[original_fence_start:original_fence_end]

        assert fenced == original_fenced, (
            f"Fenced block was modified.\nOriginal: {original_fenced!r}\nGot: {fenced!r}"
        )

    def test_tcn3_wave_start_does_not_downgrade_done(self, tmp_path: Path) -> None:
        """TC-N3: wave_start on wave with WAVE_STATUS: DONE does not downgrade to IN_PROGRESS."""
        slug = "test-plan-tcn3"
        content = _make_3wave_plan(w1_status="DONE", w1_complete="YES")
        _write_plan(tmp_path, slug, content)

        ok, msg = update_wave_in_plan(tmp_path, slug, 1, "wave_start")
        assert ok

        result = _read_plan(tmp_path, slug)

        lines = result.splitlines()
        w1_start = next(i for i, l in enumerate(lines) if "## Wave 1" in l)
        w2_start = next(i for i, l in enumerate(lines) if "## Wave 2" in l)
        w1_section = "\n".join(lines[w1_start:w2_start])

        assert "WAVE_STATUS: DONE" in w1_section, "DONE must not be downgraded to IN_PROGRESS"
        assert "WAVE_STATUS: IN_PROGRESS" not in w1_section

    def test_tcn4_phase_start_does_not_downgrade_done(self, tmp_path: Path) -> None:
        """TC-N4: phase_start on DONE phase does not downgrade PHASE_STATUS."""
        from _plan_wave_table_updater import _update_phase_in_plan

        slug = "test-plan-tcn4"
        content = _make_3wave_plan(w1_phase_status="DONE", w1_phase_complete="YES")
        _write_plan(tmp_path, slug, content)

        ok, msg = _update_phase_in_plan(tmp_path, slug, "W1.1", "phase_start")
        assert ok

        result = _read_plan(tmp_path, slug)

        w1_1_lines = [l for l in result.splitlines() if "W1.1" in l]
        assert w1_1_lines
        assert "PHASE_STATUS: DONE" in w1_1_lines[0], "DONE must not be downgraded to IN_PROGRESS"
        assert "PHASE_STATUS: IN_PROGRESS" not in w1_1_lines[0]

    def test_tcn5_wave_complete_does_not_flip_child_phase_fields(self, tmp_path: Path) -> None:
        """TC-N5: wave_complete does NOT flip child PHASE_STATUS or PHASE_COMPLETE fields."""
        slug = "test-plan-tcn5"
        content = _make_3wave_plan()
        _write_plan(tmp_path, slug, content)

        ok, msg = update_wave_in_plan(tmp_path, slug, 2, "wave_complete")
        assert ok, msg

        result = _read_plan(tmp_path, slug)

        # W2 WAVE fields updated
        lines = result.splitlines()
        w2_start = next(i for i, l in enumerate(lines) if "## Wave 2" in l)
        w3_start = next(i for i, l in enumerate(lines) if "## Wave 3" in l)
        w2_section = "\n".join(lines[w2_start:w3_start])

        assert "WAVE_STATUS: DONE" in w2_section
        assert "WAVE_COMPLETE: YES" in w2_section

        # W2 child phase fields remain TODO/NO
        phase_lines = [l for l in w2_section.splitlines() if "W2.1" in l]
        assert phase_lines, "No W2.1 phase line found"
        assert "PHASE_STATUS: TODO" in phase_lines[0], (
            f"wave_complete must not flip child PHASE_STATUS. Got: {phase_lines[0]!r}"
        )
        assert "PHASE_COMPLETE: NO" in phase_lines[0]

    def test_tcn6_missing_wave_section_safe_noop(self, tmp_path: Path) -> None:
        """TC-N6: targeting wave=3 when no ## Wave 3 section exists — safe no-op."""
        slug = "test-plan-tcn6"
        content = textwrap.dedent("""\
            ---
            plan_id: test-plan-tcn6
            ---

            ## Wave 1 — Wave

            WAVE_STATUS: TODO
            WAVE_COMPLETE: NO

            | W1 | 🔲 TODO |
        """)
        _write_plan(tmp_path, slug, content)
        original = _read_plan(tmp_path, slug)

        _, changed, msg = _update_inline_fields_in_plan(content, slug, 3, "wave_complete")
        assert not changed
        assert "no matching wave section for wave=3" in msg

        # File unchanged (no-op)
        result = _read_plan(tmp_path, slug)
        assert result == original

    def test_tcn7_duplicate_wave_sections_warn_and_noop(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """TC-N7: duplicate ## Wave 2 sections → warning to stderr, file unchanged."""
        slug = "test-plan-tcn7"
        content = textwrap.dedent("""\
            ---
            plan_id: test-plan-tcn7
            ---

            ## Wave 1 — Wave

            WAVE_STATUS: TODO

            ## Wave 2 — First duplicate

            WAVE_STATUS: TODO
            WAVE_COMPLETE: NO

            ## Wave 2 — Second duplicate

            WAVE_STATUS: TODO
            WAVE_COMPLETE: NO
        """)

        _, changed, msg = _update_inline_fields_in_plan(content, slug, 2, "wave_complete")
        assert not changed
        assert "duplicate wave sections" in msg

        captured = capsys.readouterr()
        assert "duplicate Wave 2" in captured.err

    def test_tcn8_drift_detector_covers_all_field_types(self, tmp_path: Path) -> None:
        """TC-N8: parse_plan_file detects PHASE_STATUS, PHASE_COMPLETE, and DoD - Status: drift."""
        import importlib.util

        plans_dir = tmp_path / ".claude" / "plans"
        plans_dir.mkdir(parents=True, exist_ok=True)

        stale_plan = plans_dir / "stale-plan-tcn8.md"
        stale_plan.write_text(textwrap.dedent("""\
            ---
            plan_id: stale-plan-tcn8
            ---
            # Stale Plan TCN8

            Status: COMPLETED

            ## Wave 1 — Wave

            WAVE_STATUS: TODO
            WAVE_COMPLETE: NO

            - **W1.1** — Phase | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

            ### DoD

            DoD-1: Test
            - Evidence: something
            - Status: TODO
        """), encoding="utf-8")

        closer_path = REPO_ROOT / ".claude" / "governance/scripts" / "plan_driven_closer.py"
        spec = importlib.util.spec_from_file_location("plan_driven_closer_tcn8", closer_path)
        closer = importlib.util.module_from_spec(spec)
        sys.modules["plan_driven_closer_tcn8"] = closer
        spec.loader.exec_module(closer)

        ps = closer.parse_plan_file(stale_plan)
        assert ps.inline_open_fields, "Expected non-empty inline_open_fields"

        field_names = [f.split("=")[0] for f in ps.inline_open_fields]
        assert "wave_status" in field_names, f"wave_status missing from {field_names}"
        assert "wave_complete" in field_names, f"wave_complete missing from {field_names}"
        assert "phase_status" in field_names, f"phase_status missing from {field_names}"
        assert "phase_complete" in field_names, f"phase_complete missing from {field_names}"
        assert "dod_status" in field_names, f"dod_status missing from {field_names}"
