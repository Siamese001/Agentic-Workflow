from __future__ import annotations

import ast
from pathlib import Path


def test_active_package_has_no_legacy_role_symbols() -> None:
    banned = ["A" + "gent", "Orch" + "estrator", "Plan" + "ner", "H" + "op", "Promotion" + "Loop"]
    root = Path("apps_eval")
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(term in node.name for term in banned):
                    offenders.append(f"{path.as_posix()}::{node.name}")
    assert offenders == []
