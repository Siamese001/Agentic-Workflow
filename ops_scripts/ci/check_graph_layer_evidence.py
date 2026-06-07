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

Scans .claude/plans/*.md and validates that plans which declare a
refactoring intent include an ``## ADG_GRAPH_LAYER_EVIDENCE`` section with:
  * at least 3 materialized views (mv_*) cited
  * at least 1 semantic-edge relation beyond 'imports' OR 1 P-view cross-ref

Plans that LACK a refactoring intent (question plans, docs-only plans) are
skipped. Violations are logged to artifacts/cursor/graph_layer_violations.jsonl
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
# Active-plan evaluation SSOT (W3 archive): top-level `.claude/plans/*.md` only.
PLANS_DIR = ROOT / ".claude" / "plans"
_ACTIVE_PLAN_EXCLUDE_NAMES = frozenset({"README.md", "CURSOR_RUNTIME_SEAM_TEMPLATE.md"})
LOG_DIR = ROOT / "artifacts" / "windsurf"
LOG_FILE = LOG_DIR / "graph_layer_violations.jsonl"
BASELINE_FILE = ROOT / "ops_scripts" / "ci" / "baselines" / "graph_layer_evidence_baseline.json"

# SSOT plan trees — baseline entries may use `.claude/plans/` or `docs/archive/windsurf/legacy-tree/plans/`
# prefixes; integrity checks must resolve against both roots.
_PLAN_INTEGRITY_ROOTS: tuple[Path, ...] = (
    ROOT / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans",
    ROOT / ".claude" / "plans",
)

# --- Patterns -----------------------------------------------------------------

REFACTOR_INTENT_PATTERNS = (
    re.compile(r"\brefactor(?:ing)?\b", re.IGNORECASE),
    re.compile(r"\bburn[- ]?down\b", re.IGNORECASE),
    re.compile(r"\bwave plan\b", re.IGNORECASE),
    re.compile(r"\bhotspot\b", re.IGNORECASE),
    re.compile(r"\bP[0-3] ratchet\b"),
    re.compile(r"\bantipattern (?:burn|fix|reduction)\b", re.IGNORECASE),
)

# Frontmatter parser: YAML-style fenced block at top of file.
# ``plan_type`` is the authoritative signal; when present it overrides
# the keyword heuristic below.
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_PLAN_TYPE_RE = re.compile(r"^\s*plan_type\s*:\s*([A-Za-z0-9_\-]+)\s*$", re.MULTILINE)

# plan_type values that REQUIRE the §22 evidence sections.
_REFACTOR_PLAN_TYPES: frozenset[str] = frozenset({"refactor", "scoped_refactor"})

# plan_type values that are explicitly EXEMPT from §22 (governance, CI,
# documentation, audit, or infrastructure plans that do not drive code changes
# whose blast radius can be measured against the graph layer).
_EXEMPT_PLAN_TYPES: frozenset[str] = frozenset(
    {
        "governance",  # gates, schemas, CI policy
        "audit",  # observation / inventory, no code change
        "doc",  # documentation only
        "infra",  # infrastructure / tooling, not code refactor
        "tracker",  # descope trackers, status dashboards
        # Generic core contract/schema evolution plans: these add or export
        # types and contracts that apply to ALL apps uniformly.  Their scope
        # is the contract surface itself, not any graph-measurable blast
        # radius in the app/runtime dependency graph.  Graph-layer evidence
        # is therefore not meaningful and must not be required here.
        # Enforcement still applies to any plan with plan_type='refactor'
        # that *also* touches core — that case is handled by the refactor
        # path above, not by this exemption.
        "platform_core_change",  # generic core contract / export evolution
        "retrospective",  # RCA / look-back plans; no forward refactor blast radius
        # App / delivery shapes that are not graph-measurable refactors (§22 scope).
        "apps_rg_evidence",  # GTM / evidence packs — no ADG blast-radius driver
        "verification",  # proof-bundle / certification closeout
        "execution",  # runtime wiring / rollout execution
        "hardening",  # spine hardening without broad graph refactor
        "architecture",  # structural design doc — evidence added when coding starts
    }
)


def _parse_plan_type(text: str) -> str | None:
    """Return the plan_type frontmatter value, or None when absent/malformed.

    Only reads the first YAML-fenced block (``---`` ... ``---``) at the very
    top of the file. Returns the lowercase token. Non-string or missing key =
    None, which triggers the keyword heuristic fallback.
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None
    pt_match = _PLAN_TYPE_RE.search(m.group(1))
    if not pt_match:
        return None
    return pt_match.group(1).strip().lower()


EVIDENCE_HEADER = re.compile(r"^#{1,4}\s*ADG[_ ]GRAPH[_ ]LAYER[_ ]EVIDENCE\b", re.IGNORECASE | re.MULTILINE)
HOTSPOT_HEADER = re.compile(r"^#{1,4}\s*ADG[_ ]HOTSPOT[_ ]REPORT\b", re.IGNORECASE | re.MULTILINE)

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
ARCHETYPE_PATTERN = re.compile(r"\b(" + "|".join(re.escape(a) for a in HOTSPOT_ARCHETYPES) + r")\b")

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
    """Return a violation dict if plan fails the gate, else None.

    Scope resolution (authoritative → fallback):
      1. Frontmatter ``plan_type: refactor``   → enforce
      2. Frontmatter ``plan_type: <exempt>``    → skip (governance/audit/doc/...)
      3. No frontmatter                         → keyword heuristic
                                                  (preserves legacy behavior)
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "plan": str(path.relative_to(ROOT)),
            "reason": f"read_error: {exc}",
        }

    plan_type = _parse_plan_type(text)
    if plan_type is not None:
        # Frontmatter is authoritative.
        if plan_type in _EXEMPT_PLAN_TYPES:
            return None
        if plan_type not in _REFACTOR_PLAN_TYPES:
            return {
                "plan": str(path.relative_to(ROOT)),
                "missing": [
                    f"unknown_plan_type={plan_type!r} — must be one of "
                    f"{sorted(_REFACTOR_PLAN_TYPES | _EXEMPT_PLAN_TYPES)}"
                ],
            }
        # plan_type == "refactor" → fall through to enforcement below
    else:
        # No frontmatter → fall back to keyword heuristic for legacy plans.
        if not _has_refactor_intent(text):
            return None

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
        hotspot_body = text[hotspot_match.start() :]
        archetypes_cited = {m.group(1) for m in ARCHETYPE_PATTERN.finditer(hotspot_body)}
        surfaces_cited = {m.group(1).lower() for m in SURFACE_PATTERN.finditer(hotspot_body)}
        if not archetypes_cited:
            missing.append(
                f"hotspot_report_missing_archetype (required: one of {sorted(HOTSPOT_ARCHETYPES)})"
            )
        if not surfaces_cited:
            missing.append(
                "hotspot_report_missing_surface_reference "
                f"(required: at least one of {sorted(ADG_SURFACES)} or the literal 'none')"
            )

    mvs_cited = {m.group(0).lower() for m in MV_PATTERN.finditer(text)}
    if len(mvs_cited) < MIN_MVS:
        missing.append(f"insufficient_materialized_views cited={len(mvs_cited)} required={MIN_MVS}")

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


def _plan_relpaths_on_disk(*, include_archive: bool = True) -> set[str]:
    """All ``*.md`` paths under canonical plan dirs, relative to repo root."""
    rels: set[str] = set()
    for base in _PLAN_INTEGRITY_ROOTS:
        if not base.is_dir():
            continue
        for p in base.rglob("*.md"):
            if not p.is_file():
                continue
            if not include_archive and "_archive" in p.parts:
                continue
            rels.add(str(p.relative_to(ROOT)).replace("\\", "/"))
    return rels


def _baseline_entry_resolves(entry: str, existing_rel: set[str]) -> bool:
    """True when a grandfathered path exists at listed path, alias, or under ``_archive/``."""
    for alias in _grandfather_path_aliases(entry):
        if alias in existing_rel:
            return True
    # W3 archive: `.claude/plans/foo.md` may live at `.claude/plans/_archive/YYYY-MM/foo.md`
    for prefix in (".claude/plans/", "docs/archive/windsurf/legacy-tree/plans/"):
        if not entry.startswith(prefix):
            continue
        leaf = entry[len(prefix) :]
        if leaf.startswith("_archive/"):
            continue
        name = Path(leaf).name
        for base in _PLAN_INTEGRITY_ROOTS:
            archive_root = base / "_archive"
            if not archive_root.is_dir():
                continue
            for hit in archive_root.rglob(name):
                if hit.is_file() and hit.name == name:
                    return True
    return False


def _grandfather_path_aliases(rel: str) -> set[str]:
    """Baseline may list ``.claude/plans/…`` while the live file is under ``docs/archive/windsurf/legacy-tree/plans/…`` (or vice versa)."""
    aliases = {rel}
    prefix_ws = "docs/archive/windsurf/legacy-tree/plans/"
    prefix_cc = ".claude/plans/"
    if rel.startswith(prefix_ws):
        aliases.add(prefix_cc + rel[len(prefix_ws) :])
    elif rel.startswith(prefix_cc):
        aliases.add(prefix_ws + rel[len(prefix_cc) :])
    return aliases


def _plan_is_grandfathered(baseline: set[str], rel: str) -> bool:
    """True when ``rel`` is covered by a baseline entry (including archived relocations)."""
    if baseline.intersection(_grandfather_path_aliases(rel)):
        return True
    name = Path(rel).name
    existing = _plan_relpaths_on_disk(include_archive=True)
    for entry in baseline:
        if Path(entry).name == name and _baseline_entry_resolves(entry, existing):
            return True
    return False


def _validate_baseline_integrity(baseline: set[str]) -> list[str]:
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
                issues.append("baseline_schema_invalid — grandfathered_plans is not a list")
            else:
                seen: set[str] = set()
                for entry in listed:
                    if entry in seen:
                        issues.append(f"baseline_duplicate_entry — {entry!r} listed twice")
                    seen.add(entry)
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(f"baseline_parse_error — {type(exc).__name__}: {exc}")

    # Orphan detection — baseline entry must exist (top-level, alias, or archived relocation).
    existing_rel = _plan_relpaths_on_disk(include_archive=True)
    for entry in sorted(baseline):
        if not _baseline_entry_resolves(entry, existing_rel):
            issues.append(f"baseline_orphan_entry — {entry!r} is grandfathered but no such plan exists")

    return issues


def main() -> int:
    if not PLANS_DIR.is_dir():
        print(f"[check_graph_layer_evidence] plans dir missing: {PLANS_DIR}")
        return 0  # Not blocking on missing dir — no plans to check

    plans = sorted(
        p
        for p in PLANS_DIR.glob("*.md")
        if p.is_file() and p.name not in _ACTIVE_PLAN_EXCLUDE_NAMES
    )
    if not plans:
        print("[check_graph_layer_evidence] no plans found — OK")
        return 0

    baseline = _load_baseline()

    # Baseline integrity — orphaned and duplicate entries are silent bypasses.
    integrity_issues = _validate_baseline_integrity(baseline)
    if integrity_issues:
        print(f"\n[check_graph_layer_evidence] FAIL — {len(integrity_issues)} baseline integrity issue(s):")
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
        if _plan_is_grandfathered(baseline, rel):
            skipped_grandfathered += 1
            continue
        print(f"  [{idx}/{len(plans)}] evaluating {plan.relative_to(ROOT)}")
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
        print(f"\n[check_graph_layer_evidence] FAIL — {len(violations)} plan(s) missing graph-layer evidence")
        for v in violations:
            print(f"  - {v['plan']}")
            for m in v["missing"]:
                print(f"      * {m}")
        print(f"\nConstitutional rule §22 violated. See .claude/rules/adg-graph-layer-enforcement.md")
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
