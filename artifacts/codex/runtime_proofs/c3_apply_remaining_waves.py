#!/usr/bin/env python3
"""Apply C3 silent-write receipt instrumentation for bounded P1 waves."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


QUERY = """
SELECT DISTINCT
    src.resolved_path AS writer_path,
    src.layer AS writer_layer,
    src.id AS writer_id,
    we.symbol AS write_symbol
FROM edges we
JOIN nodes src ON src.id = we.src_id
WHERE we.relation_type = 'writes_to'
  AND src.resolved_path IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM edges se
      WHERE se.src_id = we.src_id
        AND se.relation_type = 'emits_side_effect'
  )
  AND NOT EXISTS (
      SELECT 1 FROM edges se
      WHERE se.dst_id = we.src_id
        AND se.relation_type = 'emits_side_effect'
  )
ORDER BY src.resolved_path
"""

WRITE_SYMBOL_TAILS = (
    ".write_text",
    ".write_bytes",
    ".write",
    ".writelines",
    ".open",
    ".mkdir",
    ".touch",
    ".rename",
    ".unlink",
)

WRITE_SYMBOL_NAMES = {
    "open",
    "print",
    "json.dump",
    "shutil.move",
    "shutil.copy",
    "shutil.copy2",
    "shutil.copytree",
    "subprocess.run",
}


@dataclass(frozen=True)
class C3Row:
    path: str
    layer: str
    node_id: int
    symbols: tuple[str, ...]


def _call_symbol(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts: list[str] = [func.attr]
        value = func.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        return ".".join(reversed(parts))
    return ""


def _is_write_call(node: ast.Call, allowed_symbols: set[str]) -> bool:
    symbol = _call_symbol(node)
    if symbol in allowed_symbols:
        return True
    if symbol in WRITE_SYMBOL_NAMES:
        return True
    if any(symbol.endswith(tail) for tail in WRITE_SYMBOL_TAILS):
        return True
    if symbol.endswith(".open"):
        return True
    return False


def _own_calls(node: ast.AST) -> list[ast.Call]:
    """Return calls owned by this statement, excluding nested statement bodies."""
    calls: list[ast.Call] = []
    stack = list(ast.iter_child_nodes(node))
    while stack:
        child = stack.pop()
        if isinstance(child, ast.stmt):
            continue
        if isinstance(child, ast.Call):
            calls.append(child)
        stack.extend(ast.iter_child_nodes(child))
    return calls


def _statement_has_write(stmt: ast.stmt, allowed_symbols: set[str]) -> bool:
    return any(_is_write_call(call, allowed_symbols) for call in _own_calls(stmt))


def _iter_statements(node: ast.AST) -> list[ast.stmt]:
    found: list[ast.stmt] = []
    for field in ("body", "orelse", "finalbody"):
        body = getattr(node, field, None)
        if isinstance(body, list):
            for item in body:
                if isinstance(item, ast.stmt):
                    found.append(item)
                    found.extend(_iter_statements(item))
    handlers = getattr(node, "handlers", None)
    if isinstance(handlers, list):
        for handler in handlers:
            found.extend(_iter_statements(handler))
    return found


def _line_ending_for(lines: list[str], index: int | None = None) -> str:
    if index is not None and 0 <= index < len(lines) and lines[index].endswith("\r\n"):
        return "\r\n"
    crlf = sum(1 for line in lines if line.endswith("\r\n"))
    lf = sum(1 for line in lines if line.endswith("\n") and not line.endswith("\r\n"))
    return "\r\n" if crlf > lf else "\n"


def _insert_import_logging(lines: list[str], tree: ast.Module) -> list[str]:
    if any(isinstance(node, ast.Import) and any(alias.name == "logging" for alias in node.names) for node in tree.body):
        return lines

    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1
    if len(lines) > insert_at and re.match(r"#.*coding[:=]", lines[insert_at]):
        insert_at += 1

    body = list(tree.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        insert_at = max(insert_at, body[0].end_lineno or body[0].lineno)

    for node in body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            insert_at = max(insert_at, node.end_lineno or node.lineno)

    lines.insert(insert_at, f"import logging{_line_ending_for(lines, insert_at)}")
    return lines


def _instrument_file(root: Path, row: C3Row) -> dict[str, object]:
    rel_path = row.path
    path = root / rel_path
    text = path.read_text(encoding="utf-8")
    if "C3 write receipt:" in text:
        return {"file": rel_path, "status": "already_instrumented"}

    tree = ast.parse(text, filename=str(path))
    lines = text.splitlines(keepends=True)
    lines = _insert_import_logging(lines, tree)

    text = "".join(lines)
    tree = ast.parse(text, filename=str(path))
    statements = _iter_statements(tree)
    allowed_symbols = {symbol for symbol in row.symbols if symbol}
    selected = next((stmt for stmt in statements if _statement_has_write(stmt, allowed_symbols)), None)
    if selected is None:
        raise RuntimeError(
            f"no recognized write statement found in {rel_path}; "
            f"allowed_symbols={sorted(allowed_symbols)}"
        )

    end_line = selected.end_lineno or selected.lineno
    indent = re.match(r"\s*", lines[selected.lineno - 1]).group(0)
    receipt = (
        f'{indent}logging.info("C3 write receipt: {rel_path} write side effect recorded")'
        f"{_line_ending_for(lines, selected.lineno - 1)}"
    )
    lines.insert(end_line, receipt)
    updated = "".join(lines)
    ast.parse(updated, filename=str(path))
    # Preserve the existing newline bytes; PowerShell/Windows defaults would otherwise
    # expand unchanged LF files to CRLF and make the wave diff unreadable.
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(updated)
    return {
        "file": rel_path,
        "status": "instrumented",
        "receipt_line": end_line + 1,
        "write_statement_line": selected.lineno,
    }


def _load_previous_files(path: Path) -> set[str]:
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return {row["file"] for row in data.get("files", [])}


def _query_rows(sqlite_path: Path) -> list[C3Row]:
    conn = sqlite3.connect(sqlite_path)
    try:
        grouped: dict[tuple[str, str, int], set[str]] = {}
        for raw_path, layer, node_id, symbol in conn.execute(QUERY):
            key = (raw_path.replace("\\", "/"), layer, node_id)
            grouped.setdefault(key, set()).add(symbol or "")
        return [
            C3Row(path=path, layer=layer, node_id=node_id, symbols=tuple(sorted(symbols)))
            for (path, layer, node_id), symbols in grouped.items()
        ]
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--sqlite", type=Path, required=True)
    parser.add_argument("--previous-proof", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--wave-size", type=int, default=25)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    previous = _load_previous_files(args.previous_proof)
    rows = _query_rows(args.sqlite)

    selected: list[C3Row] = []
    skipped: list[dict[str, object]] = []
    for row in rows:
        path = repo_root / row.path
        if row.path in previous:
            skipped.append({"file": row.path, "reason": "previous_wave"})
            continue
        if not path.exists():
            skipped.append({"file": row.path, "reason": "missing_file"})
            continue
        if "C3 write receipt:" in path.read_text(encoding="utf-8", errors="ignore"):
            skipped.append({"file": row.path, "reason": "already_instrumented"})
            continue
        selected.append(row)
        if len(selected) >= args.limit:
            break

    results: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    for row in selected:
        try:
            result = _instrument_file(repo_root, row)
            result.update({"layer": row.layer, "node_id": row.node_id})
            results.append(result)
        except Exception as exc:  # noqa: BLE001 - fail-closed proof artifact needs exact row error.
            failures.append({"file": row.path, "error": f"{type(exc).__name__}: {exc}"})

    waves = []
    for index in range(0, len(results), args.wave_size):
        rows_for_wave = results[index : index + args.wave_size]
        waves.append(
            {
                "wave_id": f"W7.C3.{2 + index // args.wave_size}",
                "planned_rows": len(rows_for_wave),
                "files": [row["file"] for row in rows_for_wave],
            }
        )

    payload = {
        "schema_version": "adg-c3-apply-waves/v1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "adg_snapshot_id": "07072026_2307",
        "gate_id": "C3_silent_writes_ratchet",
        "source_sqlite": str(args.sqlite),
        "wave_size": args.wave_size,
        "requested_limit": args.limit,
        "snapshot_rows": len(rows),
        "previous_wave_rows": len(previous),
        "selected_rows": len(selected),
        "instrumented_rows": len(results),
        "failed_rows": len(failures),
        "waves": waves,
        "layer_counts": dict(Counter(row["layer"] for row in results)),
        "results": results,
        "skipped": skipped,
        "failures": failures,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("selected_rows", "instrumented_rows", "failed_rows")}, indent=2))
    return 0 if not failures and results else 1


if __name__ == "__main__":
    raise SystemExit(main())
