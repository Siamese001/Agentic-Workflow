"""Phase 1: Classify all agents into structural archetypes.

Produces:
- artifacts/consolidation/agent_archetype_map.json
- docs/reports/plans/agent_archetype_map.md
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INV_PATH = PROJECT_ROOT / "artifacts" / "consolidation" / "agent_inventory.json"
JSON_OUT = PROJECT_ROOT / "artifacts" / "consolidation" / "agent_archetype_map.json"
MD_OUT = PROJECT_ROOT / "docs" / "reports" / "plans" / "agent_archetype_map.md"


def classify(agent: dict) -> str:
    """Classify an agent into a structural archetype."""
    cn = agent.get("class_name", "")
    bases = set(agent.get("all_bases", []))
    methods = set(agent.get("methods", []))
    domain_methods = set(agent.get("domain_methods", []))
    entrypoints = set(agent.get("entrypoints", []))
    mixins = set(agent.get("capability_mixins", []))
    domain_loc = agent.get("domain_logic_loc", 0)
    bp_ratio = agent.get("boilerplate_ratio", 0)
    layer = agent.get("layer", "")

    # InspectionAgent: uses InspectionCapability
    if "InspectionCapability" in mixins or "perform_checks" in methods or "run_inspection" in methods:
        return "InspectionAgent"

    # StageAgent: uses HOPStageCapability (pipeline stages)
    if "HOPStageCapability" in mixins or "_process" in entrypoints:
        return "StageAgent"

    # ValidationAgent: uses RGValidationCapability or LICEngineValidationCapability or collect_issues
    if "RGValidationCapability" in mixins or "LICEngineValidationCapability" in mixins:
        return "ValidationAgent"
    if "collect_issues" in entrypoints:
        return "ValidationAgent"
    if "_validate" in entrypoints:
        return "ValidationAgent"

    # ToolRunnerAgent: uses CodeToolRunnerCapability
    if "CodeToolRunnerCapability" in mixins:
        return "ToolRunnerAgent"

    # PolicyGateAgent: guardrails, gates, compliance
    gate_keywords = {"guardrail", "guard", "gate", "compliance", "shield", "safety", "seal"}
    if any(kw in cn.lower() for kw in gate_keywords):
        return "PolicyGateAgent"

    # OrchestratorAgent: orchestrators, supervisors, coordinators
    orch_keywords = {"orchestrat", "supervisor", "coordinat", "dispatch"}
    if any(kw in cn.lower() for kw in orch_keywords):
        return "OrchestratorAgent"

    # WrapperProxyAgent: near-zero domain logic, just delegates
    if domain_loc < 10 and bp_ratio > 0.5:
        return "WrapperProxyAgent"

    # ReasoningAgent: has significant domain logic
    if domain_loc >= 50 and entrypoints:
        return "ReasoningAgent"

    # Observability: L6 layer
    if layer == "L6":
        return "ObservabilityAgent"

    # Agents with no domain logic at all
    if domain_loc == 0:
        return "WrapperProxyAgent"

    # Low domain agents without clear archetype
    if domain_loc < 15:
        return "WrapperProxyAgent"

    # Default: ReasoningAgent (has some domain logic)
    if domain_loc >= 15:
        return "ReasoningAgent"

    return "Other"


def main():
    inv = json.loads(INV_PATH.read_text(encoding="utf-8"))
    agents = inv["agents"]

    archetype_map: dict[str, list[dict]] = {}
    agent_archetypes: list[dict] = []

    for a in agents:
        archetype = classify(a)
        entry = {
            "class_name": a["class_name"],
            "archetype": archetype,
            "layer": a.get("layer", ""),
            "domain_logic_loc": a.get("domain_logic_loc", 0),
            "total_loc": a.get("total_loc", 0),
            "boilerplate_ratio": a.get("boilerplate_ratio", 0),
            "all_bases": a.get("all_bases", []),
            "capability_mixins": a.get("capability_mixins", []),
            "entrypoints": a.get("entrypoints", []),
            "file_path": a.get("file_path", ""),
        }
        archetype_map.setdefault(archetype, []).append(entry)
        agent_archetypes.append(entry)

    # Check forced consolidation targets (≥5 agents + structure sim ≥0.75)
    forced_targets = []
    for arch, members in sorted(archetype_map.items(), key=lambda x: -len(x[1])):
        if len(members) >= 5:
            # Compute structural similarity within archetype
            base_sigs = ["+".join(sorted(m["all_bases"])) for m in members]
            most_common_sig = Counter(base_sigs).most_common(1)[0]
            sig_ratio = most_common_sig[1] / len(members)
            if sig_ratio >= 0.5:  # ≥50% share same base signature → high structural sim
                forced_targets.append(
                    {
                        "archetype": arch,
                        "count": len(members),
                        "dominant_base_sig": most_common_sig[0],
                        "sig_ratio": round(sig_ratio, 2),
                        "forced": True,
                    },
                )

    result = {
        "total_agents": len(agents),
        "archetype_counts": {k: len(v) for k, v in sorted(archetype_map.items(), key=lambda x: -len(x[1]))},
        "forced_consolidation_targets": forced_targets,
        "archetypes": {k: v for k, v in sorted(archetype_map.items(), key=lambda x: -len(x[1]))},
    }

    JSON_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    # Generate markdown
    lines = ["# Agent Archetype Classification Map", "", f"**Total agents**: {len(agents)}", ""]

    lines.append("## Archetype Distribution")
    lines.append("")
    lines.append("| Archetype | Count | Forced Consolidation |")
    lines.append("|-----------|-------|---------------------|")
    for arch, members in sorted(archetype_map.items(), key=lambda x: -len(x[1])):
        forced = "YES" if any(f["archetype"] == arch for f in forced_targets) else "no"
        lines.append(f"| {arch} | {len(members)} | {forced} |")

    lines.append("")
    lines.append("## Forced Consolidation Targets")
    lines.append("")
    for ft in forced_targets:
        lines.append(f"### {ft['archetype']} ({ft['count']} agents)")
        lines.append(f"- Dominant base signature: `{ft['dominant_base_sig']}`")
        lines.append(f"- Signature ratio: {ft['sig_ratio']}")
        lines.append("- **FORCED**: No waivers allowed")
        lines.append("")
        members = archetype_map[ft["archetype"]]
        lines.append("| Agent | Layer | Domain LOC | BP Ratio | Bases |")
        lines.append("|-------|-------|-----------|----------|-------|")
        for m in sorted(members, key=lambda x: x["domain_logic_loc"]):
            lines.append(
                f"| {m['class_name']} | {m['layer']} | {m['domain_logic_loc']} | {m['boilerplate_ratio']:.2f} | {'+'.join(m['all_bases'])} |",
            )
        lines.append("")

    lines.append("## All Archetypes Detail")
    lines.append("")
    for arch, members in sorted(archetype_map.items(), key=lambda x: -len(x[1])):
        if any(f["archetype"] == arch for f in forced_targets):
            continue  # already shown above
        lines.append(f"### {arch} ({len(members)} agents)")
        lines.append("")
        lines.append("| Agent | Layer | Domain LOC | BP Ratio |")
        lines.append("|-------|-------|-----------|----------|")
        for m in sorted(members, key=lambda x: x["domain_logic_loc"]):
            lines.append(
                f"| {m['class_name']} | {m['layer']} | {m['domain_logic_loc']} | {m['boilerplate_ratio']:.2f} |",
            )
        lines.append("")

    MD_OUT.write_text("\n".join(lines), encoding="utf-8")

    # Print summary
    print("Archetype counts:")
    for k, v in sorted(result["archetype_counts"].items(), key=lambda x: -x[1]):
        print(f"  {k:25s} {v}")
    print(f"\nForced consolidation targets: {len(forced_targets)}")
    for ft in forced_targets:
        print(f"  {ft['archetype']:25s} {ft['count']} agents (sig_ratio={ft['sig_ratio']})")


if __name__ == "__main__":
    main()
