#!/usr/bin/env python3
"""
CI gate: check_graph_layer_evidence.py
Constitutional rule §22.

ARCHITECTURE: The ADG is implemented as SQLite (a relational database) with
a graph-layer overlay: ``nodes`` + ``edges`` tables, materialized views
(``mv_*``) that pre-compute graph traversals (centrality, chokepoints, blast
radius, critical paths), pre-classified P-views (``v_p0_*``..``v_p3_*``), and
semantic edges (``flows_to``, ``reads_from``, ``writes_to``, ``emits_side_effect``,
``controls_flow``, ``resolves_callsite``). The overlay provides graph-database
semantics over a relational store — no separate Neo4j/ArangoDB backend needed.

This gate enforces that T2/T3 refactoring plans use the graph-layer primitives
(MVs, semantic edges, P-views) as PRIMARY drivers — not raw ``edges`` /
``violations`` table aggregations and never grep.

Scans .windsurf/plans/*.md and validates that plans which declare a
refactoring intent include an ``## ADG_GRAPH_LAYER_EVIDENCE`` section with:
  * at least 3 materialized views (mv_*) cited
  * at least 1 semantic-edge relation beyond 'imports' OR 1 P-view cross-ref

Plans that LACK a refactoring intent (question plans, docs-only plans) are
skipped. Violations are logged to artifacts/windsurf/graph_layer_violations.jsonl
and the gate exits non-zero.

Run manually:
  python ops_scripts/ci/check_graph_layer_evidence.py
"""

from __future__ import annotations

import json
import re
import subprocess  # noqa: F401  -- reserved for future git-blame lookup
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = ROOT / ".windsurf" / "plans"
LOG_DIR = ROOT / "artifacts" / "windsurf"
LOG_FILE = LOG_DIR / "graph_layer_violations.jsonl"
BASELINE_FILE = ROOT / "ops_scripts" / "ci" / "baselines" / "graph_layer_evidence_baseline.json"

# --- Patterns -----------------------------------------------------------------

REFACTOR_INTENT_PATTERNS = (
    re.compile(r"\brefactor(?:ing)?\b", re.IGNORECASE),
    re.compile(r"\bburn[- ]?down\b", re.IGNORECASE),
    re.compile(r"\bwave plan\b", re.IGNORECASE),
    re.compile(r"\bhotspot\b", re.IGNORECASE),
    re.compile(r"\bP[0-3] ratchet\b"),
    re.compile(r"\bantipattern (?:burn|fix|reduction)\b", re.IGNORECASE),
)

EVIDENCE_HEADER = re.compile(
    r"^#{1,4}\s*ADG[_ ]GRAPH[_ ]LAYER[_ ]EVIDENCE\b", re.IGNORECASE | re.MULTILINE
)
HOTSPOT_HEADER = re.compile(
    r"^#{1,4}\s*ADG[_ ]HOTSPOT[_ ]REPORT\b", re.IGNORECASE | re.MULTILINE
)

MV_PATTERN = re.compile(r"\bmv_[a-z][a-z0-9_]+\b", re.IGNORECASE)
PVIEW_PATTERN = re.compile(r"\bv_p[0-3]_[a-z][a-z0-9_]+\b", re.IGNORECASE)
SEMANTIC_EDGE_NAMES = {
    "flows_to",
    "reads_from",
    "writes_to",
    "emits_side_effect",
    "controls_flow",
    "resolves_callsite",
}
SEMANTIC_EDGE_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(n) for n in SEMANTIC_EDGE_NAMES) + r")\b",
    re.IGNORECASE,
)

# Minimum distinct materialized views required
MIN_MVS = 3

# Archetypes that must classify every hotspot row (adg-canonical-invariants.md §5).
HOTSPOT_ARCHETYPES: frozenset[str] = frozenset(
    {
        "CENTRAL_DEPENDENCY",
        "ORCHESTRATOR",
        "STATE_NODE",
        "SAFETY_GATEKEEPER",
    }
)
ARCHETYPE_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(a) for a in HOTSPOT_ARCHETYPES) + r")\b"
)

# 5 ADG Surfaces that hotspot reports must cross-reference
# (adg-canonical-invariants.md §3).
ADG_SURFACES: frozenset[str] = frozenset(
    {
        "Execution Surface",
        "Write Surface",
        "Security Surface",
        "State Surface",
        "Observability Surface",
    }
)
SURFACE_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(s) for s in ADG_SURFACES) + r")\b",
    re.IGNORECASE,
)

# --- Logic --------------------------------------------------------------------


def _has_refactor_intent(text: str) -> bool:
    return any(p.search(text) for p in REFACTOR_INTENT_PATTERNS)


