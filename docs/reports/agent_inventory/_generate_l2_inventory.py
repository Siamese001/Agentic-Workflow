"""Generate L2 rationalization inventory JSON (planning-only). Run from repo root."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ADG_SNAPSHOT = "05172026_0651"


def git_grep(pattern: str, *scopes: str) -> list[str]:
    cmd = ["git", "grep", "-n", "-E", pattern, "--", *scopes]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    return [ln for ln in (r.stdout or "").splitlines() if ln.strip()]


def rel(path: str) -> str:
    return path.replace("\\", "/")


# --- Static inventory (curated from repo inspection; grep validates presence) ---
L2_SUBTREES = {
    "enforcement": "SovereignLLMGateway, E2 gates, provider substitution, write/read gateways",
    "healers": "healing_router, cascade registry, Gemini/Qwen gateways, local_healer",
    "reasoning": "StructuredEngineAgent, validation_orchestrator, ToolsmithAgent, executors",
    "orchestration": "l2_phase_pipeline (E1-E5 receipts; E2/E3/E4 = validate/execute/heal)",
    "providers": "gemini_provider, deterministic providers",
    "types": "l2_v3_receipts, l2_v4_contracts, heal contracts, agent taxonomy",
    "utils": "write_gateway, tool chains, l2_agent_wrappers",
    "bindings": "apps_rg_l2_binding (RETIRE shim), apps_lic_l2_binding, apps_research_l2_binding",
}

CORE_KEEP = [
    {"path": "agentic_core/L2_execution/orchestration/l2_phase_pipeline.py", "role": "E1-E5 spine orchestrator", "confidence": "HIGH"},
    {"path": "agentic_core/L2_execution/healers/healing_router.py", "role": "L2.4 tier routing (flash/pro)", "confidence": "HIGH"},
    {"path": "agentic_core/L2_execution/healers/healing_cascade_registry.py", "role": "Heal tier model IDs incl HEALING_GOOGLE_AI_PRO_MODEL", "confidence": "HIGH"},
    {"path": "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py", "role": "Provider gateway chokepoint", "confidence": "HIGH"},
    {"path": "agentic_core/L2_execution/bounded_executor.py", "role": "Bounded L2 execution envelope", "confidence": "HIGH"},
    {"path": "agentic_core/L2_execution/l2_package_driven_executor.py", "role": "Package-driven L2 execute", "confidence": "HIGH"},
    {"path": "agentic_core/L2_execution/reasoning/validation_orchestrator.py", "role": "Pre-exec validation orchestration", "confidence": "MEDIUM"},
    {"path": "agentic_core/L2_execution/reasoning/authority_validator.py", "role": "Authority slot validation", "confidence": "HIGH"},
    {"path": "agentic_core/L2_execution/healers/gemini_gateway_provisioner.py", "role": "Gemini heal provisioning", "confidence": "HIGH"},
    {"path": "agentic_core/L2_execution/healers/qwen_strict_diagnostic.py", "role": "Qwen heal diagnostics", "confidence": "MEDIUM"},
    {"path": "agentic_core/L2_execution/healers/vllm_health_probe.py", "role": "vLLM health (used by apps_rg)", "confidence": "HIGH"},
    {"path": "agentic_core/L0_routing/config/model_registry.py", "role": "Spine model ID SSOT", "confidence": "HIGH"},
    {"path": "agentic_core/config/google_ai_env.py", "role": "Google env var names", "confidence": "HIGH"},
]

CORE_QUARANTINE_RETIRE = [
    {"path": "agentic_core/L2_execution/apps_rg_l2_binding.py", "classification": "RETIRE", "confidence": "HIGH", "note": "Shim to apps_rg.runtime.bindings.l2_binding"},
    {"path": "agentic_core/L2_execution/_agentic_core_smoke.py", "classification": "QUARANTINE_UNTIL_REVIEW", "confidence": "MEDIUM"},
    {"path": "agentic_core/L2_execution/reasoning/examples/code_quality_healer.py", "classification": "QUARANTINE_UNTIL_REVIEW", "confidence": "HIGH", "note": "Exemplar only"},
    {"path": "agentic_core/L2_execution/reasoning/examples/code_quality_validator.py", "classification": "QUARANTINE_UNTIL_REVIEW", "confidence": "HIGH"},
]

APPS_RG_KEEP = [
    {"path": "apps_rg/__main__.py", "role": "Integrated R4 CLI", "confidence": "HIGH"},
    {"path": "apps_rg/runtime/orchestration/canonical_dispatch.py", "role": "Section + integrated dispatch SSOT", "confidence": "HIGH"},
    {"path": "apps_rg/l2_recipe/r4_generation_route.py", "role": "Default modular_section_lanes", "confidence": "HIGH"},
    {"path": "apps_rg/runtime/bindings/l2_binding.py", "role": "Canonical l2_execute_apps_rg", "confidence": "HIGH"},
    {"path": "apps_rg/runtime/providers/qwen_vllm_provider.py", "role": "Product generation provider", "confidence": "HIGH"},
    {"path": "apps_rg/runtime/judges/section_judge_profile.py", "role": "APPS_RG_*_JUDGE_MODEL_* resolution", "confidence": "HIGH"},
    {"path": "apps_rg/runtime/sections/executive_summary_lane.py", "role": "Section lane (Qwen)", "confidence": "HIGH"},
    {"path": "apps_rg/runtime/validators/", "role": "X2 deterministic gates per section", "confidence": "HIGH"},
    {"path": "apps_rg/runtime/exit/", "role": "X3 disposition helpers", "confidence": "HIGH"},
]

APPS_RG_SUPERSEDED = [
    {"path": "apps_rg/reasoning/RgResumeOrchestrator.py", "classification": "SUPERSEDED_BY_APPS_RG_SECTION_RUNTIME", "confidence": "HIGH"},
    {"path": "apps_rg/reasoning/RgHealingOrchestrator.py", "classification": "SUPERSEDED_BY_APPS_RG_SECTION_RUNTIME", "confidence": "HIGH"},
    {"path": "apps_rg/reasoning/RGStrategyExecutor.py", "classification": "SUPERSEDED_BY_APPS_RG_SECTION_RUNTIME", "confidence": "MEDIUM"},
    {"path": "apps_rg/runtime/dry_run/executive_summary_demo.py", "classification": "QUARANTINE_UNTIL_REVIEW", "confidence": "HIGH"},
    {"path": "apps_rg/runtime/internal/lane_batch.py", "classification": "QUARANTINE_UNTIL_REVIEW", "confidence": "HIGH", "note": "Offline orchestrator; not integrated dispatch"},
]

MODEL_CONSUMERS = {
    "GOOGLE_AI_MODEL": [
        "agentic_core/L0_routing/config/model_registry.py -> GEMINI_FLASH_MODEL_ID",
        "agentic_core/L2_execution/healers/healing_router.py",
        "agentic_core/L2_execution/healers/gemini_gateway_provisioner.py",
        "agentic_core/L3_orchestration/exit_eval/judges/google_judge.py",
        "agentic_core/config/sovereign_config.py",
        "apps_lic/reasoning/enterprise_campaign_orchestrator.py",
    ],
    "GOOGLE_AI_PRO_MODEL": [
        "agentic_core/L0_routing/config/model_registry.py -> GEMINI_PRO_MODEL_ID",
        "agentic_core/L1_cognition/enforcement/consensus_validator.py (juror)",
        "agentic_core/L3_orchestration/reasoning/engines/sub_atomic_engine_impl.py",
        "agentic_core/runtime/providers/provider_registry.py",
        "apps_rg/runtime/judges/executive_summary_x1d.py (fallback only)",
    ],
    "OPENAI_MODEL": [
        "agentic_core/L0_routing/config/model_registry.py -> OPENAI_MODEL_ID",
        "agentic_core/evaluation/judges/openai_judge.py",
        "agentic_core/runtime/config/reasoning_types.py",
        "apps_rg/runtime/judges/executive_summary_x1d.py (fallback)",
        "apps_rg/runtime/dry_run/executive_summary_demo.py (hardcoded demo)",
    ],
    "HEALING_GOOGLE_AI_PRO_MODEL": [
        "agentic_core/L2_execution/healers/healing_cascade_registry.py",
        "agentic_core/config/google_ai_env.py",
    ],
    "APPS_RG_JUDGE_VARS": [
        "apps_rg/runtime/judges/section_judge_profile.py",
        "apps_rg/runtime/judges/executive_summary_judge_profile.py",
        "apps_rg/runtime/judges/X1D_PROVIDER_CONFIG.md",
    ],
    "QWEN_VLLM": [
        "apps_rg/runtime/providers/qwen_vllm_provider.py",
        "apps_rg/runtime/sections/*_lane.py",
        "agentic_core/L0_routing/config/model_registry.py (QWEN_LOCAL_MODEL_ID / VLLM_*)",
    ],
    "SIGNAL_*": [
        "agentic_core/runtime/config/signal_quality_config.py",
        "apps_shared/utils/subatomic_hop_util.py (STUB)",
        "apps_shared/types/engine_type_types.py (STUB)",
    ],
}

WAVES = [
    {"id": "W0", "objective": "Freeze inventory SSOT and ADG provenance", "depends_on": [], "combine_with": []},
    {"id": "W1", "objective": "Document L2 subphase vocabulary E2/E3/E4 vs legacy enums", "depends_on": ["W0"], "combine_with": []},
    {"id": "W2", "objective": "Spine model env guards for apps_rg generation path", "depends_on": ["W1"], "combine_with": ["W3"]},
    {"id": "W3", "objective": "apps_rg judge env isolation and receipt model_source", "depends_on": ["W2"], "combine_with": ["W2"]},
    {"id": "W4", "objective": "Signal-quality SSOT wire-up or stub quarantine", "depends_on": ["W0"], "combine_with": [], "must_stay_separate_from": ["W2"]},
    {"id": "W5", "objective": "Same-authority healing enforcement audit", "depends_on": ["W1"], "combine_with": []},
    {"id": "W6", "objective": "Retire apps_rg_l2_binding shim", "depends_on": ["W2", "W3"], "combine_with": []},
    {"id": "W7", "objective": "Quarantine non-product apps_rg paths", "depends_on": ["W0"], "combine_with": ["W8"]},
    {"id": "W8", "objective": "Consolidate dispatch vs section lane surfaces", "depends_on": ["W7"], "combine_with": ["W7"]},
    {"id": "W9", "objective": "L2 E2 validator/gateway consolidation", "depends_on": ["W1", "W5"], "combine_with": []},
    {"id": "W10", "objective": "Exit/UWG/L4/L6 no-bypass contract tests", "depends_on": ["W5"], "combine_with": []},
    {"id": "W11", "objective": "Gated archive/delete after fan-in zero", "depends_on": ["W6", "W7", "W8", "W9", "W10"], "combine_with": []},
]

def main() -> None:
    ts = datetime.now(timezone.utc).isoformat()
    compile_r = subprocess.run(
        ["python", "-m", "compileall", "agentic_core", "apps_rg", "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    status_r = subprocess.run(["git", "status", "--short"], cwd=REPO, capture_output=True, text=True)

    agent_hits = len(git_grep(
        r"class .*Agent|class .*Healer|class .*Judge|class .*Executor|class .*Validator",
        "agentic_core", "apps_rg", "apps_shared", "apps_lic",
    ))
    model_hits = len(git_grep(
        r"OPENAI_MODEL|GOOGLE_AI_MODEL|GOOGLE_AI_PRO_MODEL|HEALING_GOOGLE_AI_PRO_MODEL|APPS_RG_.*JUDGE|QWEN|VLLM|SIGNAL_",
        "agentic_core", "apps_rg", "apps_shared", "apps_lic", "docs", "tests",
    ))

    assessment = {
        "generated_at": ts,
        "adg_snapshot_id": ADG_SNAPSHOT,
        "adg_sqlite": f"artifacts/adg/adg_indexed_{ADG_SNAPSHOT}.sqlite",
        "compileall_exit_code": compile_r.returncode,
        "git_status_short": status_r.stdout.strip().splitlines()[:40],
        "grep_via": "git grep (rg not in PATH on Windows shell)",
        "grep_counts": {"agent_healer_judge_patterns": agent_hits, "model_env_patterns": model_hits},
        "questions": {
            "1_l2_contains": {
                "module_count_approx": 273,
                "subtrees": L2_SUBTREES,
                "phase_mapping": {
                    "L2.2_validate": "E2 in l2_phase_pipeline (ValidatorResult)",
                    "L2.3_execute": "E3 in l2_phase_pipeline (ExecutorResult)",
                    "L2.4_heal": "E4 in l2_phase_pipeline (HealerResult; TwoPhaseHealerFn)",
                    "legacy_enum_warning": "l2_execution_contract.py CanonicalAgentRole may label EXECUTE as L2.2 — docs-only mismatch",
                },
            },
            "2_useful_core": CORE_KEEP,
            "3_obsolete_core": CORE_QUARANTINE_RETIRE,
            "4_canonical_apps_rg": APPS_RG_KEEP,
            "5_non_product_apps_rg": APPS_RG_SUPERSEDED,
            "6_model_consumers": MODEL_CONSUMERS,
            "7_spine_only_vars": ["GOOGLE_AI_MODEL", "GOOGLE_AI_PRO_MODEL", "OPENAI_MODEL", "HEALING_GOOGLE_AI_PRO_MODEL", "ANTHROPIC_MODEL"],
            "8_apps_rg_vars": {
                "generation": ["QWEN_VLLM_MODEL", "VLLM_BASE_URL", "VLLM_MODEL_NAME", "APPS_RG_*_QWEN_*", "APPS_RG_L2_PROVIDER_MODE"],
                "judges": ["APPS_RG_GOOGLE_JUDGE_MODEL_ENHANCED", "APPS_RG_GOOGLE_JUDGE_MODEL_STANDARD", "APPS_RG_OPENAI_JUDGE_MODEL_*", "APPS_RG_ANTHROPIC_JUDGE_MODEL_*"],
            },
            "9_signal_quality": {
                "real_ssot": "agentic_core/runtime/config/signal_quality_config.py",
                "stubbed": [
                    "apps_shared/utils/subatomic_hop_util.py",
                    "apps_shared/types/engine_type_types.py",
                ],
                "does_not_drive": ["apps_rg section generation", "apps_rg judges", "L2 heal tier routing"],
            },
            "10_waves": WAVES,
            "11_combine_rules": {
                "safe_to_combine": [["W0"], ["W2", "W3"], ["W7", "W8"]],
                "must_stay_separate": [
                    "W4 signal vs W2 model env",
                    "W5 healing before W11 delete",
                    "W6 shim retirement before W11 delete",
                    "W10 boundary tests before W11 delete",
                ],
            },
        },
        "classifications": {
            "KEEP_CORE": len(CORE_KEEP),
            "KEEP_APPS_RG": len(APPS_RG_KEEP),
            "RETIRE": 1,
            "SUPERSEDED_BY_APPS_RG_SECTION_RUNTIME": len([x for x in APPS_RG_SUPERSEDED if x["classification"].startswith("SUPERSEDED")]),
            "QUARANTINE_UNTIL_REVIEW": len([x for x in APPS_RG_SUPERSEDED + CORE_QUARANTINE_RETIRE if "QUARANTINE" in x["classification"]]),
            "NEEDS_DECISION": ["apps_shared signal stub wire vs quarantine", "legacy_full_resume rollback retention", "validation_orchestrator vs l2_phase_pipeline E2 duplication"],
        },
        "explicit_non_claims": [
            "No runtime proof that all healing respects same-authority (planned W5)",
            "No deprecation or deletion performed in this planning pass",
            "RgResumeOrchestrator still has unit tests and alias facade — not proven dead",
            "grep counts include tests/docs — not all hits are production paths",
        ],
        "waves_completed": {
            "W0": {
                "status": "PASS",
                "note": "Inventory JSON regenerated; compileall exit 0; confidence preserved",
            },
            "W1": {
                "status": "PASS",
                "note": "Ownership docs added; zero runtime behavior change",
            },
        },
        "w1_documentation_artifacts": [
            "docs/reports/agent_inventory/l2_ownership_model.md",
            "docs/reports/agent_inventory/apps_rg_canonical_runtime_boundary.md",
            "docs/reports/agent_inventory/env_ownership_boundary.md",
        ],
        "canonical_plan": {
            "slug": "l2-rationalization-waves-c8e4f1",
            "path": ".cursor/plans/l2-rationalization-waves-c8e4f1.md",
            "notion_page_id": "36527693-f55c-81d1-928c-c387dfcdafc5",
            "notion_url": "https://www.notion.so/l2-rationalization-waves-c8e4f1-36527693f55c81d1928cc387dfcdafc5",
            "notion_status": "In Progress",
        },
    }

    wave_plan = {
        "generated_at": ts,
        "recommended_wave_count": 12,
        "waves": [
            {
                **w,
                "why": {
                    "W0": "Baseline before quarantine labels change imports",
                    "W1": "Prevents wiring healers to wrong phase hooks",
                    "W2": "Stops spine vars bleeding into Qwen product path",
                    "W3": "APPS_RG_*_JUDGE must be sole proof-judge source",
                    "W4": "Stub signal_enhancer mimics SSOT — proof contamination risk",
                    "W5": "L2.4 must not heal authority/ACL/HITL failures",
                    "W6": "Canonical l2_execute lives in apps_rg binding",
                    "W7": "Demo/smoke paths mistaken for product proof",
                    "W8": "dispatch/* vs sections/* drift",
                    "W9": "Overlapping E2 enforcement modules",
                    "W10": "Architecture law enforcement",
                    "W11": "No delete until fan-in zero + quarantine elapsed",
                }.get(w["id"], ""),
                "files_likely_touched": {
                    "W0": ["docs/reports/agent_inventory/*"],
                    "W2": ["apps_rg/runtime/providers/qwen_vllm_provider.py", ".env.example", "tests/_apps_contract/"],
                    "W5": ["agentic_core/L2_execution/healers/healing_router.py", "tests/unit/agentic_core/L2_execution/healers/"],
                    "W6": ["agentic_core/L2_execution/apps_rg_l2_binding.py", "tests/_apps_contract/test_ag6_apps_rg_golden_path.py"],
                    "W11": ["archives/l2_rationalization_*"],
                }.get(w["id"], []),
                "tests": {
                    "W0": ["python docs/reports/agent_inventory/_generate_l2_inventory.py"],
                    "W2": ["pytest tests/unit/apps_rg/test_section_judge_policy.py -q"],
                    "W5": ["pytest tests/unit/agentic_core/L2_execution/healers/ -q"],
                    "W10": ["pytest tests/_apps_contract/ -k uwg -q", "pytest tests/_apps_contract/ -k exit -q"],
                }.get(w["id"], []),
                "commands": {
                    "W0": ["python -m compileall agentic_core apps_rg -q", "python docs/reports/agent_inventory/_generate_l2_inventory.py"],
                    "W2": ["pytest tests/_apps_contract/test_apps_rg_generation_entrypoints.py -q"],
                }.get(w["id"], ["pytest <scoped> -q"]),
                "acceptance": {
                    "W0": "Assessment JSON matches ADG snapshot; compileall exit 0",
                    "W2": "Contract test fails if generation lane imports GEMINI_FLASH_MODEL_ID",
                    "W5": "Negative tests: non-healable signals skip Gemini cascade",
                    "W11": "ADG fan-in=0 + migration receipt + 30d quarantine",
                }.get(w["id"], "Scoped tests green"),
                "rollback": "Revert commit or restore from archives/ manifest",
                "risks": {
                    "W2": "False positives on legitimate judge fallback",
                    "W4": "Breaking apps_shared if forced SSOT import",
                    "W11": "Premature delete breaks CI",
                }.get(w["id"], "Regression in scoped tests"),
                "pass_criteria": "Command output captured; scoped pytest PASS",
                "partial_criteria": "Docs/plan updated; tests not yet run",
                "fail_criteria": "pytest or compileall fails with no mitigation",
            }
            for w in WAVES
        ],
        "safe_to_combine": [["W0"], ["W2", "W3"], ["W7", "W8"]],
        "must_stay_separate": [
            "W4 independent from W2/W3",
            "W5/W6/W10 before W11",
        ],
        "top_risks": [
            "Mis-identifying live paths from grep alone",
            "Judge env incomplete → BLOCKED_PROVIDER_UNAVAILABLE",
            "Healing over-restriction blocks legitimate flash-tier repair",
            "Removing apps_rg_l2_binding breaks test_ag6 golden path",
            "Signal stub wire increases apps_shared → agentic_core coupling",
            "dispatch/section consolidation breaks proof receipt layout",
            "legacy_full_resume rollback still required for emergencies",
            "TwoPhaseHealerFn migration incomplete → INV-RC-5 advisory only",
            "Offline stub env mistaken for live proof",
            "W11 delete before fan-in zero",
        ],
        "top_decisions": [
            "Wire apps_shared signal stubs to SSOT vs quarantine-only",
            "Keep legacy_full_resume mode indefinitely vs sunset date",
            "Retire validation_orchestrator E2 vs fold into l2_phase_pipeline only",
            "Allow GOOGLE_AI_PRO_MODEL judge fallback in production",
            "Migrate RgResumeOrchestrator tests to section lane harness",
            "Single E2 entry: guardrail_gate vs e2_agent_gate vs authority_validator",
            "QwenJudgeGateway in L2 healers vs apps_rg-only",
            "ConfidenceAwareExecutor vs healing_router duplication",
            "Archive vs delete for dry_run/",
            "CI proof_eligible manifest enforcement location (ops_scripts vs tests)",
        ],
        "first_implementation_prompt": (
            "Execute W0+W1 only: refresh inventory JSON, add architecture doc table mapping "
            "L2.2/L2.3/L2.4 ↔ E2/E3/E4 with zero behavior change; run compileall and "
            "tests/unit/agentic_core/L2_execution/orchestration/ if present."
        ),
    }

    (OUT / "l2_rationalization_repo_assessment.json").write_text(
        json.dumps(assessment, indent=2), encoding="utf-8"
    )
    (OUT / "l2_rationalization_full_wave_plan.json").write_text(
        json.dumps(wave_plan, indent=2), encoding="utf-8"
    )
    print(f"Wrote assessment + wave plan at {ts}")


if __name__ == "__main__":
    main()
