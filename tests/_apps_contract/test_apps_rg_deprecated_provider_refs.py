"""Guard that retired local-provider names do not re-enter apps_rg source."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_RG_ROOT = REPO_ROOT / "apps_rg"


def test_apps_rg_source_has_no_retired_local_provider_refs() -> None:
    forbidden = (
        "qw" + "en",
        "Qw" + "en",
        "QW" + "EN",
        "vl" + "lm",
        "vL" + "LM",
    )
    offenders: list[str] = []
    for path in APPS_RG_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(token in text for token in forbidden):
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == []
