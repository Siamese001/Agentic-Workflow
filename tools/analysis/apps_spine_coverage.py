"""Audit apps_* runtime-mode classification + spine coverage.

Classifies each ``apps_*`` package into one of the five canonical
buckets defined in ``docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md``:

    CORE_ONLY_VALID            non-app spine paths (reserved)
    APP_OVERLAY_VALID          app delegates to the spine via canonical contracts
    APP_STANDALONE_FORBIDDEN   app claims a domain runtime but holds zero contracts
    PARTIAL_SPINE_STATIC_ONLY  app imports infrastructure (UWG/ledger/BGE) but no
                               authority-class contracts
    UNKNOWN_NEEDS_RUNTIME_TRACE static evidence is ambiguous; needs runtime trace

The authority-class contract set is fixed:

    L1PlanContract, RouteContract, FinalEvidenceContract,
    CompiledPromptArtifact, PromptEnvelope, ValidatedRequest,
    SealedArtifact, ExitReviewPacket, CommitRequest,
    RuntimeExhaustBundle, RetrievalPlan, StateDiffCandidate,
    GateVerdict

An app that imports any of these from ``agentic_core`` qualifies for
``APP_OVERLAY_VALID``. An app that only imports ``apps_shared`` or
transitive infrastructure (write_gateway, bge_runtime, ledgers, OTel
tracing) without any authority-class contract handoff is
``PARTIAL_SPINE_STATIC_ONLY``: importing apps_shared alone CANNOT make
an app valid.

The scanner does NOT penalize core-only paths and does NOT require
``apps_*`` for generic core capabilities. It ONLY flags ``apps_*``
packages that claim a domain runtime (have engines / a CLI / a wizard /
a route registry) but provide no authority-handoff evidence.

Usage:
    python -m tools.analysis.apps_spine_coverage [--json] [--app APP]

Output:
    - Markdown table to stdout (default)
    - JSON to stdout (--json)
    - Single-app deep-dive if --app APP given

Reused by:
    - Plan SSOT generation (.windsurf/plans/apps-spine-integration-*.md)
    - Future CI gate for runtime-mode ratchets
    - Tests at tests/unit/tools/analysis/test_apps_spine_coverage.py

Legacy keys preserved on the JSON output for backward-compat with the
spine-coverage-pct metric. New keys: ``runtime_mode``, ``contract_imports``,
``claims_domain_runtime``, ``classification_evidence``.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Canonical authority-class contract symbols. Importing any of these from
# ``agentic_core`` is the load-bearing evidence that an app delegates to the
# spine rather than running a shadow runtime. ``apps_shared`` re-exports do
# NOT count -- the import must be from ``agentic_core`` directly so the
# delegation chain is auditable.
#
# Source of truth: docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md.
# When a new spine contract type is added, add it here too.
# ---------------------------------------------------------------------------
CANONICAL_CONTRACTS: frozenset[str] = frozenset({
    "L1PlanContract",
    "RouteContract",
    "FinalEvidenceContract",
    "CompiledPromptArtifact",
    "PromptEnvelope",
    "ValidatedRequest",
    "SealedArtifact",
    "ExitReviewPacket",
    "CommitRequest",
    "RuntimeExhaustBundle",
    "RetrievalPlan",
    "StateDiffCandidate",
    "MutationIntent",
    "GateVerdict",
})

# Heuristic markers that an app CLAIMS a domain runtime (i.e., does more
# than passive type definitions). The presence of any of these patterns
# means the app is on the hook for delegation evidence; their absence
# means an app is purely a schema/types package and the scanner classifies
# it ``UNKNOWN_NEEDS_RUNTIME_TRACE`` instead of forbidden.
_DOMAIN_RUNTIME_MARKERS: tuple[tuple[str, str], ...] = (
    ("engines/", "engines directory present"),
    ("integrations/", "integrations directory present"),
    ("router/", "router subpackage present"),
    ("scripts/run_", "CLI runner present"),
    ("scripts/__main__.py", "CLI entrypoint present"),
    ("__main__.py", "package entrypoint present"),
    ("wizard.py", "interactive wizard present"),
    ("control_plane.py", "control-plane module present"),
    ("governed_", "governed_<X>_run.py present"),
)

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


def _safe_relative_path(py: Path, app_dir: Path) -> str:
    """Return a stable string path for an audited file.

    Prefers ``py.relative_to(REPO_ROOT)`` so callsite paths remain
    reproducible across machines. When the audited app sits outside the
    repo (test fixtures using ``tmp_path``), falls back to a path
    relative to the app's own root prefixed with the app's directory
    name. Final fallback: stringify the absolute path.
    """
    try:
        return str(py.relative_to(REPO_ROOT))
    except ValueError:
        try:
            return f"{app_dir.name}/{py.relative_to(app_dir)}"
        except ValueError:
            return str(py)


def _detect_domain_runtime_claims(app_dir: Path) -> list[str]:
    """Return reasons (human-readable) why an app claims a domain runtime.

    Empty list means the app is a passive types/schemas package and the
    scanner classifies it ``UNKNOWN_NEEDS_RUNTIME_TRACE`` rather than
    forbidden. Non-empty list means the app is on the hook for canonical
    contract delegation evidence.
    """
    reasons: list[str] = []
    for marker, label in _DOMAIN_RUNTIME_MARKERS:
        candidates = list(app_dir.rglob(f"*{marker}*")) if marker.endswith("/") else list(app_dir.rglob(marker))
        # rglob with trailing slash doesn't filter dirs strictly; fall back
        # to a directory-existence test for the directory markers.
        if marker.endswith("/"):
            sub = app_dir / marker.rstrip("/")
            if sub.is_dir() and any(sub.rglob("*.py")):
                reasons.append(label)
        elif candidates:
            # Verify at least one candidate is a real file (rglob can match
            # path stems too).
            for c in candidates:
                if c.is_file() and c.suffix == ".py":
                    reasons.append(label)
                    break
    return reasons


def scan_app(app_dir: Path) -> dict:
    """Return per-app scorecard with delegation-evidence classification.

    Adds the following keys vs the legacy import-edge metric:

    - ``runtime_mode``         one of the five buckets in the module docstring
    - ``contract_imports``     {contract_name: [callsites]}
    - ``claims_domain_runtime`` bool (any _DOMAIN_RUNTIME_MARKERS hit)
    - ``domain_runtime_reasons`` human-readable reason list
    - ``classification_evidence`` short human-readable verdict explanation
    """
    zone_counts: Counter[str] = Counter()
    layer_counts: Counter[str] = Counter()
    uwg_hits: list[tuple[str, int]] = []
    files_scanned = 0
    parse_errors = 0
    contract_imports: dict[str, list[str]] = {}

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
        rel_path = _safe_relative_path(py, app_dir)
        for node in ast.walk(tree):
            mods: list[str] = []
            symbol_names: list[str] = []
            if isinstance(node, ast.Import):
                mods = [n.name for n in node.names]
            elif isinstance(node, ast.ImportFrom):
                mods = [node.module or ""]
                symbol_names = [n.name for n in node.names]
            for mod in mods:
                zone, sub = _classify(mod)
                zone_counts[zone] += 1
                if zone == "agentic_core":
                    layer_counts[sub] += 1
                if _is_uwg_token(mod):
                    # rel_path was already _safe_relative_path-resolved above.
                    uwg_hits.append((rel_path, getattr(node, "lineno", 0)))
            # Authority-class contract detection: only counts when imported
            # FROM agentic_core (apps_shared re-exports do not qualify per
            # the doc).
            if (
                isinstance(node, ast.ImportFrom)
                and node.module is not None
                and node.module.startswith("agentic_core")
            ):
                for sym in symbol_names:
                    if sym in CANONICAL_CONTRACTS:
                        contract_imports.setdefault(sym, []).append(
                            f"{rel_path}:{getattr(node, 'lineno', 0)}"
                        )

    total_edges = sum(zone_counts.values())
    non_stdlib = total_edges - zone_counts.get("stdlib", 0)
    agentic_edges = zone_counts.get("agentic_core", 0)
    spine_score = (agentic_edges / non_stdlib) if non_stdlib > 0 else 0.0

    layers_touched = sorted(layer_counts.keys())
    has_uwg = len(uwg_hits) > 0
    has_meta_learning = zone_counts.get("system_learning", 0) > 0

    domain_runtime_reasons = _detect_domain_runtime_claims(app_dir)
    claims_domain_runtime = bool(domain_runtime_reasons)

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
        # NEW (W6): runtime-mode delegation-evidence fields.
        "contract_imports": {
            name: sites for name, sites in sorted(contract_imports.items())
        },
        "contract_count": sum(len(v) for v in contract_imports.values()),
        "distinct_contracts": sorted(contract_imports.keys()),
        "claims_domain_runtime": claims_domain_runtime,
        "domain_runtime_reasons": domain_runtime_reasons,
    }


def classify_app(scorecard: dict) -> tuple[str, str]:
    """Return (runtime_mode, evidence) per APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md.

    Five-bucket classification:

    - APP_OVERLAY_VALID: app imports >= 1 canonical authority contract
    - APP_STANDALONE_FORBIDDEN: app claims a domain runtime AND has zero
      contract imports AND has zero meaningful spine import edges. The
      most actively-violating bucket.
    - PARTIAL_SPINE_STATIC_ONLY: app imports infrastructure (UWG / ledger
      / BGE / spans) but no authority-class contracts. Spine touches the
      static surface, not the runtime delegation surface.
    - UNKNOWN_NEEDS_RUNTIME_TRACE: app does NOT claim a domain runtime
      (no engines/integrations/router/CLI), so static analysis cannot
      prove forbidden status. Needs runtime evidence (OTel spans, ledger
      rows) to classify.
    - CORE_ONLY_VALID: reserved (not assigned to apps; the scanner uses
      this only when audited path is not under apps_*).

    The legacy `"status"` key is preserved as a derived field for
    backward-compat with downstream consumers; the new `"runtime_mode"`
    key is the canonical one.
    """
    if scorecard["non_stdlib_edges"] == 0:
        return (
            "UNKNOWN_NEEDS_RUNTIME_TRACE",
            "empty package: no non-stdlib imports; cannot statically classify",
        )

    has_contracts = scorecard["contract_count"] > 0
    claims_runtime = scorecard["claims_domain_runtime"]
    has_static_spine = scorecard["agentic_core_edges"] > 0 or scorecard["has_uwg_usage"]

    if has_contracts:
        return (
            "APP_OVERLAY_VALID",
            f"imports {scorecard['contract_count']} canonical contract(s) "
            f"({', '.join(scorecard['distinct_contracts'])}) directly from agentic_core",
        )

    if not claims_runtime:
        return (
            "UNKNOWN_NEEDS_RUNTIME_TRACE",
            "no domain-runtime markers (engines/integrations/router/CLI); "
            "static analysis cannot decide; runtime trace required",
        )

    if has_static_spine:
        return (
            "PARTIAL_SPINE_STATIC_ONLY",
            "claims domain runtime AND imports spine infrastructure (UWG/ledger/BGE), "
            "BUT zero canonical contract imports; static-only spine touch, "
            "runtime authority is local to the app -- not valid as APP_OVERLAY",
        )

    return (
        "APP_STANDALONE_FORBIDDEN",
        "claims domain runtime ("
        + ", ".join(scorecard["domain_runtime_reasons"])
        + ") AND zero canonical contracts AND zero spine import edges; "
        + "shadow runtime; constitutional violation",
    )


def _legacy_status_for(scorecard: dict) -> str:
    """Compute the legacy ON_SPINE / PARTIAL_SPINE / ... bucket.

    Preserved for downstream consumers that grep on the old strings;
    new consumers should read ``runtime_mode`` instead.
    """
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
        runtime_mode, evidence = classify_app(sc)
        sc["runtime_mode"] = runtime_mode
        sc["classification_evidence"] = evidence
        sc["status"] = _legacy_status_for(sc)  # backward-compat
        results.append(sc)
    return results


_RUNTIME_MODE_EMOJI: dict[str, str] = {
    "APP_OVERLAY_VALID": "✅",
    "APP_STANDALONE_FORBIDDEN": "🔴",
    "PARTIAL_SPINE_STATIC_ONLY": "🟠",
    "UNKNOWN_NEEDS_RUNTIME_TRACE": "❔",
    "CORE_ONLY_VALID": "🔵",
}


def render_markdown(results: list[dict]) -> str:
    lines = []
    lines.append("# apps_* runtime-mode scorecard")
    lines.append("")
    lines.append(
        "**Methodology**: AST scan of every `apps_*/` package (excluding "
        "tests/fixtures). Detects (a) imports of canonical authority-class "
        "contracts FROM `agentic_core`, (b) domain-runtime markers "
        "(engines/integrations/router/CLI/wizard), and (c) infrastructure "
        "imports (UWG/ledger/BGE). Classifies per the five-bucket taxonomy "
        "in `docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md`."
    )
    lines.append("")
    lines.append(
        "**Authority-class contracts**: " + ", ".join(
            f"`{c}`" for c in sorted(CANONICAL_CONTRACTS)
        )
    )
    lines.append("")
    lines.append(
        "| App | Files | Spine % (legacy) | Contracts | Distinct contracts | Claims runtime | Runtime Mode |"
    )
    lines.append(
        "|---|---:|---:|---:|---|:---:|---|"
    )
    for r in results:
        rm = r.get("runtime_mode", "UNKNOWN_NEEDS_RUNTIME_TRACE")
        emoji = _RUNTIME_MODE_EMOJI.get(rm, "?")
        contract_summary = (
            ", ".join(f"`{c}`" for c in r["distinct_contracts"])
            if r["distinct_contracts"]
            else "—"
        )
        claims = "✓" if r["claims_domain_runtime"] else "—"
        lines.append(
            f"| `{r['app']}` | {r['files_scanned']} | {r['spine_coverage_pct']}% | "
            f"{r['contract_count']} | {contract_summary} | {claims} | {emoji} {rm} |"
        )
    lines.append("")
    lines.append("## Runtime-mode legend")
    lines.append("")
    lines.append(
        "- ✅ **APP_OVERLAY_VALID** — imports ≥1 canonical authority "
        "contract from `agentic_core`. Delegates to the spine."
    )
    lines.append(
        "- � **APP_STANDALONE_FORBIDDEN** — claims a domain runtime "
        "(engines/integrations/router/CLI) AND imports zero canonical "
        "contracts AND zero spine edges. Shadow runtime."
    )
    lines.append(
        "- 🟠 **PARTIAL_SPINE_STATIC_ONLY** — claims domain runtime AND "
        "imports spine infrastructure (UWG/ledger/BGE), BUT no "
        "authority-class contracts. Static-only spine touch."
    )
    lines.append(
        "- ❔ **UNKNOWN_NEEDS_RUNTIME_TRACE** — does not claim a domain "
        "runtime; static analysis cannot decide. Runtime trace required."
    )
    lines.append(
        "- � **CORE_ONLY_VALID** — reserved for non-`apps_*` paths."
    )
    lines.append("")
    lines.append("## Per-app classification evidence")
    lines.append("")
    for r in results:
        rm = r.get("runtime_mode", "UNKNOWN_NEEDS_RUNTIME_TRACE")
        ev = r.get("classification_evidence", "")
        emoji = _RUNTIME_MODE_EMOJI.get(rm, "?")
        lines.append(f"- {emoji} **`{r['app']}`** → {rm}")
        lines.append(f"  - {ev}")
        if r["distinct_contracts"]:
            lines.append(f"  - contracts: {', '.join(r['distinct_contracts'])}")
        if r["domain_runtime_reasons"]:
            lines.append(
                f"  - claims runtime via: {', '.join(r['domain_runtime_reasons'])}"
            )
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
        runtime_mode, evidence = classify_app(sc)
        sc["runtime_mode"] = runtime_mode
        sc["classification_evidence"] = evidence
        sc["status"] = _legacy_status_for(sc)
        # JSON in either branch — single-app deep-dive is always
        # machine-readable since the markdown render is built for the
        # multi-app comparison view.
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
