"""One-off: build Dec 2025 apps_rg agent inventory artifacts (read-only)."""
from __future__ import annotations

import json
import re
from pathlib import Path

HIST = Path(r"c:/Git/apps_rg_dec2025_review")
CURR = Path(r"c:/Git/Agentic-Workflow-FRESH")
OUT = CURR / "docs/reports/agent_inventory"

ARCHETYPE_RULES: list[tuple[str, str]] = [
    (r"resumeagent", "SECTION_GENERATOR_AGENT"),
    (r"planner|rgplanner|strategicplanner", "PLANNER_AGENT"),
    (
        r"contentquality|factcheck|brandcompliance|sectionbalance|atscompat|testpilot|validationagent",
        "VALIDATOR_AGENT",
    ),
    (r"judge|evaluat|critic|reflection", "JUDGE_OR_EVALUATOR_AGENT"),
    (r"healing|healer|signalrouter|agentfactory|conversationalrepair|resilientmutator", "HEALER_OR_RECOVERY_AGENT"),
    (r"orchestrat|unifiedorchestrator|phase\d+orchestrator|resumeorchestrator", "RESUME_ORCHESTRATOR_AGENT"),
    (r"resume_generator|execute_resume|generat", "SECTION_GENERATOR_AGENT"),
    (r"dispatch", "DISPATCH_OR_ROUTER_AGENT"),
    (r"mock|smoke|demo|test_resume_logic_mock|debug_resume", "DEMO_OR_SMOKE_AGENT"),
    (r"generativemodel|gemini|openai|anthropic|qwen|vllm|call_llm|resume_generator", "MODEL_PROVIDER_WRAPPER"),
]

RISK_RULES: list[tuple[str, str]] = [
    (r"orchestrat.*run|unifiedorchestrator|phase\d+orchestrator", "ROUTE_AUTHORITY_DRIFT"),
    (r"gemini|openai|anthropic|generativemodel", "PROVIDER_SUBSTITUTION_RISK"),
    (r"call_llm|_generate_with_gemini|resume_generator", "DIRECT_MODEL_BYPASS"),
    (r"healingorchestrator|conversationalrepair|agentfactory", "SAME_AUTHORITY_HEALING_VIOLATION"),
    (r"record_pass|record_fail|signals", "EXIT_X3_BYPASS"),
    (r"gitops|mutat|rollback", "UWG_L4_BYPASS"),
    (r"mock|test_resume_logic_mock|debug_resume|create_test_resume", "MOCK_AS_PRODUCT_PROOF"),
    (r"strategicplanner|reflectionagent|promptgovernor", "PROMPT_AUTHORITY_DRIFT"),
    (r"cycle_results|record_result", "EVIDENCE_AUTHORITY_DRIFT"),
]

CURRENT_MAP: dict[str, tuple[str, str]] = {
    "PLANNER_AGENT": (
        "apps_rg/l2_recipe/modular_resume_generation.py, domain_contract targeting",
        "REPLACED_BY_CANONICAL_RUNTIME",
    ),
    "SECTION_GENERATOR_AGENT": (
        "apps_rg/runtime/sections/*_lane.py + qwen_vllm_provider",
        "SUPERSEDED_BY_SECTION_LANE",
    ),
    "RESUME_ORCHESTRATOR_AGENT": (
        "apps_rg/runtime/orchestration/canonical_dispatch.py, python -m apps_rg",
        "REPLACED_BY_CANONICAL_RUNTIME",
    ),
    "HEALER_OR_RECOVERY_AGENT": (
        "apps_rg/runtime/sections/*_repair_policy.py, section_repair_ledger.py (E4)",
        "SUPERSEDED_BY_E2_E4",
    ),
    "VALIDATOR_AGENT": ("apps_rg/runtime/validators/*_x2.py", "SUPERSEDED_BY_X2_X3"),
    "JUDGE_OR_EVALUATOR_AGENT": (
        "apps_rg/runtime/judges/*, APPS_RG_*_JUDGE_MODEL_*",
        "SUPERSEDED_BY_X2_X3",
    ),
    "DISPATCH_OR_ROUTER_AGENT": (
        "apps_rg/runtime/orchestration/canonical_dispatch.py",
        "REPLACED_BY_CANONICAL_RUNTIME",
    ),
    "DEMO_OR_SMOKE_AGENT": (
        "tests/unit/apps_rg/, tests.helpers.offline_lane_orchestration",
        "KEEP_AS_TEST_FIXTURE",
    ),
    "MODEL_PROVIDER_WRAPPER": (
        "apps_rg/runtime/providers/qwen_vllm_provider.py",
        "REPLACED_BY_CANONICAL_RUNTIME",
    ),
    "UTILITY_SCRIPT": ("ops_scripts/apps_rg/, historical reference", "HISTORICAL_REFERENCE_ONLY"),
    "UNKNOWN": ("NEEDS_DECISION", "NEEDS_DECISION"),
}

