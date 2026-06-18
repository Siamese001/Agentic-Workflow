from __future__ import annotations

import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_codex_hooks_feature_flag_enabled() -> None:
    config = tomllib.loads((REPO_ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
    features = config.get("features", {})

    assert features.get("codex_hooks") is True
    assert "hooks" not in features
