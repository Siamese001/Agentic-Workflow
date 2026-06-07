#!/usr/bin/env python3
"""apps_rg layer-assignment audit (advisory).

apps_rg engines were mass-decorated by name-pattern policy. This report
flags engines whose declared layer might not match the method's actual
semantics, by inspecting the AST for write-side / read-side / emit-side
patterns inside the method body.

Heuristics (advisory only — operator review required):

  * Method body calls `self._XXX_LOG.debug(...)` for `_AGENT_DISPATCH_LOG`,
    `_WRITES_THROUGH_LOG`, etc. → likely L4_STATE or L6_OBSERVABILITY,
    not L3_ORCHESTRATION (the default).
  * Method body has more `return` than control-flow ops → likely a pure
    L1_COGNITION compute, not L3 orchestration.
  * Method body calls something like `repository.save()` / `db.write()`
    / `cache.set()` → confirmed L4_STATE.
  * Method body calls `await tracer.start_span()` or `_emit_*` → already
    instrumented at a different level; layer assignment may be redundant.

Output: ``artifacts/observability/apps_rg_layer_audit.md`` — markdown
report listing each engine with current layer, suggested layer, and
evidence. Operator reviews and amends `required_spans.yaml` manually.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (P5 NEXT_STEP)
"""
from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

OUT_DIR = REPO / "artifacts" / "observability"
OUT_FILE = OUT_DIR / "apps_rg_layer_audit.md"

# Patterns indicating a layer beyond the name-pattern default.
WRITE_PATTERNS = (
    "_AGENT_DISPATCH_LOG", "_WRITES_THROUGH_LOG", "_STORES_EMBEDDING_LOG",
    ".save(", ".write(", ".store(", ".persist(", ".commit(",
    "cache.set", "repository.add", "repository.put", "repository.write",
)
EMIT_PATTERNS = (
    "_emit_records_telemetry_event", "_emit_captures_evaluation_metric",
    "tracer.start", "_TRANSCRIPT_LOG", "_HARDFAIL_LOG",
)
READ_PATTERNS = (
    ".get(", ".find(", ".search(", ".query(", ".fetch(",
    "cache.get", "repository.find", "repository.list",
)


def _classify_method(file_path: Path, class_name: str, method_name: str) -> tuple[str, list[str], bool]:
    """Inspect method body and return (suggested_layer, evidence, defined_here).

    `defined_here` is False when the class+method isn't actually defined
    in this file (e.g. inherited from BaseRGEngine). Inherited methods
    get classified once — at the file where they're actually defined —
    so we skip them in derived files.
    """
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return "UNKNOWN", [], False

    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for sub in node.body:
            if not isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if sub.name != method_name:
                continue
            body_src = ast.unparse(sub)
            evidence: list[str] = []
            write_hits = sum(1 for p in WRITE_PATTERNS if p in body_src)
            emit_hits = sum(1 for p in EMIT_PATTERNS if p in body_src)
            read_hits = sum(1 for p in READ_PATTERNS if p in body_src)
            if write_hits:
                evidence.append(f"write_patterns={write_hits}")
            if emit_hits:
                evidence.append(f"emit_patterns={emit_hits}")
            if read_hits:
                evidence.append(f"read_patterns={read_hits}")

            if write_hits >= 2:
                return "L4_STATE", evidence, True
            if emit_hits >= 2:
                return "L6_OBSERVABILITY", evidence, True
            if read_hits >= 3 and write_hits == 0:
                return "L1_COGNITION", evidence, True
            return "(no change)", evidence, True
    return "(inherited — not defined in this file)", [], False


def _scan_apps_rg() -> list[dict]:
    rows: list[dict] = []
    eng_dir = REPO / "apps_rg" / "engines"
    for f in sorted(eng_dir.glob("*.py")):
        if f.name.startswith(("_", ".")) or f.name == "__init__.py":
            continue
        mod_id = f"apps_rg.engines.{f.stem}"
        try:
            mod = importlib.import_module(mod_id)
        except ImportError:
            continue
        for name in dir(mod):
            try:
                obj = getattr(mod, name, None)
            except Exception:  # noqa: BLE001
                continue
            if not isinstance(obj, type):
                continue
            for attr_name, attr in vars(obj).items():
                marker = getattr(attr, "__adg_traces_execute__", None)
                if not marker:
                    continue
                current = getattr(attr, "__adg_traces_layer__", "UNKNOWN")
                qual = marker[0]
                cls_name, meth_name = qual.split(".", 1)
                suggested, evidence, defined_here = _classify_method(f, cls_name, meth_name)
                if not defined_here:
                    # Skip inherited methods — they get classified once,
                    # at their definition site (e.g. base_rg_engine.py).
                    continue
                rows.append({
                    "file": f.relative_to(REPO).as_posix(),
                    "qual": qual,
                    "current_layer": current,
                    "suggested_layer": suggested,
                    "evidence": ", ".join(evidence) or "(none)",
                    "needs_review": suggested != "(no change)" and suggested != current,
                })
    return rows


def main() -> int:
    rows = _scan_apps_rg()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    needs_review = [r for r in rows if r["needs_review"]]
    confirmed = [r for r in rows if not r["needs_review"]]

    lines: list[str] = []
    lines.append("# apps_rg Layer Audit — Advisory Report")
    lines.append("")
    lines.append(f"Generated: {len(rows)} decorated methods scanned")
    lines.append(f"  - Confirmed (current layer matches AST evidence): **{len(confirmed)}**")
    lines.append(f"  - Needs operator review: **{len(needs_review)}**")
    lines.append("")
    lines.append("## How to read this report")
    lines.append("")
    lines.append("Each apps_rg engine method was decorated by the W-OTEL name-pattern policy. ")
    lines.append("This report inspects the method body for write/read/emit signatures and ")
    lines.append("flags methods where AST evidence suggests a different layer than was assigned.")
    lines.append("")
    lines.append("**This is advisory.** Operator reviews each `needs_review` row and either:")
    lines.append("1. Updates the decorator's `layer=` kwarg to the suggested layer, OR")
    lines.append("2. Documents in the engine's docstring why the current layer is correct.")
    lines.append("")
    lines.append("After remediation, regenerate `required_spans.yaml` and confirm L3 gate passes.")
    lines.append("")

    if needs_review:
        lines.append("## Methods needing review")
        lines.append("")
        lines.append("| File | Method | Current | Suggested | Evidence |")
        lines.append("|---|---|---|---|---|")
        for r in needs_review:
            lines.append(
                f"| `{r['file']}` | `{r['qual']}` | `{r['current_layer']}` | "
                f"**`{r['suggested_layer']}`** | {r['evidence']} |"
            )
        lines.append("")
    else:
        lines.append("## ✅ No methods flagged for review")
        lines.append("")
        lines.append("All apps_rg layer assignments are consistent with AST evidence.")
        lines.append("")

    lines.append("## Confirmed methods (current layer matches evidence)")
    lines.append("")
    lines.append(f"{len(confirmed)} methods. See report metadata for full list — abbreviated here.")
    lines.append("")
    if confirmed[:10]:
        lines.append("| Method | Current Layer |")
        lines.append("|---|---|")
        for r in confirmed[:10]:
            lines.append(f"| `{r['qual']}` | `{r['current_layer']}` |")
        if len(confirmed) > 10:
            lines.append(f"| ... | ({len(confirmed) - 10} more) |")
        lines.append("")

    OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO).as_posix()}")
    print(f"  total={len(rows)}, confirmed={len(confirmed)}, needs_review={len(needs_review)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
