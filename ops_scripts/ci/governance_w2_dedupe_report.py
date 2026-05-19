#!/usr/bin/env python3
"""Emit W2 governance dedupe report JSON + markdown (cursor-governance-two-tier-b4e8f2)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT_JSON = REPO / "docs/reports/cursor/governance_w2_dedupe_report.json"
REPORT_MD = REPO / "docs/reports/cursor/governance_w2_dedupe_report.md"


def _bytes(path: Path) -> int:
    return path.stat().st_size if path.exists() else 0


def main() -> int:
    clusters = {
        "author_gate": {
            "tier_1": ".cursor/rules/003-cursor-author-gate-hitl.mdc",
            "on_demand_rules": [
                ".cursor/rules/author-gate-enforcement.mdc",
                ".cursor/rules/author-gate-decision-points.mdc",
                ".cursor/rules/anti-pattern-author-gate.mdc",
                ".cursor/rules/author-gate-svp-calibration.mdc",
            ],
            "skills": [
                ".cursor/skills/author-gate-packet-builder/SKILL.md",
                ".cursor/skills/author-gate-ui-renderer/SKILL.md",
                ".cursor/skills/refactor-decision-memory/SKILL.md",
            ],
            "workflows_thinned": [
                ".cursor/workflows/author-gate-decision-gate.md",
                ".cursor/workflows/antipattern-author-gate.md",
                ".cursor/workflows/author-gate-calibration-report.md",
            ],
            "removed_duplicate_locations": [
                "author-gate-enforcement.mdc: pipeline steps 1-9 (now points to 003)",
                "workflows/author-gate-decision-gate.md: full procedural body",
                "workflows/antipattern-author-gate.md: scanner walkthrough body",
            ],
            "no_loss_assertion": "Tier-1 003 unchanged; emitter, anti-pattern, calibration, and hook references preserved in author-gate-enforcement.mdc",
        },
        "adg": {
            "on_demand_rules": [
                ".cursor/rules/adg-analysis-procedures.mdc",
                ".cursor/rules/adg-canonical-invariants.mdc",
                ".cursor/rules/adg-p-band-burn-down-discipline.mdc",
            ],
            "skills": [
                ".cursor/skills/adg-sqlite/SKILL.md",
                ".cursor/skills/graph-analysis/SKILL.md",
            ],
            "workflows_thinned": [
                ".cursor/workflows/adg-repair-loop.md",
                ".cursor/workflows/adg-test-triage-gate.md",
            ],
            "removed_duplicate_locations": [
                "workflows/adg-repair-loop.md: step-by-step repair body",
                "workflows/adg-test-triage-gate.md: selector walkthrough body",
            ],
            "no_loss_assertion": "Full repair/hotspot procedures remain in adg-analysis-procedures.mdc; invariants in adg-canonical-invariants.mdc",
        },
        "structured_reasoning": {
            "on_demand_rules": [".cursor/rules/sequential-thinking-enforcement.mdc"],
            "skills": [".cursor/skills/structured-reasoning/SKILL.md"],
            "workflows_thinned": [".cursor/workflows/structured-reasoning.md"],
            "removed_duplicate_locations": [
                "workflows/structured-reasoning.md: SR_INTAKE through SR_SUMMARY phase bodies",
            ],
            "no_loss_assertion": "SR packet shape and hard limits preserved in rule + skill templates",
        },
        "tavily": {
            "skills": [
                ".cursor/skills/tavily-research/SKILL.md",
                ".cursor/skills/mcp-integration/SKILL.md",
            ],
            "workflows_thinned": [
                ".cursor/workflows/tavily-search.md",
                ".cursor/workflows/tavily-extract.md",
                ".cursor/workflows/tavily-map.md",
                ".cursor/workflows/tavily-crawl.md",
                ".cursor/workflows/tavily-research.md",
                ".cursor/workflows/tavily-best-practices.md",
            ],
            "removed_duplicate_locations": [
                "All six tavily workflow files: duplicated tool params and hard rules",
            ],
            "no_loss_assertion": "Routing table and §25 sole-MCP discipline remain in mcp-integration §8 and tavily-research skill",
        },
        "notion_plan": {
            "on_demand_rules": [
                ".cursor/rules/plan-location.mdc",
                ".cursor/rules/plan-update-enforcement.mdc",
                ".cursor/rules/plan-lifecycle-procedures.mdc",
            ],
            "skills": [".cursor/skills/plan-governance/SKILL.md"],
            "workflows_thinned": [],
            "removed_duplicate_locations": [
                "plan-lifecycle-procedures.mdc: full procedural body (moved to plan-governance skill)",
            ],
            "no_loss_assertion": "Path/format/authorization invariants remain in plan-location and plan-update-enforcement rules",
        },
    }

    triples_before = 8  # AG + SR + 6 Tavily workflow/skill pairs (pre-W2 inventory)
    triples_after = 0  # workflows are aliases only

    intentional = [
        {
            "location": "003 + author-gate-enforcement",
            "reason": "Tier-1 pipeline vs on-demand emitter/anti-pattern/calibration extensions (non-overlapping after W2 trim)",
        },
        {
            "location": "adg-canonical-invariants + adg-analysis-procedures",
            "reason": "Invariant vs procedural split by design",
        },
        {
            "location": "plan-location + plan-governance skill",
            "reason": "Invariant path/format vs procedural lifecycle",
        },
        {
            "location": "mcp-integration §8 + tavily-research skill stub",
            "reason": "Redirect stub until W4 skill split; routing table authoritative in mcp-integration",
        },
    ]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "plan_id": "cursor-governance-two-tier-b4e8f2",
        "wave": "W2",
        "policy_option": "A",
        "cluster_inventory": clusters,
        "duplication": {
            "duplicate_triples_before": triples_before,
            "duplicate_triples_after": triples_after,
            "intentional_duplicates_remaining": intentional,
        },
        "tier_1_bytes": None,
        "always_apply_count": 4,
        "risk_notes": [
            "Agents must load plan-governance skill for lifecycle work — rule file is now a pointer",
            "Tavily workflows no longer embed params — agents must follow mcp-integration §8",
        ],
        "explicit_non_claims": [
            "W3-W5 not executed",
            "hooks not rewired",
            "active plans not archived",
            ".windsurf not deleted",
            "runtime RAG not touched",
            "agentic_core untouched",
            "apps_rg runtime/product code untouched",
            "full consolidation not complete",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Governance W2 dedupe report",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        "",
        f"- Duplicate triples before: **{triples_before}**",
        f"- Duplicate triples after: **{triples_after}**",
        f"- AlwaysApply count: **4** (Option A)",
        "",
        "## Clusters",
        "",
    ]
    for name, data in clusters.items():
        md_lines.append(f"### {name}")
        md_lines.append(f"- No-loss: {data['no_loss_assertion']}")
        md_lines.append("- Removed duplicates:")
        for loc in data["removed_duplicate_locations"]:
            md_lines.append(f"  - {loc}")
        md_lines.append("")

    md_lines.append("## Intentional duplication remaining")
    for item in intentional:
        md_lines.append(f"- **{item['location']}**: {item['reason']}")

    REPORT_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"[w2-dedupe] wrote {REPORT_JSON}")
    print(f"[w2-dedupe] wrote {REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