PRIMARY: list[tuple[str, str, str]] = [
    ("apps_rg/engines/resume_engine/autonomous/resume_base.py", "ResumeAgent", "Base agent with Gemini call_llm"),
    ("apps_rg/engines/resume_engine/autonomous/agents.py", "ContentQualityAgent", "Content quality validator agent"),
    ("apps_rg/engines/resume_engine/autonomous/agents.py", "FactCheckAgent", "Profile fact-check agent"),
    ("apps_rg/engines/resume_engine/autonomous/agents.py", "BrandComplianceAgent", "Brand/tone compliance"),
    ("apps_rg/engines/resume_engine/autonomous/agents.py", "TemplateOptimizer", "Template selection agent"),
    ("apps_rg/engines/resume_engine/autonomous/agents.py", "SectionBalanceAgent", "Section balance validator"),
    ("apps_rg/engines/resume_engine/autonomous/agents.py", "ATSCompatibilityAgent", "ATS formatting validator"),
    ("apps_rg/engines/resume_engine/autonomous/agents.py", "TestPilot", "Validation test runner agent"),
    ("apps_rg/engines/resume_engine/autonomous/agents.py", "StrategicPlanner", "Execution strategy planner agent"),
    ("apps_rg/engines/resume_engine/autonomous/agents.py", "ReflectionAgent", "Post-run reflection/learning agent"),
    ("apps_rg/engines/resume_engine/autonomous/healing.py", "HealingOrchestrator", "Multi-cycle self-healing coordinator"),
    ("apps_rg/engines/resume_engine/autonomous/healing.py", "SignalRouter", "Maps signals to agent sets"),
    ("apps_rg/engines/resume_engine/autonomous/healing.py", "AgentFactory", "Instantiates healing agents"),
    ("apps_rg/engines/resume_engine/autonomous/intelligence.py", "UnifiedOrchestrator", "Phase-6 intelligence orchestrator"),
    ("apps_rg/engines/resume_engine/autonomous/intelligence.py", "Phase6Orchestrator", "Phase 6 wrapper orchestrator"),
    ("apps_rg/engines/resume_engine/autonomous/gitops.py", "GitOpsManager", "File mutation / gitops repair"),
    ("apps_rg/engines/resume_engine/autonomous/gitops.py", "ConversationalRepair", "LLM-driven conversational repair"),
    ("apps_rg/engines/resume_engine/autonomous/gitops.py", "Phase4Orchestrator", "GitOps phase orchestrator"),
    ("apps_rg/engines/resume_engine/autonomous/governance.py", "Phase7Orchestrator", "Governance phase orchestrator"),
    ("apps_rg/engines/resume_engine/autonomous/governance.py", "PredictiveBudgetManager", "Cost prediction / budget"),
    ("apps_rg/engines/resume_engine/autonomous/learning.py", "ResumeLearningAgent", "Learning loop agent"),
    ("apps_rg/engines/resume_engine/autonomous/proactive.py", "ProactiveAgent", "Proactive scheduling/handoff agent"),
    ("apps_rg/engines/resume_engine/autonomous/context.py", "ResumeEngineContext", "Shared mutable agent context"),
    ("apps_rg/engines/resume_engine/autonomous/context.py", "BudgetManager", "Token/cost budget for agents"),
    ("apps_rg/engines/resume_engine/resume_planner.py", "RGPlanner", "K1-K8 resume pipeline planner (L1)"),
    ("apps_rg/engines/resume_engine/orchestrate_resume.py", "ResumeOrchestrator", "Hop-based resume workflow orchestrator"),
    ("apps_rg/engines/resume_engine/dispatch_resume_tools.py", "DispatchResumeTools", "Titanium RAG tool dispatcher"),
    ("apps_rg/engines/resume_engine/resume_generator.py", "ResumeGenerator", "Gemini resume synthesis"),
    ("apps_rg/engines/resume_engine/resume_engine.py", "resume_engine", "Main resume engine entry / Gemini config"),
    ("apps_rg/engines/resume_engine/execute_resume_generation.py", "execute_resume_generation", "Generation execution"),
    ("apps_rg/engines/resume_engine/test_resume_logic_mock.py", "test_resume_logic_mock", "Mock resume logic tests"),
    ("apps_rg/engines/resume_engine/debug_resume_test.py", "debug_resume_test", "Debug resume test harness"),
    ("apps_rg/engines/resume_engine/create_test_resume.py", "create_test_resume", "Test resume factory script"),
]


