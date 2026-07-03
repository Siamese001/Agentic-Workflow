from __future__ import annotations

from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[3]
AUTOMATION_TOML = (
    REPO_ROOT
    / ".codex"
    / "automations"
    / "adg-p0-blocker-burndown"
    / "automation.toml"
)


def test_p0_burndown_consumes_digest_bound_handoff_pointer() -> None:
    payload = tomllib.loads(AUTOMATION_TOML.read_text(encoding="utf-8"))
    handoff = payload["handoff"]
    prompt = payload["prompt"]

    pointer_path = "artifacts/adg/handoffs/adg_repair_handoff_latest.json"
    validator = (
        "python tools/adg/consume_adg_repair_handoff.py "
        "--handoff-pointer artifacts/adg/handoffs/adg_repair_handoff_latest.json --json"
    )

    assert handoff["handoff_pointer_path"] == pointer_path
    assert handoff["validator"] == validator
    assert handoff["requires_digest_bound_handoff_pointer"] is True
    assert validator in prompt
    assert "verify the receipt SHA, run ID, and artifact digests" in prompt
    assert "compute current P0 FIX, P0 WAVE, P0 TRACKED BACKLOG" in prompt
