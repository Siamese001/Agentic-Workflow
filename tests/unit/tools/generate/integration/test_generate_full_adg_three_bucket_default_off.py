"""W1.6: default ADG hot path must not mandate three-bucket audit stages."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tools.generate.integration import optional_three_bucket as mod

REPO_ROOT = Path(__file__).resolve().parents[5]
GENERATE_FULL_ADG = REPO_ROOT / "tools" / "generate" / "generate_full_adg.py"


def test_generate_full_adg_has_no_inline_three_bucket_producers() -> None:
    text = GENERATE_FULL_ADG.read_text(encoding="utf-8")
    forbidden = (
        "build_runtime_view",
        "registry_lift(",
        "emit_three_bucket_reports",
        "sign_snapshot(",
    )
    for name in forbidden:
        assert name not in text, f"{name} must not appear on hot path; use optional_three_bucket"


def test_generate_full_adg_routes_through_optional_orchestrator() -> None:
    text = GENERATE_FULL_ADG.read_text(encoding="utf-8")
    assert "_run_optional_three_bucket" in text
    assert "optional_three_bucket" in text
    assert re.search(r"--three-bucket", text)


def test_default_env_skips_optional_enrichment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "ADG_THREE_BUCKET",
        "ADG_RUNTIME_VIEW",
        "ADG_REGISTRY_LIFT",
        "ADG_THREE_BUCKET_REPORTS",
        "ADG_THREE_BUCKET_SIGN",
    ):
        monkeypatch.delenv(name, raising=False)

    snap = tmp_path / "adg_indexed_test.sqlite"
    snap.write_bytes(b"SQLite format 3\x00")
    result = mod.run_optional_three_bucket_enrichment(snap)
    assert result.skipped_reason
    assert result.report_paths == {}
