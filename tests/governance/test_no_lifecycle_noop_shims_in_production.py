"""Test 6 — bootstrap_runtime.py must not silence emit_replay_key.

Fails today: ``apps_rg/bootstrap_runtime.py`` overrides
``lifecycle.emit_replay_key = _noop`` (and the wider lifecycle ``__getattr__``
fallback that returns ``_noop`` for missing attributes), which means replay
keys are never persisted from apps_rg in production.

Remediation: plan ``apps-rg-governed-runtime-b8d4f1.md`` Wave 7 P7.2.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.governance
@pytest.mark.xfail(
    reason="Governance gap: bootstrap_runtime.py shims emit_replay_key to _noop. "
    "Remediation: plan apps-rg-governed-runtime-b8d4f1.md Wave 7 P7.2.",
    strict=True,
)
def test_bootstrap_runtime_does_not_noop_replay_key() -> None:
    boot = REPO_ROOT / "apps_rg" / "bootstrap_runtime.py"
    assert boot.exists(), f"missing {boot}"
    src = boot.read_text(encoding="utf-8")

    # Forbidden: explicit override of replay-key emitter.
    assert not re.search(r"emit_replay_key\s*=\s*_noop", src), (
        "bootstrap_runtime.py must not assign emit_replay_key = _noop in production. "
        "Replay receipts depend on real key emission."
    )

    # Forbidden: blanket lifecycle.__getattr__ fallback that returns _noop.
    # If a fallback exists, it must be guarded (env-gated for tests, or removed entirely).
    if re.search(r"lifecycle\.__getattr__\s*=", src):
        assert "TEST" in src.upper() or "DEBUG" in src.upper() or "STRICT" in src.upper(), (
            "bootstrap_runtime.py installs lifecycle.__getattr__ fallback without an "
            "env/strict guard — this silences any missing emitter in production."
        )
