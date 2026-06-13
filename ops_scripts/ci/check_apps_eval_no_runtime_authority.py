"""CI gate: apps_eval must stay a harness, not a runtime authority layer."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPS_EVAL = ROOT / "apps_eval"

ALLOWED_IMPORTS = {
    "agentic_core.runtime.entry.apps_rg_dispatch": {"dispatch_apps_rg_run"},
    "apps_lic.runtime.dispatch.canonical_dispatch": {
        "build_cli_ingress_raw",
        "run_canonical_apps_lic_spine",
    },
}
FORBIDDEN_TEXT = (
    "MetaLearningBus",
    "governed_run",
    "maybe_invoke_exit_eval",
    "promotion_loop",
    "publish_eval_outcome",
    "apps_shared.spine_emission",
    "route_registry",
    "l4_write",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "agentic_core.L0_",
    "agentic_core.L1_",
    "agentic_core.L2_",
    "agentic_core.L3_",
    "agentic_core.L4_",
    "agentic_core.L5_",
    "agentic_core.L6_",
    "agentic_core.runtime.exit",
    "agentic_core.runtime.gates",
    "apps_rg.",
    "apps_lic.",
    "apps_shared.",
)


def _import_names(node: ast.ImportFrom) -> set[str]:
    return {alias.name for alias in node.names}


def main() -> int:
    failures: list[str] = []
    for path in sorted(APPS_EVAL.rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        for term in FORBIDDEN_TEXT:
            if term in text:
                failures.append(f"forbidden runtime/learning term {term} in {rel}")
        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    if any(name.startswith(prefix) for prefix in FORBIDDEN_IMPORT_PREFIXES):
                        failures.append(f"forbidden import {name} in {rel}:{node.lineno}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module in ALLOWED_IMPORTS:
                    extra = _import_names(node) - ALLOWED_IMPORTS[module]
                    if extra:
                        failures.append(f"noncanonical import {sorted(extra)} from {module} in {rel}:{node.lineno}")
                    continue
                if any(module.startswith(prefix) for prefix in FORBIDDEN_IMPORT_PREFIXES):
                    failures.append(f"forbidden import from {module} in {rel}:{node.lineno}")
                if module.startswith("agentic_core.") and module not in ALLOWED_IMPORTS:
                    failures.append(f"noncanonical agentic_core import from {module} in {rel}:{node.lineno}")

    if failures:
        print("apps_eval runtime authority gate failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS: apps_eval imports only canonical product entrypoints and no runtime authority wiring")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
