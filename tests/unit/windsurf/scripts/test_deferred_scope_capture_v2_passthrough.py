"""Test: post_agent_deferred_scope_capture forwards v2 optional signals
from DEFERRED_SCOPE marker keys to the scorer. ADR-031 passthrough contract.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

HOOK_PATH = REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf" / "post_agent_deferred_scope_capture.py"
spec = importlib.util.spec_from_file_location("dsc_hook", HOOK_PATH)
hook = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(hook)  # type: ignore[union-attr]


def _base_marker() -> dict[str, str]:
    return {
        "plan": "my-plan-abcdef",
        "wave": "W1",
        "phase": "W1.1",
        "layer": "L_TOOLS",
        "fan_in": "3",
        "surface": "Security",
        "coverage_gap_pct": "60.0",
        "est_tokens": "1000",
        "reason": "test passthrough",
    }


def test_v1_only_marker_scores_at_v1_band():
    """Marker with no v2 keys → scorer sees neutral defaults → v1-equivalent P3."""
    # Stub Notion token absent so no network; still scores and logs.
    rec = hook._process_marker(_base_marker(), has_receipt=True, token=None)
    assert rec["kind"] == "confirmed_by_receipt"
    assert rec["band"] == "P3"


def test_v2_heavy_signals_promote_band():
    """Marker with heavy v2 signals → scorer promotes to P1."""
    m = _base_marker()
    m["prod_invocations"] = "5000"
    m["trajectory_defect_rate"] = "0.05"
    m["reversibility"] = "action"
    m["item_class"] = "regression"
    rec = hook._process_marker(m, has_receipt=True, token=None)
    assert rec["kind"] == "confirmed_by_receipt"
    assert rec["band"] == "P1", (
        f"expected P1 with heavy signals, got {rec['band']} impact={rec['impact_score']}"
    )


def test_v2_adds_complexity_penalty():
    """adds_complexity=true applies 0.8x penalty."""
    m = _base_marker()
    m["prod_invocations"] = "100"
    without = hook._process_marker(dict(m), has_receipt=True, token=None)
    m["adds_complexity"] = "true"
    with_penalty = hook._process_marker(m, has_receipt=True, token=None)
    assert with_penalty["impact_score"] < without["impact_score"]
    # 0.8x is exact
    assert abs(with_penalty["impact_score"] - without["impact_score"] * 0.8) < 1.0


def test_v2_parse_marker_preserves_optional_keys():
    """Marker grammar parsing captures the 5 optional keys."""
    body = (
        "plan=p wave=W phase=P layer=L5 fan_in=2 surface=Write "
        "coverage_gap_pct=50.0 est_tokens=100 "
        "prod_invocations=1000 trajectory_defect_rate=0.1 "
        "reversibility=write item_class=regression adds_complexity=true "
        "reason=scope gap"
    )
    fields = hook._parse_marker(body)
    assert fields["prod_invocations"] == "1000"
    assert fields["trajectory_defect_rate"] == "0.1"
    assert fields["reversibility"] == "write"
    assert fields["item_class"] == "regression"
    assert fields["adds_complexity"] == "true"
    assert fields["reason"] == "scope gap"


def test_v2_unknown_reversibility_fails_open_as_neutral():
    """Unknown reversibility value → scorer uses neutral 1.0 (fail-open)."""
    m = _base_marker()
    m["reversibility"] = "bogus"
    rec = hook._process_marker(m, has_receipt=True, token=None)
    assert rec["kind"] == "confirmed_by_receipt"
    # Same band as baseline v1 — bogus reversibility didn't move the score
    baseline = hook._process_marker(_base_marker(), has_receipt=True, token=None)
    assert rec["band"] == baseline["band"]
