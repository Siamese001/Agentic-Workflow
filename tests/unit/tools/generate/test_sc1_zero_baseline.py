"""Regression guard: SC-1 gravity must stay at zero.

P2 W2 (2026-04-23) drove SC-1 from 63 to 0 by:
  1. Fixing guardian_filter window to cover multi-line imports
  2. Adding legit guardian exemptions on 3 L2 healer files

This test locks the baseline at 0 and flips to red any regression on
either of those fixes. Companion to the enforce-mode flip planned in W5.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[4]
ADG_DIR = REPO / "artifacts" / "adg"


def _latest_snapshot() -> Path | None:
    snaps = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))
    return snaps[-1] if snaps else None


@pytest.mark.skipif(_latest_snapshot() is None, reason="No ADG snapshot present")
def test_sc1_gravity_is_zero() -> None:
    """SC-1 gravity violations must remain at 0 after P2 W2."""
    from tools.generate.validation.gates import _query_sc1_gravity

    snap = _latest_snapshot()
    assert snap is not None
    conn = sqlite3.connect(str(snap))
    try:
        violations = _query_sc1_gravity(conn)
    finally:
        conn.close()

    if violations:
        preview = "\n".join(
            f"  {v.get('source_file')}:{v.get('line_no')} — {v.get('evidence')}" for v in violations[:10]
        )
        pytest.fail(
            f"SC-1 regression: {len(violations)} gravity violation(s) detected "
            f"(baseline is 0 after P2 W2).\n{preview}"
        )


def test_guardian_filter_covers_multiline_imports(tmp_path: Path) -> None:
    """Regression: guardian comment on closing `)` of multi-line import
    must be recognized as an exemption."""
    from tools.adg.core.guardian_filter import clear_cache, is_layer_violation_exempted

    sample = tmp_path / "sample.py"
    sample.write_text(
        "\n".join(
            [
                "def loader():",  # line 1
                "    from some.module import (",  # line 2 (import start — edge line_no)
                "        thing_a,",  # line 3
                "        thing_b,",  # line 4
                "    )  # guardian: allow-layer-violation -- test marker",  # line 5
                "    return thing_a",
            ]
        ),
        encoding="utf-8",
    )
    clear_cache()
    # Edge line_no points at the import start (line 2); marker is on line 5.
    assert is_layer_violation_exempted(sample, 2, repo_root=tmp_path) is True
    clear_cache()
    # Single-line import exemption still works (marker on same line).
    single = tmp_path / "single.py"
    single.write_text(
        "from a.b import X  # guardian: allow-layer-violation -- same line",
        encoding="utf-8",
    )
    assert is_layer_violation_exempted(single, 1, repo_root=tmp_path) is True
    clear_cache()
    # A line with no marker within the window is NOT exempted.
    clean = tmp_path / "clean.py"
    clean.write_text("from a.b import X\n", encoding="utf-8")
    assert is_layer_violation_exempted(clean, 1, repo_root=tmp_path) is False