def _evaluate_plan(path: Path) -> dict | None:
    """Return a violation dict if plan fails the gate, else None."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "plan": str(path.relative_to(ROOT)),
            "reason": f"read_error: {exc}",
        }

    if not _has_refactor_intent(text):
        return None  # Non-refactor plans skipped

    missing: list[str] = []

    if not EVIDENCE_HEADER.search(text):
        missing.append("missing_adg_graph_layer_evidence_section")

    hotspot_match = HOTSPOT_HEADER.search(text)
    if not hotspot_match:
        missing.append(
            "missing_adg_hotspot_report_section "
            "(required by adg-hotspot-enforcement.md; "
            "plans must include ranked hotspot report from MV-driven analysis)"
        )
    else:
        # When the hotspot section exists, validate that it contains the
        # canonical classifications required by adg-canonical-invariants.md:
        # at least one archetype and at least one surface reference.
        hotspot_body = text[hotspot_match.start():]
        archetypes_cited = {m.group(1) for m in ARCHETYPE_PATTERN.finditer(hotspot_body)}
        surfaces_cited = {m.group(1).lower() for m in SURFACE_PATTERN.finditer(hotspot_body)}
        if not archetypes_cited:
            missing.append(
                "hotspot_report_missing_archetype "
                f"(required: one of {sorted(HOTSPOT_ARCHETYPES)})"
            )
        if not surfaces_cited:
            missing.append(
                "hotspot_report_missing_surface_reference "
                f"(required: at least one of {sorted(ADG_SURFACES)} or the literal 'none')"
            )

    mvs_cited = {m.group(0).lower() for m in MV_PATTERN.finditer(text)}
    if len(mvs_cited) < MIN_MVS:
        missing.append(
            f"insufficient_materialized_views cited={len(mvs_cited)} required={MIN_MVS}"
        )

    semantic_hits = {m.group(1).lower() for m in SEMANTIC_EDGE_PATTERN.finditer(text)}
    pview_hits = {m.group(0).lower() for m in PVIEW_PATTERN.finditer(text)}
    if not semantic_hits and not pview_hits:
        missing.append(
            "no_semantic_edge_or_pview — must cite at least one of "
            f"{sorted(SEMANTIC_EDGE_NAMES)} or v_p0/1/2/3_* view"
        )

    if not missing:
        return None

    return {
        "plan": str(path.relative_to(ROOT)),
        "missing": missing,
        "mvs_cited": sorted(mvs_cited),
        "semantic_edges_cited": sorted(semantic_hits),
        "pviews_cited": sorted(pview_hits),
    }


def _load_baseline() -> set[str]:
    """Load grandfathered plan paths (plans existing at rule-adoption time)."""
    if not BASELINE_FILE.exists():
        return set()
    try:
        data = json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[check_graph_layer_evidence] WARNING: baseline read failed: {exc}")
        return set()
    return set(data.get("grandfathered_plans", []))


def _validate_baseline_integrity(baseline: set[str], plans: list[Path]) -> list[str]:
    """Validate the grandfathered-plans baseline for integrity.

    Two failure modes detected:
      1. ORPHANED entries — baseline lists a plan that no longer exists on disk
         (silent rot: would allow a future plan with the same name to bypass
         the gate).
      2. DUPLICATE entries — the same plan path appears more than once in the
         JSON list (shouldn't happen in clean SSOT; indicates human error).

    Returns a list of issue strings; empty when integrity is intact.
    """
    issues: list[str] = []

    # Duplicate detection requires re-reading the raw list (not the set form).
    if BASELINE_FILE.exists():
        try:
            raw = json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
            listed = raw.get("grandfathered_plans", [])
            if not isinstance(listed, list):
                issues.append(
                    "baseline_schema_invalid — grandfathered_plans is not a list"
                )
            else:
                seen: set[str] = set()
                for entry in listed:
                    if entry in seen:
                        issues.append(f"baseline_duplicate_entry — {entry!r} listed twice")
                    seen.add(entry)
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(f"baseline_parse_error — {type(exc).__name__}: {exc}")

    # Orphan detection — every baseline entry must correspond to an existing plan.
    existing_rel = {
        str(p.relative_to(ROOT)).replace("\\", "/") for p in plans
    }
    for entry in sorted(baseline):
        if entry not in existing_rel:
            issues.append(
                f"baseline_orphan_entry — {entry!r} is grandfathered but no such plan exists"
            )

    return issues


def main() -> int:
    if not PLANS_DIR.is_dir():
        print(f"[check_graph_layer_evidence] plans dir missing: {PLANS_DIR}")
        return 0  # Not blocking on missing dir — no plans to check

    plans = sorted(p for p in PLANS_DIR.rglob("*.md") if p.is_file())
    if not plans:
        print("[check_graph_layer_evidence] no plans found — OK")
        return 0

    baseline = _load_baseline()

    # Baseline integrity — orphaned and duplicate entries are silent bypasses.
    integrity_issues = _validate_baseline_integrity(baseline, plans)
    if integrity_issues:
        print(
            f"\n[check_graph_layer_evidence] FAIL — "
            f"{len(integrity_issues)} baseline integrity issue(s):"
        )
        for issue in integrity_issues:
            print(f"  - {issue}")
        print(
            "\nFix: remove stale entries from "
            "ops_scripts/ci/baselines/graph_layer_evidence_baseline.json "
            "or restore the missing plan file. Duplicate entries must be deduped."
        )
        return 1

    violations: list[dict] = []
    skipped_grandfathered = 0
    for idx, plan in enumerate(plans, 1):
        rel = str(plan.relative_to(ROOT)).replace("\\", "/")
        if rel in baseline:
            skipped_grandfathered += 1
            continue
        print(
            f"  [{idx}/{len(plans)}] evaluating {plan.relative_to(ROOT)}"
        )
        result = _evaluate_plan(plan)
        if result is not None:
            violations.append(result)

    if violations:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).isoformat()
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            for v in violations:
                v["ts"] = ts
                fh.write(json.dumps(v, ensure_ascii=False) + "\n")
        print(
            f"\n[check_graph_layer_evidence] FAIL — "
            f"{len(violations)} plan(s) missing graph-layer evidence"
        )
        for v in violations:
            print(f"  - {v['plan']}")
            for m in v["missing"]:
                print(f"      * {m}")
        print(
            f"\nConstitutional rule §22 violated. "
            f"See .windsurf/rules/adg-graph-layer-enforcement.md"
        )
        print(f"Log: {LOG_FILE.relative_to(ROOT)}")
        return 1

    print(
        f"[check_graph_layer_evidence] PASS — "
        f"{len(plans) - skipped_grandfathered} plan(s) evaluated "
        f"({skipped_grandfathered} grandfathered), all refactor plans have graph-layer evidence"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
