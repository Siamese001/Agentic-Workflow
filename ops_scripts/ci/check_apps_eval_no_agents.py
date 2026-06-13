"""CI gate: active apps_eval must not expose legacy role-like machinery."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPS_EVAL = ROOT / "apps_eval"

BANNED_NAME_FRAGMENTS = (
    "Agent",
    "AgentSpec",
    "Orchestrator",
    "Planner",
    "Hop",
    "PromotionLoop",
)
BANNED_PATH_PARTS = {
    "reasoning",
    "specs",
}
BANNED_FILES = {
    "agent_spec_config.py",
    "base_eval_engine.py",
    "hop_scorecard_engine.py",
    "hop_pipeline.py",
    "enterprise_eval_renderer.py",
    "promotion_loop.py",
}


def _active_python_files() -> list[Path]:
    return sorted(path for path in APPS_EVAL.rglob("*.py") if "__pycache__" not in path.parts)


def main() -> int:
    failures: list[str] = []
    if not APPS_EVAL.is_dir():
        failures.append("apps_eval directory is missing")
    if (APPS_EVAL / "reasoning").exists():
        failures.append("apps_eval/reasoning exists in active package")
    if (APPS_EVAL / "config" / "agent_spec_config.py").exists():
        failures.append("apps_eval/config/agent_spec_config.py exists in active package")
    if (APPS_EVAL / "config" / "specs").exists():
        failures.append("apps_eval/config/specs exists in active package")

    for path in APPS_EVAL.rglob("*"):
        rel = path.relative_to(ROOT).as_posix()
        if any(part in BANNED_PATH_PARTS for part in path.relative_to(APPS_EVAL).parts):
            failures.append(f"banned active path part: {rel}")
        if path.name in BANNED_FILES:
            failures.append(f"banned active file: {rel}")
        if any(fragment in path.stem for fragment in BANNED_NAME_FRAGMENTS):
            failures.append(f"banned active filename fragment: {rel}")

    for path in _active_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(fragment in node.name for fragment in BANNED_NAME_FRAGMENTS):
                    rel = path.relative_to(ROOT).as_posix()
                    failures.append(f"banned symbol {node.name} in {rel}:{node.lineno}")

    if failures:
        print("apps_eval legacy role gate failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS: active apps_eval exposes no legacy role-like files or symbols")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