def detect_roles(text: str, path: str) -> list[str]:
    roles: list[str] = []
    if re.search(r"class\s+\w*Planner|rgplanner|strategicplanner", text, re.I):
        roles.append("plan")
    if re.search(r"orchestrat", text, re.I):
        roles.append("orchestrate")
    if re.search(r"class\s+\w*Agent|resumeagent", text, re.I):
        roles.append("agent_execute")
    if re.search(r"heal|repair|rollback|recovery", text, re.I):
        roles.append("heal")
    if re.search(r"validat|validator|gate", text, re.I):
        roles.append("validate")
    if re.search(r"judge|evaluat|critic|review", text, re.I):
        roles.append("judge")
    if re.search(r"dispatch|router|route", text, re.I):
        roles.append("route")
    if re.search(r"mock|smoke|demo|dry_run|stub", text, re.I) or "test_" in path.lower():
        roles.append("test_mock")
    if re.search(r"generativemodel|openai|anthropic|gemini|qwen|vllm|call_llm", text, re.I):
        roles.append("model_call")
    return sorted(set(roles))


def archetype(name: str, path: str) -> str:
    blob = (name + " " + path).lower()
    for pat, arch in ARCHETYPE_RULES:
        if re.search(pat, blob, re.I):
            return arch
    if "test" in path.lower():
        return "UTILITY_SCRIPT"
    return "UNKNOWN"


def risks(name: str, path: str, text: str) -> list[str]:
    blob = (name + path + text).lower()
    out: list[str] = []
    for pat, risk in RISK_RULES:
        if re.search(pat, blob, re.I):
            out.append(risk)
    if not out and "test" in path.lower():
        out.append("LOW_RISK_TEST_UTILITY")
    return sorted(set(out))


