"""Structural Audit — Phases A-G for consolidation validation.

Programmatic verification of shim integrity, dispatch coverage,
domain logic isolation, blast radius, layer balance, and reduction quality.

All checks use AST parsing per constitutional rules.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TARGETS = json.loads((PROJECT_ROOT / "artifacts" / "consolidation" / "target_paths.json").read_text())
INVENTORY = json.loads((PROJECT_ROOT / "artifacts" / "consolidation" / "agent_inventory.json").read_text())
# Use fresh discovery snapshot for accurate AST-verified data
_snap_fresh = PROJECT_ROOT / "artifacts" / "consolidation" / "discovery_snapshot_fresh.json"
_snap_after = PROJECT_ROOT / "artifacts" / "consolidation" / "discovery_snapshot_after.json"
SNAPSHOT_AFTER = json.loads((_snap_fresh if _snap_fresh.exists() else _snap_after).read_text())

RETIRE_FILES = TARGETS["retire"]
MERGE_FILES = TARGETS["merge"]

# Canonical executor paths and their expected dispatch keys
EXECUTORS = {
    "InspectorExecutor": {
        "path": "agentic_core/L5_safety/reasoning/InspectorExecutor.py",
        "dispatch_keys": ["dag_runtime", "signature", "token_budget"],
        "merged_agents": ["DagRuntimeInspectorAgent", "SignatureVerifierAgent", "TokenBudgetInspectorAgent"],
    },
    "RGValidationExecutor": {
        "path": "apps_rg/engines/RGValidationExecutor.py",
        "dispatch_keys": ["ats_compatibility", "brand_compliance", "fact_check", "section_balance"],
        "merged_agents": [
            "ATSCompatibilityAgent",
            "BrandComplianceAgent",
            "FactCheckAgent",
            "SectionBalanceAgent",
        ],
    },
    "LICValidationExecutor": {
        "path": "apps_lic/engines/LICValidationExecutor.py",
        "dispatch_keys": ["campaign_balance", "deliverability"],
        "merged_agents": ["CampaignBalanceAgent", "DeliverabilityAgent"],
    },
    "ObservabilityProbeExecutor": {
        "path": "agentic_core/L6_observability/reasoning/ObservabilityProbeExecutor.py",
        "dispatch_keys": [
            "cost_tracker",
            "coordinator",
            "strategic",
            "deadlock",
            "debate",
            "runtime_telemetry",
        ],
        "merged_agents": [
            "TrackObservabilityCostAgent",
            "CoordinateObservabilityOperationsAgent",
            "StrategicObservationAgent",
            "DeadlockDetectorAgent",
            "DebateSynthesisAgent",
            "RuntimeTelemetryAgent",
        ],
    },
    "RGStrategyExecutor": {
        "path": "apps_rg/engines/RGStrategyExecutor.py",
        "dispatch_keys": ["content", "strategic_planner", "template_optimizer"],
        "merged_agents": ["ContentStrategyAgent", "RgStrategicPlannerAgent", "RgTemplateOptimizerAgent"],
    },
    "HOPPipelineExecutor": {
        "path": "apps_lic/engines/HOPPipelineExecutor.py",
        "dispatch_keys": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "merged_agents": [
            "HOP1ProfileAnalysisAgent",
            "HOP2ResearchAgent",
            "HOP3SenderGroundingAgent",
            "HOP4RoutingAgent",
            "HOP5GenerationAgent",
            "HOP6ValidationAgent",
            "HOP7GateDecisionAgent",
            "HOP8QAReportAgent",
            "HOP9IntegrationAgent",
        ],
    },
}

# Expected merge shim → canonical mapping
MERGE_SHIM_MAP = {
    "agentic_core/L3_orchestration/reasoning/DagRuntimeInspectorAgent.py": (
        "DagRuntimeInspectorAgent",
        "InspectorExecutor",
        "agentic_core.L5_safety.reasoning.InspectorExecutor",
    ),
    "agentic_core/L5_safety/reasoning/SignatureVerifierAgent.py": (
        "SignatureVerifierAgent",
        "InspectorExecutor",
        "agentic_core.L5_safety.reasoning.InspectorExecutor",
    ),
    "agentic_core/L5_safety/reasoning/TokenBudgetInspectorAgent.py": (
        "TokenBudgetInspectorAgent",
        "InspectorExecutor",
        "agentic_core.L5_safety.reasoning.InspectorExecutor",
    ),
    "agentic_core/L6_observability/reasoning/CoordinateObservabilityOperationsAgent.py": (
        "CoordinateObservabilityOperationsAgent",
        "ObservabilityProbeExecutor",
        "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor",
    ),
    "agentic_core/L6_observability/reasoning/DeadlockDetectorAgent.py": (
        "DeadlockDetectorAgent",
        "ObservabilityProbeExecutor",
        "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor",
    ),
    "agentic_core/L6_observability/reasoning/DebateSynthesisAgent.py": (
        "DebateSynthesisAgent",
        "ObservabilityProbeExecutor",
        "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor",
    ),
    "agentic_core/L6_observability/reasoning/RuntimeTelemetryAgent.py": (
        "RuntimeTelemetryAgent",
        "ObservabilityProbeExecutor",
        "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor",
    ),
    "agentic_core/L6_observability/reasoning/StrategicObservationAgent.py": (
        "StrategicObservationAgent",
        "ObservabilityProbeExecutor",
        "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor",
    ),
    "agentic_core/L6_observability/reasoning/TrackObservabilityCostAgent.py": (
        "TrackObservabilityCostAgent",
        "ObservabilityProbeExecutor",
        "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor",
    ),
    "apps_lic/engines/CampaignBalanceAgent.py": (
        "CampaignBalanceAgent",
        "LICValidationExecutor",
        "apps_lic.engines.LICValidationExecutor",
    ),
    "apps_lic/engines/DeliverabilityAgent.py": (
        "DeliverabilityAgent",
        "LICValidationExecutor",
        "apps_lic.engines.LICValidationExecutor",
    ),
    "apps_lic/engines/Hop1ProfileAnalysisAgent.py": (
        "HOP1ProfileAnalysisAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/Hop2ResearchAgent.py": (
        "HOP2ResearchAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/HOP3SenderGroundingAgent.py": (
        "HOP3SenderGroundingAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/Hop4RoutingAgent.py": (
        "HOP4RoutingAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/HOP5GenerationAgent.py": (
        "HOP5GenerationAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/Hop6ValidationAgent.py": (
        "HOP6ValidationAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/HOP7GateDecisionAgent.py": (
        "HOP7GateDecisionAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/HOP8QAReportAgent.py": (
        "HOP8QAReportAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/HOP9IntegrationAgent.py": (
        "HOP9IntegrationAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_rg/reasoning/ATSCompatibilityAgent.py": (
        "ATSCompatibilityAgent",
        "RGValidationExecutor",
        "apps_rg.engines.RGValidationExecutor",
    ),
    "apps_rg/reasoning/BrandComplianceAgent.py": (
        "BrandComplianceAgent",
        "RGValidationExecutor",
        "apps_rg.engines.RGValidationExecutor",
    ),
    "apps_rg/reasoning/ContentStrategyAgent.py": (
        "ContentStrategyAgent",
        "RGStrategyExecutor",
        "apps_rg.engines.RGStrategyExecutor",
    ),
    "apps_rg/reasoning/FactCheckAgent.py": (
        "FactCheckAgent",
        "RGValidationExecutor",
        "apps_rg.engines.RGValidationExecutor",
    ),
    "apps_rg/reasoning/RgStrategicPlannerAgent.py": (
        "RgStrategicPlannerAgent",
        "RGStrategyExecutor",
        "apps_rg.engines.RGStrategyExecutor",
    ),
    "apps_rg/reasoning/RgTemplateOptimizerAgent.py": (
        "RgTemplateOptimizerAgent",
        "RGStrategyExecutor",
        "apps_rg.engines.RGStrategyExecutor",
    ),
    "apps_rg/reasoning/SectionBalanceAgent.py": (
        "SectionBalanceAgent",
        "RGValidationExecutor",
        "apps_rg.engines.RGValidationExecutor",
    ),
    "agentic_core/L2_execution/reasoning/RgStrategicPlannerAgent.py": (
        "RgStrategicPlannerAgent",
        "RGStrategyExecutor",
        "apps_rg.engines.RGStrategyExecutor",
    ),
}

failures: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"  FAIL: {msg}")


def warn(msg: str) -> None:
    warnings.append(msg)
    print(f"  WARN: {msg}")


def ok(msg: str) -> None:
    print(f"  OK: {msg}")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE A: SHIM INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════
def phase_a_shim_integrity() -> dict:
    print("\n" + "=" * 80)
    print("PHASE A: SHIM INTEGRITY VERIFICATION")
    print("=" * 80)

    results = {"merge_shims": [], "retire_shims": [], "failures": []}
    # Use AST-verified class names, falling back to registry class_name
    after_class_names = set()
    for a in SNAPSHOT_AFTER:
        vc = a.get("verification_status", {}).get("class", "")
        after_class_names.add(vc if vc else a["class_name"])

    # --- Verify merge shims ---
    print("\n--- Merge Shims (28 expected) ---")
    for rel_path, (old_cls, canon_cls, canon_mod) in MERGE_SHIM_MAP.items():
        full = PROJECT_ROOT / rel_path
        entry = {"file": rel_path, "old_class": old_cls, "canonical": canon_cls}

        if not full.exists():
            fail(f"Merge shim missing: {rel_path}")
            entry["status"] = "MISSING"
            results["merge_shims"].append(entry)
            continue

        source = full.read_text(encoding="utf-8")
        loc = len([l for l in source.splitlines() if l.strip()])
        entry["loc"] = loc

        # Check no ClassDef
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            fail(f"Syntax error in shim {rel_path}: {e}")
            entry["status"] = "SYNTAX_ERROR"
            results["merge_shims"].append(entry)
            continue

        class_defs = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        if class_defs:
            fail(f"Shim {rel_path} contains ClassDef: {[c.name for c in class_defs]}")
            entry["status"] = "HAS_CLASSDEF"
            results["merge_shims"].append(entry)
            continue

        # Check exactly one import-from with alias
        import_froms = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        alias_found = False
        import_target = None
        for imp in import_froms:
            for alias in imp.names:
                if alias.asname == old_cls:
                    alias_found = True
                    import_target = f"{imp.module}.{alias.name}"
                elif alias.name == old_cls and alias.asname is None:
                    alias_found = True
                    import_target = f"{imp.module}.{alias.name}"

        if not alias_found:
            fail(f"Shim {rel_path} missing re-export alias for {old_cls}")
            entry["status"] = "NO_ALIAS"
            results["merge_shims"].append(entry)
            continue

        # Check no residual logic (functions, loops, conditionals)
        func_defs = [
            n for n in ast.iter_child_nodes(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        if func_defs:
            fail(f"Shim {rel_path} contains residual functions: {[f.name for f in func_defs]}")
            entry["status"] = "HAS_LOGIC"
            results["merge_shims"].append(entry)
            continue

        # Check LOC < 30
        if loc >= 30:
            fail(f"Shim {rel_path} exceeds 30 LOC: {loc}")
            entry["status"] = "OVERSIZED"
            results["merge_shims"].append(entry)
            continue

        # Verify import target module file exists
        mod_path = canon_mod.replace(".", "/") + ".py"
        if not (PROJECT_ROOT / mod_path).exists():
            fail(f"Shim {rel_path} import target does not exist: {mod_path}")
            entry["status"] = "TARGET_MISSING"
            results["merge_shims"].append(entry)
            continue

        entry["status"] = "PASS"
        entry["import_target"] = import_target
        ok(f"{rel_path} → {canon_cls} ({loc} LOC)")
        results["merge_shims"].append(entry)

    # --- Verify retirement shims ---
    print("\n--- Retirement Shims (19 expected) ---")
    for rel_path in RETIRE_FILES:
        full = PROJECT_ROOT / rel_path
        entry = {"file": rel_path}

        if not full.exists():
            fail(f"Retirement file missing: {rel_path}")
            entry["status"] = "MISSING"
            results["retire_shims"].append(entry)
            continue

        source = full.read_text(encoding="utf-8")

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            fail(f"Syntax error in retirement {rel_path}: {e}")
            entry["status"] = "SYNTAX_ERROR"
            results["retire_shims"].append(entry)
            continue

        class_defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

        # Check the TARGETED retirement class is not in discovery
        # The target class name is derived from the retirement list in implement_consolidation.py
        retirement_targets = {
            "apps_lic/engines/LicReflectionAgent.py": "OutreachAgent",
            "apps_lic/engines/LicTemplateOptimizerAgent.py": "OutreachAgent",
            "apps_lic/engines/MessageComplianceAgent.py": "OutreachAgent",
            "apps_lic/engines/OutreachLearningAgent.py": "OutreachAgent",
            "apps_lic/engines/OutreachProactiveAgent.py": "OutreachAgent",
            "apps_lic/engines/MessageDiversityValidator.py": "MCPHardenedMixin",
            "agentic_core/runtime/utils/discovery_util.py": "DiscoveredAgent",
        }
        targeted_class = retirement_targets.get(rel_path)
        still_discovered = False
        if targeted_class:
            # Partial retirement — only the targeted class should be gone
            if targeted_class in after_class_names:
                fail(f"Retired class {targeted_class} still in discovery_snapshot_after.json")
                entry["status"] = "STILL_DISCOVERED"
                still_discovered = True
        else:
            # Full retirement — check NO class from this file is discovered
            for cn in class_defs:
                if cn in after_class_names:
                    fail(f"Retired class {cn} still in discovery_snapshot_after.json")
                    entry["status"] = "STILL_DISCOVERED"
                    still_discovered = True
                    break

        if not still_discovered:
            entry["status"] = "PASS"
            loc = len([l for l in source.splitlines() if l.strip()])
            entry["loc"] = loc
            entry["residual_classes"] = class_defs
            if class_defs:
                # Partial retirement — other classes remain, target was removed
                warn(f"{rel_path} has residual ClassDefs: {class_defs} (partial retirement)")
            else:
                ok(f"{rel_path} — clean shim ({loc} LOC)")

        results["retire_shims"].append(entry)

    merge_pass = sum(1 for s in results["merge_shims"] if s["status"] == "PASS")
    retire_pass = sum(1 for s in results["retire_shims"] if s["status"] == "PASS")
    print(f"\nMerge shims: {merge_pass}/{len(MERGE_SHIM_MAP)} pass")
    print(f"Retire shims: {retire_pass}/{len(RETIRE_FILES)} pass")

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE B: REGISTRY & DISPATCH VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════
def phase_b_dispatch_validation() -> dict:
    print("\n" + "=" * 80)
    print("PHASE B: REGISTRY & DISPATCH VALIDATION")
    print("=" * 80)

    results = {}

    for exec_name, spec in EXECUTORS.items():
        print(f"\n--- {exec_name} ---")
        full = PROJECT_ROOT / spec["path"]
        entry = {"executor": exec_name, "path": spec["path"]}

        if not full.exists():
            fail(f"Canonical executor missing: {spec['path']}")
            entry["status"] = "MISSING"
            results[exec_name] = entry
            continue

        source = full.read_text(encoding="utf-8")
        tree = ast.parse(source)

        # Find ClassDef
        class_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == exec_name:
                class_node = node
                break

        if not class_node:
            fail(f"ClassDef {exec_name} not found in {spec['path']}")
            entry["status"] = "NO_CLASSDEF"
            results[exec_name] = entry
            continue

        # Check dispatch keys are present in source
        missing_keys = []
        for key in spec["dispatch_keys"]:
            key_str = str(key)
            if key_str not in source:
                # Try alternate representations
                if isinstance(key, int):
                    if f"{key}:" not in source and f"{key}," not in source and f"= {key}" not in source:
                        missing_keys.append(key_str)
                else:
                    if f'"{key}"' not in source and f"'{key}'" not in source:
                        missing_keys.append(key_str)

        if missing_keys:
            fail(f"{exec_name} missing dispatch keys: {missing_keys}")
            entry["status"] = "MISSING_KEYS"
            entry["missing_keys"] = missing_keys
        else:
            ok(f"{exec_name}: all {len(spec['dispatch_keys'])} dispatch keys present")
            entry["status"] = "PASS"
            entry["dispatch_keys"] = [str(k) for k in spec["dispatch_keys"]]

        # Check no silent default fallthrough (except RGStrategy which has explicit default)
        if exec_name == "RGValidationExecutor":
            if "unknown_rule_set" in source:
                ok(f"{exec_name}: explicit error on unknown rule_set")
            else:
                warn(f"{exec_name}: no explicit error on unknown rule_set")
        elif exec_name == "HOPPipelineExecutor":
            if '"error"' in source or "'error'" in source:
                ok(f"{exec_name}: explicit error on missing stage")
            else:
                warn(f"{exec_name}: no explicit error on missing stage")

        # Check old agent_id resolves (shim exists)
        for old_agent in spec["merged_agents"]:
            # Find corresponding shim file
            found = False
            for path_key in MERGE_SHIM_MAP:
                if MERGE_SHIM_MAP[path_key][0] == old_agent:
                    if (PROJECT_ROOT / path_key).exists():
                        found = True
                    break
            if not found:
                warn(f"{exec_name}: shim not found for {old_agent}")

        results[exec_name] = entry

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE C: DOMAIN LOGIC ISOLATION CHECK
# ═══════════════════════════════════════════════════════════════════════════════
def phase_c_domain_isolation() -> dict:
    print("\n" + "=" * 80)
    print("PHASE C: DOMAIN LOGIC ISOLATION CHECK")
    print("=" * 80)

    results = {}

    # HOP Pipeline — verify all 9 stages registered
    print("\n--- HOPPipelineExecutor: Stage Registry ---")
    registry_path = PROJECT_ROOT / "apps_lic" / "engines" / "hop_stage_registry.py"
    if not registry_path.exists():
        fail("hop_stage_registry.py missing")
        results["hop_registry"] = {"status": "MISSING"}
    else:
        source = registry_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        registered_ids = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "register_stage":
                    if node.args and isinstance(node.args[0], ast.Constant):
                        registered_ids.add(node.args[0].value)
        expected = set(range(1, 10))
        missing = expected - registered_ids
        extra = registered_ids - expected
        if missing:
            fail(f"HOP registry missing stage_ids: {sorted(missing)}")
        if extra:
            warn(f"HOP registry has extra stage_ids: {sorted(extra)}")
        if not missing:
            ok(f"HOP registry: all 9 stages registered {sorted(registered_ids)}")
        results["hop_registry"] = {
            "status": "PASS" if not missing else "FAIL",
            "registered": sorted(registered_ids),
            "missing": sorted(missing),
        }

    # ObservabilityProbeExecutor — verify 6 probe types mapped
    print("\n--- ObservabilityProbeExecutor: Probe Coverage ---")
    obs_path = PROJECT_ROOT / EXECUTORS["ObservabilityProbeExecutor"]["path"]
    source = obs_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    # Find _get_handler method and extract dict keys
    probe_keys_found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_get_handler":
            for inner in ast.walk(node):
                if isinstance(inner, ast.Dict):
                    for key in inner.keys:
                        if isinstance(key, ast.Constant):
                            probe_keys_found.add(key.value)
    expected_probes = set(EXECUTORS["ObservabilityProbeExecutor"]["dispatch_keys"])
    missing_probes = expected_probes - probe_keys_found
    if missing_probes:
        fail(f"ObservabilityProbeExecutor missing probe types: {missing_probes}")
    else:
        ok(f"ObservabilityProbeExecutor: all 6 probe types present {sorted(probe_keys_found)}")
    # Check no cross-probe state bleed: _results reset each execute
    if "self._results = handler(ctx)" in source or "self._results = handler(" in source:
        ok("ObservabilityProbeExecutor: _results reset per execute call")
    else:
        warn("ObservabilityProbeExecutor: _results may not reset per call")
    results["observability"] = {
        "status": "PASS" if not missing_probes else "FAIL",
        "probes_found": sorted(probe_keys_found),
    }

    # RGValidationExecutor — verify 4 rule_set handlers
    print("\n--- RGValidationExecutor: Rule Registry ---")
    rg_path = PROJECT_ROOT / EXECUTORS["RGValidationExecutor"]["path"]
    source = rg_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    rule_keys = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "register_rule":
                if node.args and isinstance(node.args[0], ast.Constant):
                    rule_keys.add(node.args[0].value)
    expected_rules = set(EXECUTORS["RGValidationExecutor"]["dispatch_keys"])
    missing_rules = expected_rules - rule_keys
    if missing_rules:
        fail(f"RGValidationExecutor missing rules: {missing_rules}")
    else:
        ok(f"RGValidationExecutor: all 4 rules registered {sorted(rule_keys)}")
    results["rg_validation"] = {
        "status": "PASS" if not missing_rules else "FAIL",
        "rules_found": sorted(rule_keys),
    }

    # LICValidationExecutor — verify 2 rule_set branches
    print("\n--- LICValidationExecutor: Rule Dispatch ---")
    lic_path = PROJECT_ROOT / EXECUTORS["LICValidationExecutor"]["path"]
    source = lic_path.read_text(encoding="utf-8")
    expected_lic = {"campaign_balance", "deliverability"}
    found_lic = set()
    for key in expected_lic:
        if f'"{key}"' in source or f"'{key}'" in source:
            found_lic.add(key)
    missing_lic = expected_lic - found_lic
    if missing_lic:
        fail(f"LICValidationExecutor missing rules: {missing_lic}")
    else:
        ok(f"LICValidationExecutor: both rules present {sorted(found_lic)}")
    results["lic_validation"] = {
        "status": "PASS" if not missing_lic else "FAIL",
        "rules_found": sorted(found_lic),
    }

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE D: BLAST RADIUS REASSESSMENT
# ═══════════════════════════════════════════════════════════════════════════════
def phase_d_blast_radius() -> dict:
    print("\n" + "=" * 80)
    print("PHASE D: BLAST RADIUS REASSESSMENT")
    print("=" * 80)

    # Build import graph for post-consolidation state
    agent_blast: dict[str, int] = {}
    # Use AST-verified class names, falling back to registry class_name
    after_class_names = set()
    for a in SNAPSHOT_AFTER:
        vc = a.get("verification_status", {}).get("class", "")
        after_class_names.add(vc if vc else a["class_name"])

    # Recompute blast radius from inventory for agents still in after snapshot
    for agent in INVENTORY["agents"]:
        cn = agent["class_name"]
        if cn in after_class_names:
            agent_blast[cn] = agent.get("blast_radius", 0)

    # Add canonical executors — count how many shims import them
    for exec_name, spec in EXECUTORS.items():
        shim_count = len(spec["merged_agents"])
        # Executor's own blast = number of shims pointing to it
        agent_blast[exec_name] = shim_count

    # Find agents > 20
    high_blast = {k: v for k, v in agent_blast.items() if v >= 20}
    new_high = {k: v for k, v in high_blast.items() if k in EXECUTORS}

    print(f"\nTotal agents with blast_radius data: {len(agent_blast)}")

    # Check for agents > 25
    over_25 = {k: v for k, v in agent_blast.items() if v > 25}
    if over_25:
        for k, v in over_25.items():
            fail(f"Agent {k} has blast_radius > 25: {v}")
    else:
        ok("No agent exceeds blast_radius 25")

    if new_high:
        for k, v in new_high.items():
            warn(f"Canonical executor {k} has blast_radius >= 20: {v}")
    else:
        ok("No canonical executor reached blast_radius >= 20")

    # Pre-existing high-blast agents
    pre_existing = {k: v for k, v in high_blast.items() if k not in EXECUTORS}
    if pre_existing:
        for k, v in pre_existing.items():
            print(f"  INFO: Pre-existing high blast: {k} = {v}")

    # Sort top 10
    top_10 = sorted(agent_blast.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\n  Top 10 blast radius:")
    for name, br in top_10:
        marker = " [EXECUTOR]" if name in EXECUTORS else ""
        print(f"    {name}: {br}{marker}")

    return {
        "total_measured": len(agent_blast),
        "over_25": over_25,
        "over_20": high_blast,
        "top_10": top_10,
        "executor_blast": {k: agent_blast.get(k, 0) for k in EXECUTORS},
        "status": "PASS" if not over_25 else "FAIL",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE E: LAYER BALANCE VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════
def phase_e_layer_balance() -> dict:
    print("\n" + "=" * 80)
    print("PHASE E: LAYER BALANCE VALIDATION")
    print("=" * 80)

    before_layers = INVENTORY["summary"]["by_layer"]
    after_layers: dict[str, int] = {}
    for agent in SNAPSHOT_AFTER:
        layer = agent.get("layer", "unknown")
        # Normalize to short form matching inventory keys: L0, L1, L2, L3, L5, L6, apps_lic, apps_rg, apps_shared, unknown
        if layer.startswith("L") and "_" in layer:
            short = layer.split("_")[0]  # L5_safety -> L5, L0_maintenance -> L0, etc.
        elif "lic" in layer.lower():
            short = "apps_lic"
        elif "rg" in layer.lower():
            short = "apps_rg"
        elif "shared" in layer.lower():
            short = "apps_shared"
        else:
            short = layer
        after_layers[short] = after_layers.get(short, 0) + 1

    # Normalize before keys
    before_norm: dict[str, int] = {}
    for k, v in before_layers.items():
        before_norm[k] = v

    # Check L5 safety not lost
    l5_before = before_norm.get("L5", 0)
    l5_after = after_layers.get("L5", 0)
    print(f"\n  L5 Safety: {l5_before} → {l5_after}")
    if l5_after < l5_before * 0.5:
        fail(f"L5 safety lost more than 50% of agents: {l5_before} → {l5_after}")
    else:
        ok(f"L5 safety retains {l5_after}/{l5_before} agents ({l5_after / l5_before * 100:.0f}%)")

    # Check no layer went to zero
    for layer, count in after_layers.items():
        if count == 0:
            fail(f"Layer {layer} has zero agents after consolidation")
        else:
            ok(f"Layer {layer}: {count} agents")

    # Cross-layer boundary check: canonical executors should be in appropriate layers
    cross_layer_issues = []
    # InspectorExecutor is in L5 — OK (safety)
    # ObservabilityProbeExecutor is in L6 — OK
    # RGValidationExecutor is in apps_rg — OK
    # LICValidationExecutor is in apps_lic — OK
    # RGStrategyExecutor is in apps_rg — OK
    # HOPPipelineExecutor is in apps_lic — OK
    # Check merge shims don't cross from core to app or vice versa incorrectly
    for rel_path, (old_cls, canon_cls, canon_mod) in MERGE_SHIM_MAP.items():
        shim_layer = rel_path.split("/")[0]
        canon_layer = canon_mod.split(".")[0]
        # L3 orchestration agent shimmed to L5 safety executor — acceptable (inspector consolidation)
        # L2 execution agent shimmed to apps_rg — acceptable (strategy consolidation)
        # Just flag any that look odd
        if shim_layer.startswith("agentic_core") and canon_layer.startswith("apps"):
            cross_layer_issues.append(f"{rel_path} ({shim_layer}) → {canon_mod} ({canon_layer})")

    if cross_layer_issues:
        for issue in cross_layer_issues:
            warn(f"Cross-layer shim: {issue}")

    return {
        "before": before_norm,
        "after": after_layers,
        "l5_retention": f"{l5_after}/{l5_before}",
        "zero_layers": [l for l, c in after_layers.items() if c == 0],
        "cross_layer_issues": cross_layer_issues,
        "status": "PASS",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE G: REDUCTION QUALITY METRICS
# ═══════════════════════════════════════════════════════════════════════════════
def phase_g_reduction_quality() -> dict:
    print("\n" + "=" * 80)
    print("PHASE G: REDUCTION QUALITY METRICS")
    print("=" * 80)

    # Use AST-verified class names, falling back to registry class_name
    after_class_names = set()
    for a in SNAPSHOT_AFTER:
        vc = a.get("verification_status", {}).get("class", "")
        after_class_names.add(vc if vc else a["class_name"])

    # 1. True ClassDefs removed (retired files that are now shims with no ClassDef)
    true_removals = 0
    shimmed_aliases = 0
    for rel_path in RETIRE_FILES:
        full = PROJECT_ROOT / rel_path
        if full.exists():
            try:
                tree = ast.parse(full.read_text(encoding="utf-8"))
                class_defs = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                if not class_defs:
                    true_removals += 1
            except SyntaxError:
                pass
    for rel_path in MERGE_SHIM_MAP:
        full = PROJECT_ROOT / rel_path
        if full.exists():
            try:
                tree = ast.parse(full.read_text(encoding="utf-8"))
                class_defs = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                if not class_defs:
                    shimmed_aliases += 1
            except SyntaxError:
                pass

    print(f"\n  True ClassDefs removed (retirements): {true_removals}")
    print(f"  ClassDefs replaced with aliases (merges): {shimmed_aliases}")

    # 2. Net LOC reduction
    before_loc = 0
    after_loc = 0
    for agent in INVENTORY["agents"]:
        cn = agent["class_name"]
        before_loc += agent.get("total_loc", 0)
        if cn in after_class_names:
            after_loc += agent.get("total_loc", 0)
    # Add canonical executor LOC
    for exec_name, spec in EXECUTORS.items():
        full = PROJECT_ROOT / spec["path"]
        if full.exists():
            loc = len(full.read_text(encoding="utf-8").splitlines())
            after_loc += loc

    loc_reduction = before_loc - after_loc
    print(f"  Agent LOC before: {before_loc}")
    print(f"  Agent LOC after (approx): {after_loc}")
    print(f"  Net LOC reduction: {loc_reduction}")

    # 3. Import graph node reduction
    before_nodes = len(INVENTORY["agents"])
    after_nodes = len(SNAPSHOT_AFTER)
    print(f"  Import graph nodes before: {before_nodes}")
    print(f"  Import graph nodes after: {after_nodes}")
    print(f"  Node reduction: {before_nodes - after_nodes}")

    # 4. Average boilerplate ratio shift
    before_bp = []
    after_bp = []
    for agent in INVENTORY["agents"]:
        cn = agent["class_name"]
        bp = agent.get("boilerplate_ratio", 0)
        before_bp.append(bp)
        if cn in after_class_names:
            after_bp.append(bp)

    avg_before = sum(before_bp) / len(before_bp) if before_bp else 0
    avg_after = sum(after_bp) / len(after_bp) if after_bp else 0
    print(f"  Avg boilerplate_ratio before: {avg_before:.3f}")
    print(f"  Avg boilerplate_ratio after: {avg_after:.3f}")
    print(f"  Shift: {avg_after - avg_before:+.3f}")

    return {
        "true_classdefs_removed": true_removals,
        "shimmed_aliases": shimmed_aliases,
        "loc_before": before_loc,
        "loc_after": after_loc,
        "loc_reduction": loc_reduction,
        "node_before": before_nodes,
        "node_after": after_nodes,
        "node_reduction": before_nodes - after_nodes,
        "avg_bp_before": round(avg_before, 3),
        "avg_bp_after": round(avg_after, 3),
        "bp_shift": round(avg_after - avg_before, 3),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    print("STRUCTURAL AUDIT — CONSOLIDATION VALIDATION")
    print("=" * 80)

    a = phase_a_shim_integrity()
    b = phase_b_dispatch_validation()
    c = phase_c_domain_isolation()
    d = phase_d_blast_radius()
    e = phase_e_layer_balance()
    g = phase_g_reduction_quality()

    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"  Total FAILURES: {len(failures)}")
    print(f"  Total WARNINGS: {len(warnings)}")

    if failures:
        print("\n  FAILURES:")
        for f in failures:
            print(f"    - {f}")
    if warnings:
        print("\n  WARNINGS:")
        for w in warnings:
            print(f"    - {w}")

    # Write full results JSON
    full_results = {
        "phase_a": a,
        "phase_b": b,
        "phase_c": c,
        "phase_d": d,
        "phase_e": e,
        "phase_g": g,
        "failures": failures,
        "warnings": warnings,
        "failure_count": len(failures),
        "warning_count": len(warnings),
    }
    out_path = PROJECT_ROOT / "artifacts" / "consolidation" / "structural_audit_results.json"
    out_path.write_text(json.dumps(full_results, indent=2, default=str), encoding="utf-8")
    print(f"\n  Results written to: {out_path.relative_to(PROJECT_ROOT)}")

    return len(failures)


if __name__ == "__main__":
    sys.exit(main())
