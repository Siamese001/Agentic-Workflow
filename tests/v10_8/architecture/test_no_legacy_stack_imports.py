"""Architecture regression tests to enforce v10.8 stack usage."""

from __future__ import annotations

from pathlib import Path


def test_no_v10_7_stack_imports_outside_legacy_dirs():
    repo_root = Path(__file__).resolve().parents[1]
    offenders: list[Path] = []

    for path in repo_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "agent_stacks_v10_7" in text or "stacks_v10_7" in text:
            offenders.append(path.relative_to(repo_root))

    assert offenders == [], f"Found legacy stack imports in: {offenders}"
