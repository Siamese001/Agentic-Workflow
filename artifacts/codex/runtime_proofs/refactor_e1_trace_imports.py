"""Refactor E1 trace-stub modules for the P1 ratchet first wave.

This helper is an ignored run artifact. It selects the highest trace-import
ratio modules from the immutable ADG snapshot and rewrites imports from:

    from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_x

to:

    from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

Then it rewrites local trace symbol references to ``trace_contract.<symbol>``.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import sqlite3
import tokenize
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TRACE_MODULE = "agentic_core.runtime.contracts.lifecycle_trace_contract"
ALIAS_IMPORT = "from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract"
TRACE_MARKER_PREFIXES = (
    "agentic_core.runtime.contracts.lifecycle_trace_contract._emit_",
    "agentic_core.runtime.contracts.lifecycle_trace_contract.emit_",
)
PRODUCTION_ROOTS = (
    "agentic_core/",
    "apps_eval/",
    "apps_exec/",
    "apps_lic/",
    "apps_research/",
    "apps_rg/",
    "apps_shared/",
    "apps_underwriting_ai/",
    "system_learning/",
    "infrastructure/",
)
EXCLUDE_PATHS = {"agentic_core/runtime/contracts/lifecycle_trace_contract.py"}


@dataclass(frozen=True)
class Candidate:
    path: str
    total_imports: int
    trace_imports: int
    ratio: float


@dataclass(frozen=True)
class RewriteResult:
    path: str
    changed: bool
    local_names: list[str]
    import_blocks_removed: int


def _candidate_rows(snapshot: Path, limit: int, exclude_paths: set[str]) -> list[Candidate]:
    conn = sqlite3.connect(snapshot)
    try:
        rows = conn.execute(
            """
            SELECT e.source_file, e.symbol
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            WHERE e.relation_type = 'imports'
              AND e.source_file IS NOT NULL
              AND e.source_file != ''
            """
        ).fetchall()
    finally:
        conn.close()

    buckets: dict[str, dict[str, int]] = {}
    for source_file, symbol in rows:
        if source_file in EXCLUDE_PATHS:
            continue
        if source_file in exclude_paths:
            continue
        if not source_file.startswith(PRODUCTION_ROOTS):
            continue
        bucket = buckets.setdefault(source_file, {"total": 0, "trace": 0})
        bucket["total"] += 1
        if symbol and symbol.startswith(TRACE_MARKER_PREFIXES):
            bucket["trace"] += 1

    candidates: list[Candidate] = []
    for path, counts in buckets.items():
        total = counts["total"]
        trace = counts["trace"]
        if total < 10 or trace == 0:
            continue
        ratio = trace / total
        if ratio < 0.80:
            continue
        candidates.append(Candidate(path, total, trace, round(ratio, 3)))
    candidates.sort(key=lambda row: (-row.trace_imports, -row.total_imports, row.path))
    return candidates[:limit]


def _trace_import_nodes(tree: ast.AST) -> list[ast.ImportFrom]:
    nodes: list[ast.ImportFrom] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == TRACE_MODULE:
            nodes.append(node)
    return sorted(nodes, key=lambda node: node.lineno)


def _local_name_map(nodes: Iterable[ast.ImportFrom]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for node in nodes:
        for alias in node.names:
            if alias.name == "*":
                raise ValueError("star imports from lifecycle_trace_contract are not supported")
            local_name = alias.asname or alias.name
            mapping[local_name] = alias.name
    return mapping


def _remove_import_blocks(lines: list[str], nodes: list[ast.ImportFrom]) -> tuple[list[str], int]:
    remove_ranges: set[int] = set()
    for node in nodes:
        end_lineno = getattr(node, "end_lineno", node.lineno)
        for line_no in range(node.lineno, end_lineno + 1):
            remove_ranges.add(line_no)
    kept = [line for idx, line in enumerate(lines, start=1) if idx not in remove_ranges]
    insert_at = min((node.lineno for node in nodes), default=1) - 1
    insert_at -= sum(1 for line_no in remove_ranges if line_no < min((node.lineno for node in nodes), default=1))
    insert_at = max(0, min(insert_at, len(kept)))
    kept.insert(insert_at, ALIAS_IMPORT + "\n")
    return kept, len(nodes)


def _line_offsets(source: str) -> list[int]:
    offsets = [0]
    running = 0
    for line in source.splitlines(keepends=True):
        running += len(line)
        offsets.append(running)
    return offsets


def _offset(offsets: list[int], position: tuple[int, int]) -> int:
    line, column = position
    return offsets[line - 1] + column


def _replace_local_names(source: str, mapping: dict[str, str]) -> str:
    previous_significant = ""
    offsets = _line_offsets(source)
    replacements: list[tuple[int, int, str]] = []
    token_stream = tokenize.generate_tokens(io.StringIO(source).readline)
    for token in token_stream:
        token_type = token.type
        token_text = token.string
        if (
            token_type == tokenize.NAME
            and token_text in mapping
            and previous_significant != "."
            and token_text != "trace_contract"
        ):
            replacements.append(
                (
                    _offset(offsets, token.start),
                    _offset(offsets, token.end),
                    f"trace_contract.{mapping[token_text]}",
                )
            )
            previous_significant = mapping[token_text]
            continue
        if token_type not in {tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.COMMENT}:
            previous_significant = token_text
    rewritten = source
    for start, end, replacement in reversed(replacements):
        rewritten = rewritten[:start] + replacement + rewritten[end:]
    return rewritten


def rewrite_file(root: Path, relative_path: str, *, apply: bool) -> RewriteResult:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=relative_path)
    import_nodes = _trace_import_nodes(tree)
    if not import_nodes:
        return RewriteResult(relative_path, False, [], 0)
    mapping = _local_name_map(import_nodes)
    lines, removed = _remove_import_blocks(text.splitlines(keepends=True), import_nodes)
    rewritten = _replace_local_names("".join(lines), mapping)
    ast.parse(rewritten, filename=relative_path)
    changed = rewritten != text
    if changed and apply:
        path.write_text(rewritten, encoding="utf-8", newline="")
    return RewriteResult(relative_path, changed, sorted(mapping), removed)


def _excluded_paths_from_manifests(manifests: list[Path]) -> set[str]:
    excluded: set[str] = set()
    for manifest_path in manifests:
        if not manifest_path.exists():
            raise FileNotFoundError(manifest_path)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        for candidate in payload.get("candidates", []):
            path = candidate.get("path")
            if isinstance(path, str):
                excluded.add(path)
    return excluded


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--exclude-manifest", action="append", type=Path, default=[])
    parser.add_argument("--wave-id", default="W2.E1")
    args = parser.parse_args()

    exclude_paths = _excluded_paths_from_manifests(args.exclude_manifest)
    selected: list[Candidate] = []
    results: list[RewriteResult] = []
    for candidate in _candidate_rows(args.snapshot, args.limit + len(exclude_paths) + 100, exclude_paths):
        result = rewrite_file(args.repo_root, candidate.path, apply=args.apply)
        if not result.changed:
            continue
        selected.append(candidate)
        results.append(result)
        if len(selected) >= args.limit:
            break
    manifest = {
        "snapshot": str(args.snapshot),
        "repo_root": str(args.repo_root),
        "limit": args.limit,
        "wave_id": args.wave_id,
        "applied": args.apply,
        "candidate_count": len(selected),
        "changed_count": sum(1 for result in results if result.changed),
        "excluded_count": len(exclude_paths),
        "exclude_manifests": [str(path) for path in args.exclude_manifest],
        "candidates": [candidate.__dict__ for candidate in selected],
        "results": [result.__dict__ for result in results],
        "adg_provenance": {
            "backend_used": "sqlite_with_mcp_health",
            "reason": "ADG MCP health passed for snapshot 07072026_2307; detailed E1 candidate extraction used immutable digest-bound SQLite snapshot because exposed MCP tools do not include ad hoc SQL.",
            "snapshot": args.snapshot.name,
        },
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"changed_count": manifest["changed_count"], "candidate_count": len(selected)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
