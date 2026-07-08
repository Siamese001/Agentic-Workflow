"""Lightweight source replay for the E1 trace import wave."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


TRACE_MODULE = "agentic_core.runtime.contracts.lifecycle_trace_contract"
ALIAS_MODULE = "agentic_core.runtime.contracts"
ALIAS_NAME = "lifecycle_trace_contract"
ALIAS_ASNAME = "trace_contract"


def _has_alias_import(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module != ALIAS_MODULE:
            continue
        for alias in node.names:
            if alias.name == ALIAS_NAME and alias.asname == ALIAS_ASNAME:
                return True
    return False


def _trace_symbol_imports(tree: ast.AST) -> list[str]:
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == TRACE_MODULE:
            imported.extend(alias.name for alias in node.names)
    return imported


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: e1_trace_import_wave1_source_replay.py <repo-root> <manifest> <output>")
        return 2
    repo_root = Path(sys.argv[1])
    manifest_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    results = []
    for candidate in manifest["candidates"]:
        path = candidate["path"]
        full_path = repo_root / path
        tree = ast.parse(full_path.read_text(encoding="utf-8"), filename=path)
        trace_imports = _trace_symbol_imports(tree)
        has_alias = _has_alias_import(tree)
        status = "PASS" if has_alias and not trace_imports else "FAIL"
        results.append(
            {
                "path": path,
                "status": status,
                "has_trace_contract_alias": has_alias,
                "remaining_trace_symbol_imports": trace_imports,
            }
        )
    failures = [result for result in results if result["status"] != "PASS"]
    payload = {
        "manifest": str(manifest_path),
        "candidate_count": len(results),
        "passed": len(results) - len(failures),
        "failed": len(failures),
        "results": results,
        "proof": "selected modules no longer import lifecycle trace symbols directly and use trace_contract alias instead",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("candidate_count", "passed", "failed")}, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
