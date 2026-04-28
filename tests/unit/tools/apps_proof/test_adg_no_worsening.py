"""adg_delta.json must report no P0 worsening on touched files."""

from __future__ import annotations

import json
from pathlib import Path


def test_adg_delta_no_p0_worsening(proof_dir: Path) -> None:
    p = proof_dir / "adg" / "adg_delta.json"
    if not p.exists():
        # Run was invoked without --require-adg — check is N/A.
        return
    body = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(body, dict), "adg_delta.json not a JSON object"
    assert body.get("p0_increased", False) is False, (
        f"ADG P0 worsened by {body.get('delta_p0')} on touched files"
    )
    assert int(body.get("delta_p0", 0)) <= 0, (
        f"ADG delta_p0={body.get('delta_p0')} > 0 (regression)"
    )
