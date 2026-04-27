"""replay_comparison.json must exist and report ok=True for the deterministic three."""

from __future__ import annotations

import json
from pathlib import Path


def test_replay_comparison_present_and_ok(proof_dir: Path) -> None:
    p = proof_dir / "replay" / "replay_comparison.json"
    assert p.exists(), "replay_comparison.json missing"
    body = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(body, dict), "replay_comparison.json not a JSON object"
    assert body.get("ok") is True, (
        f"replay reported not-ok: reasons={body.get('reasons')}"
    )


def test_deterministic_digest_report_present(proof_dir: Path) -> None:
    p = proof_dir / "replay" / "deterministic_digest_report.json"
    assert p.exists(), "deterministic_digest_report.json missing"
    body = json.loads(p.read_text(encoding="utf-8"))
    assert "deterministic_three" in body, "missing deterministic_three section"
    # Every key in the deterministic three must report match=True
    for k, rec in body["deterministic_three"].items():
        assert rec.get("match") is True, f"{k} digest mismatch: {rec}"
