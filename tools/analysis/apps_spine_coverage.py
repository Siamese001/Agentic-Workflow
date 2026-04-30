"""Audit apps_* spine coverage.

For each apps_* package, count outbound import edges into:
  - agentic_core/L0..L6 (each layer separately)
  - system_learning (meta-learning)
  - UWG / write_gateway symbols
  - apps_shared (shared resources, NOT spine)

Reports a scorecard:
  - Spine-coverage score: edges into agentic_core / total non-stdlib edges
  - Per-layer coverage: which layers each app touches
  - Off-spine flags: apps that bypass the spine entirely

Usage:
    python -m tools.analysis.apps_spine_coverage [--json] [--app APP]

Output:
    - Markdown table to stdout (default)
    - JSON to stdout (--json)
    - Single-app deep-dive if --app APP given

Reused by:
    - Plan SSOT generation (.windsurf/plans/apps-spine-integration-*.md)
    - Future CI gate for spine-coverage ratchets
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

STDLIB_PREFIXES = {
    "typing", "dataclasses", "pathlib", "json", "os", "sys", "re", "enum",
    "datetime", "collections", "functools", "itertools", "argparse", "logging",
    "contextlib", "copy", "io", "tempfile", "textwrap", "warnings",
    "subprocess", "time", "math", "hashlib", "uuid", "abc", "__future__",
    "shutil", "glob", "asyncio", "concurrent", "threading", "queue", "socket",
    "struct", "pickle", "csv", "string", "operator", "random", "secrets",
    "base64", "binascii", "zipfile", "tarfile", "platform", "errno",
    "traceback", "inspect", "importlib", "types", "weakref", "gc",
    "ast", "dis", "tokenize", "keyword", "parser", "symtable",
    "unittest", "doctest", "pdb", "profile", "cProfile", "trace",
    "fnmatch", "linecache", "atexit", "signal", "selectors",
    "http", "urllib", "email", "html", "xml", "json", "configparser",
}


def _classify(mod: str) -> tuple[str, str]:
    """Return (zone, sub_zone). zone is the headline; sub_zone splits agentic_core layers."""
    if not mod:
        return ("<empty>", "<empty>")
    head = mod.split(".")[0]
    if head in STDLIB_PREFIXES:
        return ("stdlib", "stdlib")
    if mod.startswith("agentic_core."):
        for layer in (
            "L0_routing", "L1_cognition", "L2_execution", "L3_orchestration",
            "L4_storage", "L5_safety", "L6_observability",
        ):
            if mod.startswith(f"agentic_core.{layer}"):
                return ("agentic_core", layer)
        return ("agentic_core", "agentic_core_other")
    if mod.startswith("system_learning"):
        return ("system_learning", "system_learning")
    if mod.startswith("apps_shared"):
        return ("apps_shared", "apps_shared")
    if mod.startswith("apps_"):
        return (f"sibling_apps", head)
    if mod.startswith("infrastructure"):
        return ("infrastructure", "infrastructure")
    if mod.startswith("tools"):
        return ("tools", "tools")
    return ("external", head)


def _is_uwg_token(mod: str) -> bool:
    lower = mod.lower()
    return (
        "uwg" in lower
        or "write_gateway" in lower
        or "durable_write" in lower
        or "writegateway" in lower.replace("_", "")
    )


def scan_app(app_dir: Path) -> dict:
    """Return per-app scorecard."""
    zone_counts: Counter[str] = Counter()
    layer_counts: Counter[str] = Counter()
    uwg_hits: list[tuple[str, int]] = []
    files_scanned = 0
    parse_errors = 0

    for py in app_dir.rglob("*.py"):
        # Skip tests for spine-routing analysis (tests have legitimate
        # reasons to import almost anything for fixturing).
        if any(part in {"tests", "_tests", "test", "fixtures"} for part in py.parts):
            continue
        files_scanned += 1
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            parse_errors += 1
            continue
        for node in ast.walk(tree):
            mods: list[str] = []
            if isinstance(node, ast.Import):
                mods = [n.name for n in node.names]
            elif isinstance(node, ast.ImportFrom):
                mods = [node.module or ""]
            for mod in mods:
                zone, sub = _classify(mod)
                zone_counts[zone] += 1
                if zone == "agentic_core":
                    layer_counts[sub] += 1
                if _is_uwg_token(mod):
                    uwg_hits.append((str(py.relative_to(REPO_ROOT)), getattr(node, "lineno", 0)))

    total_edges = sum(zone_counts.values())
    non_stdlib = total_edges - zone_counts.get("stdlib", 0)
    agentic_edges = zone_counts.get("agentic_core", 0)
    spine_score = (agentic_edges / non_stdlib) if non_stdlib > 0 else 0.0

    layers_touched = sorted(layer_counts.keys())
    has_uwg = len(uwg_hits) > 0
    has_meta_learning = zone_counts.get("system_learning", 0) > 0

    return {
        "app": app_dir.name,
        "files_scanned": files_scanned,
        "parse_errors": parse_errors,
        "total_import_edges": total_edges,
        "non_stdlib_edges": non_stdlib,
        "agentic_core_edges": agentic_edges,
        "spine_coverage_pct": round(spine_score * 100, 1),
        "system_learning_edges": zone_counts.get("system_learning", 0),
        "apps_shared_edges": zone_counts.get("apps_shared", 0),
        "infrastructure_edges": zone_counts.get("infrastructure", 0),
        "tools_edges": zone_counts.get("tools", 0),
        "external_edges": zone_counts.get("external", 0),
        "sibling_apps_edges": zone_counts.get("sibling_apps", 0),
        "layers_touched": layers_touched,
        "layer_counts": dict(layer_counts),
        "has_uwg_usage": has_uwg,
        "uwg_hit_count": len(uwg_hits),
        "uwg_hit_locations": uwg_hits[:5],
        "has_meta_learning_usage": has_meta_learning,
    }


def classify_app(scorecard: dict) -> str:
    """Bucket the app into a status label."""
    if scorecard["non_stdlib_edges"] == 0:
        return "EMPTY"
    if scorecard["agentic_core_edges"] == 0:
        return "OFF_SPINE"
    if scorecard["spine_coverage_pct"] < 5:
        return "BARELY_ON_SPINE"
    if scorecard["spine_coverage_pct"] < 20:
        return "PARTIAL_SPINE"
    return "ON_SPINE"


def scan_all() -> list[dict]:
    apps = sorted(
        d for d in REPO_ROOT.iterdir()
        if d.is_dir() and d.name.startswith("apps_")
    )
    results = []
    for app_dir in apps:
        sc = scan_app(app_dir)
        sc["status"] = classify_app(sc)
        results.append(sc)
    return results


def render_markdown(results: list[dict]) -> str:
    lines = []
    lines.append("# apps_* spine-coverage scorecard")
    lines.append("")
    lines.append("**Methodology**: AST scan of every `apps_*/` package (excluding tests/fixtures). Counts module-level `import` and `from ... import` edges and classifies the target.")
    lines.append("")
    lines.append("**Spine = `agentic_core/L0..L6`**. `apps_shared` is shared resources, not the spine. `system_learning` is meta-learning (separate but spine-adjacent invariant per constitutional §29).")
    lines.append("")
    lines.append(
        "| App | Files | Total | Non-stdlib | Spine edges | Spine % | UWG | Meta-Learning | Layers Touched | Status |"
    )
    lines.append(
        "|---|---:|---:|---:|---:|---:|:---:|:---:|---|---|"
    )
    for r in results:
        layers = ", ".join(L.replace("_routing", "").replace("_cognition", "").replace("_execution", "").replace("_orchestration", "").replace("_storage", "").replace("_safety", "").replace("_observability", "") for L in r["layers_touched"]) or "—"
        uwg = "✓" if r["has_uwg_usage"] else "—"
        ml = "✓" if r["has_meta_learning_usage"] else "—"
        status_emoji = {
            "ON_SPINE": "✅",
            "PARTIAL_SPINE": "🟡",
            "BARELY_ON_SPINE": "🟠",
            "OFF_SPINE": "🔴",
            "EMPTY": "⚪",
        }.get(r["status"], "?")
        lines.append(
            f"| `{r['app']}` | {r['files_scanned']} | {r['total_import_edges']} | {r['non_stdlib_edges']} | {r['agentic_core_edges']} | {r['spine_coverage_pct']}% | {uwg} | {ml} | {layers} | {status_emoji} {r['status']} |"
        )
    lines.append("")
    lines.append("## Status legend")
    lines.append("")
    lines.append("- ✅ **ON_SPINE** — ≥20% non-stdlib edges target `agentic_core/`. Spine-routed.")
    lines.append("- 🟡 **PARTIAL_SPINE** — 5–20%. Some spine, lots of bypass.")
    lines.append("- 🟠 **BARELY_ON_SPINE** — <5%. Token use of the spine; effectively independent.")
    lines.append("- 🔴 **OFF_SPINE** — Zero edges into `agentic_core/`. Constitutional violation.")
    lines.append("- ⚪ **EMPTY** — No non-stdlib edges (placeholder package).")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    parser.add_argument("--app", default=None, help="Deep-dive a single app (e.g. apps_qna)")
    args = parser.parse_args(argv)

    if args.app:
        app_dir = REPO_ROOT / args.app
        if not app_dir.is_dir():
            print(f"App not found: {args.app}", file=sys.stderr)
            return 1
        sc = scan_app(app_dir)
        sc["status"] = classify_app(sc)
        if args.json:
            print(json.dumps(sc, indent=2, default=str))
        else:
            print(json.dumps(sc, indent=2, default=str))
        return 0

    results = scan_all()
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(render_markdown(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
