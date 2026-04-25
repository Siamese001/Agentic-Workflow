"""CI gate: prompt reception v2 wiring \u2014 W5 RH5.3.

Verifies that ``SovereignLLMGateway`` routes provider calls through the W2
adapter layer when ``PROMPT_ADAPTER_V2=1`` is set, rather than passing the
flat ``final_system_string`` / ``final_user_string`` directly.

Strategy: static AST scan of
``agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`` to ensure
the file imports the adapter registry and feature flag and calls
``_resolve_provider_payload`` from the two ``generate*`` methods.

A true golden-replay test (end-to-end behavior check against frozen
Anthropic/OpenAI fixtures) is deferred to W5b follow-up.

Exit codes:
    0 \u2014 wiring intact
    1 \u2014 any missing import or call site
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GATEWAY_FILE = _REPO_ROOT / "agentic_core" / "L2_execution" / "enforcement" / "SovereignLLMGateway.py"

_REQUIRED_IMPORTS: tuple[tuple[str, str], ...] = (
    (
        "agentic_core.L2_execution.enforcement._adapter_registry",
        "get_adapter",
    ),
    (
        "agentic_core.L2_execution.enforcement.provider_adapter",
        "adapter_v2_enabled",
    ),
    (
        "agentic_core.L2_execution.enforcement._reception_audit",
        "emit",
    ),
)

_REQUIRED_METHODS: tuple[str, ...] = ("_resolve_provider_payload",)
_REQUIRED_CALLERS: tuple[str, ...] = ("generate", "generate_with_reasoning")


def _find_imported_names(tree: ast.AST) -> set[tuple[str, str]]:
    """Collect ``(module, imported_name)`` pairs from ``from X import Y as Z``."""
    found: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                found.add((node.module, alias.name))
    return found


def _find_method_defs(tree: ast.AST) -> dict[str, ast.FunctionDef]:
    """Collect methods defined inside ``class SovereignLLMGateway``.

    Restricting to this class avoids collisions with other classes that
    happen to define a ``generate`` method (e.g. ``_PlaceholderProvider``).
    """
    methods: dict[str, ast.FunctionDef] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SovereignLLMGateway":
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    methods[child.name] = child
            break
    return methods


def _method_calls(method_node: ast.FunctionDef) -> set[str]:
    calls: set[str] = set()
    for node in ast.walk(method_node):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                calls.add(func.attr)
            elif isinstance(func, ast.Name):
                calls.add(func.id)
    return calls


def validate_gateway_wiring(gateway_path: Path) -> tuple[bool, list[str]]:
    """Return ``(ok, errors)``."""
    errors: list[str] = []
    if not gateway_path.exists():
        return False, [f"gateway file not found: {gateway_path}"]

    try:
        source = gateway_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(gateway_path))
    except (OSError, SyntaxError) as exc:
        return False, [f"parse failed: {exc}"]

    # Imports
    imports = _find_imported_names(tree)
    for module, name in _REQUIRED_IMPORTS:
        if (module, name) not in imports:
            errors.append(f"missing import: from {module} import {name}")

    # Method definitions + call-site wiring
    methods = _find_method_defs(tree)
    for required in _REQUIRED_METHODS:
        if required not in methods:
            errors.append(f"missing method definition: {required}")

    for caller in _REQUIRED_CALLERS:
        node = methods.get(caller)
        if node is None:
            errors.append(f"missing method: {caller}")
            continue
        calls = _method_calls(node)
        if "_resolve_provider_payload" not in calls:
            errors.append(
                f"{caller}() does not call _resolve_provider_payload \u2014 adapter dispatch missing"
            )
        if "emit" not in calls and "_emit_reception_evidence" not in calls:
            errors.append(f"{caller}() does not call the reception-audit emit()")

    return (len(errors) == 0, errors)


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate gateway adapter-v2 wiring.")
    parser.add_argument("--gateway", type=Path, default=_GATEWAY_FILE)
    args = parser.parse_args(argv)

    ok, errors = validate_gateway_wiring(args.gateway)
    if not ok:
        print(f"FAIL: {args.gateway}", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"OK: {args.gateway}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())


__all__ = ["validate_gateway_wiring"]
