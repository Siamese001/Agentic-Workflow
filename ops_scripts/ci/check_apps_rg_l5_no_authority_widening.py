#!/usr/bin/env python3
"""Static guard for apps_rg L5 certification authority boundaries.

The guard covers the L5 certification surface wired by apps_rg. It blocks:
- certification code importing runtime gate verdict or Exit/X3 disposition types
- certification code performing file/network/provider side effects
- app-specific literals in agentic_core L5 certification/contracts code
- apps_rg placing L5 packet refs inside gate_verdict_refs
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_L5_CERT_ROOTS = (
    REPO_ROOT / "agentic_core" / "L5_safety" / "certification",
    REPO_ROOT / "agentic_core" / "L5_safety" / "contracts" / "l5_certification_contracts.py",
)
APPS_RG_RUNTIME_ROOTS = (
    REPO_ROOT / "apps_rg" / "runtime",
    REPO_ROOT / "apps_rg" / "cache",
)

FORBIDDEN_IMPORT_TOKENS = (
    "runtime_gates",
    "GateVerdict",
    "ExitDisposition",
    "X3",
    "x3",
    "exit_disposition_types",
    "exit_outcome_types",
)
PROVIDER_OR_NETWORK_IMPORTS = (
    "anthropic",
    "boto3",
    "cohere",
    "google.generativeai",
    "httpx",
    "openai",
    "requests",
    "socket",
    "urllib",
)
APP_LITERAL_TOKENS = (
    "apps_rg",
    "apps_lic",
    "apps_research",
    "resume_generation",
    "role_target",
)
FILE_WRITE_CALLS = {
    "open",
    "os.open",
    "Path.open",
    "write",
    "write_text",
    "write_bytes",
}
NETWORK_CALLS = {
    "urlopen",
    "connect",
    "send",
    "recv",
}
L5_PACKET_TOKENS = (
    "l5_certification_packet",
    "l5_packet",
    "L5CertificationPacket",
)


def _iter_python_files(paths: tuple[Path, ...] | list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            files.append(path)
        elif path.is_dir():
            files.extend(p for p in path.rglob("*.py") if p.is_file())
    return sorted(set(files))


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else str(path)


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _scan_core_file(path: Path) -> list[str]:
    rel = _rel(path)
    errors: list[str] = []
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=rel)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if any(token in name for token in FORBIDDEN_IMPORT_TOKENS):
                    errors.append(f"{rel}:{node.lineno} forbidden L5 runtime/X3 import {name!r}")
                if name in PROVIDER_OR_NETWORK_IMPORTS or name.split(".", 1)[0] in PROVIDER_OR_NETWORK_IMPORTS:
                    errors.append(f"{rel}:{node.lineno} forbidden provider/network import {name!r}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported = " ".join(alias.name for alias in node.names)
            haystack = f"{module} {imported}"
            if any(token in haystack for token in FORBIDDEN_IMPORT_TOKENS):
                errors.append(f"{rel}:{node.lineno} forbidden L5 runtime/X3 import {haystack!r}")
            if module in PROVIDER_OR_NETWORK_IMPORTS or module.split(".", 1)[0] in PROVIDER_OR_NETWORK_IMPORTS:
                errors.append(f"{rel}:{node.lineno} forbidden provider/network import {module!r}")
        elif isinstance(node, ast.Call):
            call = _call_name(node.func)
            tail = call.rsplit(".", 1)[-1]
            if call in FILE_WRITE_CALLS or tail in FILE_WRITE_CALLS:
                errors.append(f"{rel}:{node.lineno} forbidden file write/open call {call!r}")
            if (
                call in NETWORK_CALLS
                or tail in NETWORK_CALLS
                or any(call.startswith(f"{module}.") for module in PROVIDER_OR_NETWORK_IMPORTS)
            ):
                errors.append(f"{rel}:{node.lineno} forbidden network call {call!r}")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            if any(token in value for token in APP_LITERAL_TOKENS):
                errors.append(f"{rel}:{getattr(node, 'lineno', 0)} app-specific literal in agentic_core L5 certification")

    return errors


def _scan_apps_rg_file(path: Path) -> list[str]:
    rel = _rel(path)
    errors: list[str] = []
    source = path.read_text(encoding="utf-8")
    for lineno, line in enumerate(source.splitlines(), start=1):
        if "gate_verdict_refs" in line and any(token in line for token in L5_PACKET_TOKENS):
            errors.append(f"{rel}:{lineno} L5 packet ref placed in gate_verdict_refs")

    try:
        tree = ast.parse(source, filename=rel)
    except SyntaxError as exc:
        return [f"{rel}: syntax error: {exc}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for keyword in node.keywords:
                if keyword.arg != "gate_verdict_refs":
                    continue
                rendered = ast.unparse(keyword.value) if hasattr(ast, "unparse") else ""
                if any(token in rendered for token in L5_PACKET_TOKENS):
                    errors.append(f"{rel}:{node.lineno} L5 packet ref placed in gate_verdict_refs")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extra-path", action="append", default=[])
    args = parser.parse_args(argv)

    core_files = _iter_python_files(CORE_L5_CERT_ROOTS)
    app_files = _iter_python_files(APPS_RG_RUNTIME_ROOTS + tuple((REPO_ROOT / p).resolve() for p in args.extra_path))
    errors: list[str] = []

    for path in core_files:
        errors.extend(_scan_core_file(path))
    for path in app_files:
        errors.extend(_scan_apps_rg_file(path))

    print(
        f"[APPS-RG-L5-AUTH] scanned {len(core_files)} core certification file(s), "
        f"{len(app_files)} apps_rg file(s), {len(errors)} issue(s)"
    )
    if errors:
        for error in errors:
            print(f"  ERROR  {error}")
        return 1
    print("[APPS-RG-L5-AUTH] L5 certification authority boundary gate GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