def models_from_text(text: str) -> list[str]:
    found: list[str] = []
    if re.search(r"gemini|GEMINI|GenerativeModel", text):
        found.append("google_gemini")
    if re.search(r"openai", text, re.I):
        found.append("openai")
    if re.search(r"anthropic", text, re.I):
        found.append("anthropic")
    if re.search(r"qwen|vllm", text, re.I):
        found.append("qwen_vllm")
    return found


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    file_list = (OUT / "_hist_all_files.txt").read_text(encoding="utf-8").splitlines()

    inventory: list[dict] = []
    for path, symbol, desc in PRIMARY:
        p = HIST / path.replace("/", "\\")
        text = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
        roles = detect_roles(text, path)
        arch = archetype(symbol, path)
        model = models_from_text(text)
        ce, rec = CURRENT_MAP.get(arch, ("NEEDS_DECISION", "NEEDS_DECISION"))
        inventory.append(
            {
                "path": path,
                "symbol": symbol,
                "description": desc,
                "apparent_role": roles,
                "archetype": arch,
                "model_providers": model,
                "planned": "plan" in roles,
                "routed": "route" in roles,
                "executed": "agent_execute" in roles or "orchestrate" in roles,
                "healed": "heal" in roles,
                "judged": "judge" in roles,
                "validated": "validate" in roles,
                "domain_specific": path.startswith("apps_rg/"),
                "direct_model_calls": "model_call" in roles or bool(model),
                "fallback_retry_heal": "heal" in roles
                or bool(re.search(r"fallback|retry", text, re.I)),
                "receipts_or_proof": bool(re.search(r"receipt|proof|x2|x3|manifest", text, re.I)),
                "current_equivalent": ce,
                "recommendation": rec,
                "risks": risks(symbol, path, text),
            }
        )

    hist_source = {
        "commit_sha": "5b443166b24379ba09c843ed59474c0800e26f4e",
        "commit_date": "2025-12-31T21:52:33-05:00",
        "branch_tag": None,
        "selection_method": (
            "git log --before=2026-01-01T00:00:00 -1 (last commit in calendar Dec 2025). "
            "No Dec 2025 tags matched *2025*/*dec*/*apps_rg*. "
            "Read-only worktree: c:/Git/apps_rg_dec2025_review."
        ),
        "confidence": "HIGH",
        "apps_rg_py_file_count": len(list((HIST / "apps_rg").rglob("*.py"))),
        "apps_rg_all_file_count": len(file_list),
    }

    archetype_counts: dict[str, int] = {}
    for item in inventory:
        archetype_counts[item["archetype"]] = archetype_counts.get(item["archetype"], 0) + 1

    comparison = {
        "historical_source": hist_source,
        "dec2025_agent_count": len(inventory),
        "dec2025_archetype_counts": archetype_counts,
        "removed_entire_subtree": (
            "apps_rg/engines/resume_engine/autonomous/ — present Dec 2025, not current product runtime"
        ),
        "current_canonical_entry": "python -m apps_rg (__main__.py -> canonical_dispatch)",
        "current_section_lanes": [
            "apps_rg/runtime/sections/executive_summary_lane.py",
            "apps_rg/runtime/sections/headline_lane.py",
            "apps_rg/runtime/sections/unify_narrative_lane.py",
            "apps_rg/runtime/sections/competencies_lane_runtime.py",
        ],
        "legacy_surfaces_still_present": [
            "apps_rg/reasoning/Rg*.py (test/harness façades)",
            "apps_rg/engines/resume_orchestrator_engine.py",
        ],
        "mapping_summary": [
            {
                "old": "ResumeAgent swarm + HealingOrchestrator",
                "new": "Section lanes + E4 repair + X2 gates + Exit/X3",
                "status": "SUPERSEDED_BY_SECTION_LANE",
            },
            {
                "old": "RGPlanner K1-K8 pipeline plan",
                "new": "l2_recipe/modular_resume_generation + domain_contract",
                "status": "REPLACED_BY_CANONICAL_RUNTIME",
            },
            {
                "old": "Gemini GenerativeModel in ResumeAgent.call_llm",
                "new": "qwen_vllm_provider + APPS_RG judge pins",
                "status": "DO_NOT_RESTORE",
            },
            {
                "old": "DispatchResumeTools / Titanium RAG",
                "new": "C0 retrieval + apps_rg cache (r1b)",
                "status": "NEEDS_DECISION",
            },
            {
                "old": "test_resume_logic_mock.py",
                "new": "pytest harness (APPS_RG_TEST_HARNESS)",
                "status": "KEEP_AS_TEST_FIXTURE",
            },
        ],
        "top_risks": [
            "ROUTE_AUTHORITY_DRIFT",
            "DIRECT_MODEL_BYPASS",
            "SAME_AUTHORITY_HEALING_VIOLATION",
            "MOCK_AS_PRODUCT_PROOF",
            "PROVIDER_SUBSTITUTION_RISK",
            "EXIT_X3_BYPASS",
            "EVIDENCE_AUTHORITY_DRIFT",
        ],
        "needs_decision": [
            "Whether apps_rg/reasoning/Rg* classes remain or move to quarantine",
            "Historical Titanium dispatch_resume_tools vs current C0 retrieval",
        ],
    }

    (OUT / "dec2025_apps_rg_agent_inventory.json").write_text(
        json.dumps(
            {
                "historical_commit_source": hist_source,
                "inventory": inventory,
                "archetype_counts": archetype_counts,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (OUT / "dec2025_to_current_agent_comparison.json").write_text(
        json.dumps(comparison, indent=2), encoding="utf-8"
    )

    md_inv = _md_inventory(hist_source, inventory, archetype_counts)
    md_cmp = _md_comparison(hist_source, comparison)
    (OUT / "dec2025_apps_rg_agent_inventory.md").write_text(md_inv, encoding="utf-8")
    (OUT / "dec2025_to_current_agent_comparison.md").write_text(md_cmp, encoding="utf-8")

    print(f"inventory={len(inventory)} archetypes={archetype_counts}")


def _md_inventory(hist_source: dict, inventory: list[dict], archetype_counts: dict[str, int]) -> str:
    lines = [
        "# December 2025 apps_rg Agent Inventory",
        "",
        "## 1. HISTORICAL_COMMIT_SOURCE",
        "",
        f"- **commit_sha**: `{hist_source['commit_sha']}`",
        f"- **commit_date**: {hist_source['commit_date']}",
        f"- **branch/tag**: {hist_source['branch_tag'] or 'none'}",
        f"- **selection**: {hist_source['selection_method']}",
        f"- **confidence**: {hist_source['confidence']}",
        f"- **worktree**: `c:/Git/apps_rg_dec2025_review`",
        f"- **apps_rg files**: {hist_source['apps_rg_all_file_count']} total, "
        f"{hist_source['apps_rg_py_file_count']} Python",
        "",
        "## 2. DEC2025_AGENT_INVENTORY",
        "",
        f"**DEC2025_AGENT_COUNT**: {len(inventory)} primary symbols (autonomous swarm + engine surface)",
        "",
        "| Path | Symbol | Archetype | Models | Roles | Receipts | Current equivalent | Recommendation | Risks |",
        "|------|--------|-----------|--------|-------|----------|-------------------|----------------|-------|",
    ]
    for i in sorted(inventory, key=lambda x: (x["archetype"], x["path"])):
        lines.append(
            "| `{p}` | {s} | {a} | {m} | {r} | {rc} | {c} | {rec} | {rk} |".format(
                p=i["path"],
                s=i["symbol"],
                a=i["archetype"],
                m=",".join(i["model_providers"]) or "-",
                r=",".join(i["apparent_role"]) or "-",
                rc="yes" if i["receipts_or_proof"] else "no",
                c=i["current_equivalent"][:72],
                rec=i["recommendation"],
                rk=",".join(i["risks"][:4]) or "-",
            )
        )
    lines += ["", "## 3. OLD_AGENT_ARCHETYPE_MAP", ""]
    for a, c in sorted(archetype_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- **{a}**: {c}")
    lines += [
        "",
        "## 4. RISK_ASSESSMENT_AGAINST_CURRENT_SPINE",
        "",
        "See per-row `risks` in JSON. Dominant classes if old agents were reactivated:",
        "- **ROUTE_AUTHORITY_DRIFT** — `UnifiedOrchestrator`, `HealingOrchestrator`, `ResumeOrchestrator` route multi-hop flows without spine E1–E5 packets.",
        "- **DIRECT_MODEL_BYPASS** — `ResumeAgent.call_llm` / `resume_generator` call Gemini directly.",
        "- **SAME_AUTHORITY_HEALING_VIOLATION** — `HealingOrchestrator` re-runs validator agents cross-signal without bounded E4 scope.",
        "- **EXIT_X3_BYPASS** — agents record pass/fail on shared context, not Exit→single X3.",
        "- **MOCK_AS_PRODUCT_PROOF** — `test_resume_logic_mock`, `debug_resume_test`, `create_test_resume`.",
        "",
        "## 5–6. CURRENT_EQUIVALENT / KEEP_OR_ARCHIVE",
        "",
        "Encoded per inventory row (`current_equivalent`, `recommendation`). Default for autonomous subtree: "
        "**HISTORICAL_REFERENCE_ONLY** / **DO_NOT_RESTORE**.",
        "",
        "## 7. LESSONS_LEARNED",
        "",
        "December 2025 `apps_rg` experimented with a **ResumeAgent swarm**: shared `ResumeEngineContext`, "
        "signal-driven healing cycles, and embedded Gemini calls. That accelerated iteration but **merged plan, "
        "route, execute, heal, judge, and model access** inside the app without L2 packet boundaries, Exit, or UWG.",
        "",
        "The governed model delegates durable authority to the spine; product proof is `python -m apps_rg` + "
        "section lanes + X2/X3 + pinned judges — not autonomous orchestrators or mocks.",
        "",
        "## EXPLICIT_NON_CLAIMS",
        "",
        "- Historical grep/worktree inventory does not prove current runtime reachability.",
        "- Old mock/smoke/demo paths are not product proof.",
        "- No code was restored, deleted, or migrated in this review.",
        "",
    ]
    return "\n".join(lines)


def _md_comparison(hist_source: dict, comparison: dict) -> str:
    sha = hist_source["commit_sha"]
    lines = [
        "# December 2025 → Current apps_rg Agent Comparison",
        "",
        "## HISTORICAL_COMMIT_SOURCE",
        "",
        f"- **SHA**: `{sha}`",
        f"- **Date**: {hist_source['commit_date']}",
        f"- **Confidence**: **{hist_source['confidence']}**",
        "",
        "## Structural delta",
        "",
        "| Dimension | Dec 2025 | Current (May 2026 HEAD) |",
        "|-----------|----------|-------------------------|",
        "| Entry | `resume_engine` + `autonomous/` swarm | `python -m apps_rg` → `canonical_dispatch` |",
        "| Layout | `apps_rg/engines/resume_engine/` (~104 py) | `apps_rg/runtime/` section lanes (~560 files) |",
        "| Generation | Gemini via `ResumeAgent.call_llm` | `qwen_vllm_provider` + section lanes |",
        "| Validation | In-agent `record_pass` / signals | `validators/*_x2.py` deterministic gates |",
        "| Healing | `HealingOrchestrator` multi-cycle | E4 same-authority section repair policies |",
        "| Proof | Ad-hoc results on context | `runtime_proof_layout`, X1D/X2/X3 receipts |",
        "",
        "## Mapping table",
        "",
        "| Old behavior | Governed owner today | Status |",
        "|--------------|---------------------|--------|",
    ]
    for m in comparison["mapping_summary"]:
        lines.append(f"| {m['old']} | {m['new']} | {m['status']} |")
    lines += [
        "",
        "## TOP_10_OLD_AGENTS (material)",
        "",
        "1. `HealingOrchestrator` — autonomous multi-cycle heal",
        "2. `UnifiedOrchestrator` — Phase 6 intelligence routing",
        "3. `ResumeAgent` + specialized validators — swarm execution",
        "4. `RGPlanner` — K1–K8 pipeline planning",
        "5. `ResumeOrchestrator` — hop workflow",
        "6. `ConversationalRepair` — LLM gitops repair",
        "7. `ResumeGenerator` / Gemini — direct synthesis",
        "8. `DispatchResumeTools` — Titanium dispatch",
        "9. `StrategicPlanner` / `ReflectionAgent` — plan/learn in-agent",
        "10. `test_resume_logic_mock` — mock product path",
        "",
        "## TOP_10_CURRENT_REPLACEMENTS",
        "",
        "1. `apps_rg/__main__.py` — canonical CLI",
        "2. `runtime/orchestration/canonical_dispatch.py`",
        "3. `runtime/sections/*_lane.py` — modular section lanes",
        "4. `runtime/providers/qwen_vllm_provider.py`",
        "5. `runtime/validators/*_x2.py`",
        "6. `runtime/judges/*` + `APPS_RG_*_JUDGE_MODEL_*`",
        "7. `runtime/sections/*_repair_policy.py` — E4 repair",
        "8. `runtime/runtime_proof_layout.py`",
        "9. `l2_recipe/modular_resume_generation.py`",
        "10. `runtime/bindings/exit_binding.py` — Exit handoff",
        "",
        "## TOP_10_RISKS (if legacy reintroduced)",
        "",
    ]
    for r in comparison["top_risks"]:
        lines.append(f"- {r}")
    lines += ["", "## NEEDS_DECISION", ""]
    for n in comparison["needs_decision"]:
        lines.append(f"- {n}")
    lines += [
        "",
        "## LESSONS_LEARNED",
        "",
        "The old model optimized for **agent autonomy and fast local iteration**. The governed model optimizes for "
        "**bounded execution, single Exit disposition, and pinned providers**. Keep Dec 2025 artifacts as "
        "historical reference only; do not treat mocks or orchestrators as product proof.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
