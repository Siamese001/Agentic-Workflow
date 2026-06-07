"""Validate the 18 reclassification candidates against codebase + filesystem.

For each Retired row claimed as DELIVERED or MIXED, check:
  1. If summary names a CI gate (check_*.py) -> does it exist on disk?
  2. If summary names a successor plan -> does docs/archive/windsurf/legacy-tree/plans/<successor>*.md exist?
  3. If summary says "decomposed into children" -> do child plan files exist?
  4. Predecessor plan file: open it and look for COMPLETED/SHIPPED markers.

Outputs artifacts/notion/retired_validation.json with per-row verdict:
  CONFIRMED_DELIVERED  - codebase evidence supports flip to Completed
  WEAK_EVIDENCE        - some signal but not conclusive
  CANT_VERIFY          - successor named but couldn't locate
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
CI_DIR = REPO / "ops_scripts" / "ci"

DUMP = Path("C:/Users/amita/AppData/Local/Temp/windsurf/mcp_output_4570bbeb1534c8d5.txt")

# 18 candidates from _audit_retired_vs_completed.py output (slugs only;
# page_ids resolved from dump).
CANDIDATES: list[str] = [
    # DELIVERED (9 unique — duplicate adg-ci-gate-hardening-deferred-b4e3c9
    # already archived; surviving row stays in this list)
    "d-bucket-burndown-e4f2c9",
    "adg-ci-gate-hardening-deferred-b4e3c9",
    "adg-ci-spine-delegation-gate-438b16",
    "three-bucket-otel-view-5db409",
    "three-bucket-gap-remediation-069806",
    "adg-three-bucket-authority-model-7e2a91",
    "query-progress-bar-backlog",
    "prompt-reception-followups-a7b3c4",
    "llm-judge-hardening-followups-f2c8e1",
    # MIXED (8)
    "test-coverage-backlog-f8f5a7",
    "terminal-cleanup-burndown-a7f2d1",
    "p2-burndown-wave-9e4c17",
    "p2-antipattern-burndown-ae0549",
    "p1-antipattern-burndown-8a3f2b",
    "l0-prompt-retrieval-deferred-triage-d3e8f1",
    "cache-r1ab-residuals-8c4e2a",
    "anthropic-alignment-followups",
]

_GATE_RE = re.compile(r"\b(check_[a-z0-9_]+\.py)\b")
_PLAN_REF_RE = re.compile(r"\b([a-z][a-z0-9-]+-[0-9a-f]{6})\b")
_DECOMP_RE = re.compile(r"decomposed into (\d+)", re.I)


def _find_predecessor_plan(slug: str) -> Path | None:
    matches = list(PLANS_DIR.glob(f"{slug}*.md"))
    return matches[0] if matches else None


def _find_successor_plan(name: str) -> Path | None:
    matches = list(PLANS_DIR.glob(f"{name}*.md"))
    return matches[0] if matches else None


def _ci_gate_exists(name: str) -> bool:
    return (CI_DIR / name).exists()


def validate(slug: str, page_id: str, summary: str, exists_on_disk: bool) -> dict:
    evidence: list[str] = []
    issues: list[str] = []

    # 1) Predecessor plan file
    pred = _find_predecessor_plan(slug)
    if pred:
        try:
            head = pred.read_text(encoding="utf-8", errors="replace")[:3000]
            if re.search(r"\b(COMPLETED|SHIPPED|DELIVERED)\b", head):
                evidence.append(f"plan-file: COMPLETED/SHIPPED/DELIVERED in head ({pred.name})")
            elif re.search(r"\bRetired\b", head):
                issues.append(f"plan-file: marked Retired in head ({pred.name})")
            else:
                evidence.append(f"plan-file present ({pred.name})")
        except OSError as exc:
            issues.append(f"plan-file unreadable: {exc}")
    else:
        if exists_on_disk:
            issues.append(f"Notion says Exists On Disk=true but no .md file matches '{slug}*'")
        else:
            issues.append("plan-file missing from disk (matches Notion exists=False)")

    # 2) CI gates named in summary
    for gate in set(_GATE_RE.findall(summary)):
        ok = _ci_gate_exists(gate)
        if ok:
            evidence.append(f"ci-gate exists: {gate}")
        else:
            issues.append(f"ci-gate NOT FOUND: {gate}")

    # 3) Successor plans named in summary
    referenced = set(_PLAN_REF_RE.findall(summary)) - {slug}
    for ref in referenced:
        succ = _find_successor_plan(ref)
        if succ:
            try:
                head = succ.read_text(encoding="utf-8", errors="replace")[:2000]
                status_match = re.search(r"\*\*Status\*\*:\s*([A-Za-z]+)", head)
                status = status_match.group(1) if status_match else "?"
                evidence.append(f"successor exists: {succ.name} (Status={status})")
            except OSError:
                evidence.append(f"successor exists: {succ.name}")
        else:
            issues.append(f"successor NOT FOUND in plans/: {ref}")

    # 4) Decomposed-into-N children
    m = _DECOMP_RE.search(summary)
    if m:
        n = int(m.group(1))
        # Look for child plans referenced by name in summary
        refs = set(_PLAN_REF_RE.findall(summary)) - {slug}
        children_found = sum(1 for r in refs if _find_successor_plan(r))
        if children_found >= n:
            evidence.append(f"decompose: claimed {n} children, found {children_found}")
        else:
            issues.append(f"decompose: claimed {n} children, only {children_found} found")

    # Verdict
    has_strong = any("CI gate" in e or "ci-gate exists" in e or "COMPLETED/SHIPPED" in e
                     or "successor exists" in e for e in evidence)
    if has_strong and not any("NOT FOUND" in i for i in issues):
        verdict = "CONFIRMED_DELIVERED"
    elif evidence and len(evidence) > len(issues):
        verdict = "WEAK_EVIDENCE"
    else:
        verdict = "CANT_VERIFY"

    return {
        "slug": slug,
        "page_id": page_id,
        "verdict": verdict,
        "evidence": evidence,
        "issues": issues,
    }


def main() -> int:
    data = json.loads(DUMP.read_text(encoding="utf-8"))
    by_slug: dict[str, dict] = {}
    for r in data["results"]:
        title = r["properties"]["Slug"]["title"]
        slug = title[0]["plain_text"] if title else "(no-slug)"
        summary = "".join(c["plain_text"] for c in r["properties"]["Summary"]["rich_text"])
        exists = r["properties"]["Exists On Disk"]["checkbox"]
        by_slug[slug] = {"page_id": r["id"], "summary": summary, "exists": exists}

    results: list[dict] = []
    for slug in CANDIDATES:
        info = by_slug.get(slug)
        if not info:
            print(f"WARN: {slug} not found in dump")
            continue
        results.append(validate(slug, info["page_id"], info["summary"], info["exists"]))

    out = REPO / "artifacts" / "notion" / "retired_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    counts: dict[str, int] = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print(f"Validated {len(results)} candidates -> {out}")
    print()
    for v, n in counts.items():
        print(f"  {v}: {n}")
    print()
    for r in results:
        print(f"--- [{r['verdict']}] {r['slug']}")
        for e in r["evidence"]:
            print(f"    + {e}")
        for i in r["issues"]:
            print(f"    - {i}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
