#!/usr/bin/env python3
"""
Generate functionality metrics for Phase 2 manual review duplicates.
"""
from pathlib import Path
from datetime import datetime

from agentic_core.config.blueprint_sovereign.structure_blueprint_1 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)


PHASE2_PAIRS = [
    ("agentic_core/L4_state/ValidationContext/CheckpointManagerAgent.py", 
     "agentic_core/runtime/shared_runtime/CheckpointManagerAgent.py"),
    ("agentic_core/L2_execution/ToolRegistry/CognitiveContractManagerAgent.py",
     "agentic_core/schemas/models/CognitiveContractManagerAgent.py"),
    ("agentic_core/L5_safety/guardrails/DeadCodeDetectorAgent.py",
     "agentic_core/utils/core_extensions/DeadCodeDetectorAgent.py"),
    ("agentic_core/L4_state/filesystem/FileManagerAgent.py",
     "agentic_core/utils/core_extensions/FileManagerAgent.py"),
    ("agentic_core/L5_safety/validators/GovernanceAgent.py",
     "agentic_core/L1_cognition/thought_engine/GovernanceAgent.py"),
    ("agentic_core/L2_execution/ToolRegistry/HealerAgent.py",
     "agentic_core/L5_safety/guardrails/HealerAgent.py"),
    ("agentic_core/L1_cognition/learning/MetaLearningAgent.py",
     "agentic_core/L1_cognition/thought_engine/MetaLearningAgent.py"),
    ("agentic_core/L1_cognition/learning/MetaLearningAgent.py",
     "agentic_core/L3_orchestration/meta_learning/MetaLearningAgent.py"),
    ("agentic_core/L2_execution/ToolRegistry/PromptGovernorAgent.py",
     "agentic_core/prompt_governance/rendering/PromptGovernorAgent.py"),
    ("agentic_core/L3_orchestration/workflow_engines/TerritoryHealerAgent.py",
     "agentic_core/L5_safety/guardrails/TerritoryHealerAgent.py"),
]


def count_methods(file_path: Path) -> int:
    try:
        content = file_path.read_text(encoding='utf-8')
        return sum(1 for line in content.split('\n') if line.strip().startswith('def '))
    except:
        return 0


def has_pattern(file_path: Path, pattern: str) -> bool:
    try:
        return pattern in file_path.read_text(encoding='utf-8')
    except:
        return False


def count_lines(file_path: Path) -> int:
    try:
        return len(file_path.read_text(encoding='utf-8').split('\n'))
    except:
        return 0


def main():
    project_root = Path.cwd()
    
    print("=" * 80)
    print("PHASE 2: MANUAL REVIEW DUPLICATE METRICS")
    print("=" * 80)
    
    report_file = project_root / REPORTS_DIR / "phase2_metrics_report.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Phase 2: Manual Review Duplicate Metrics\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("| Agent | Canonical | Duplicate | Can Lines | Dup Lines | Can Methods | Dup Methods | Recommendation |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- | --- |\n")
        
        delete_commands = []
        
        for canonical_rel, duplicate_rel in PHASE2_PAIRS:
            canonical = project_root / canonical_rel
            duplicate = project_root / duplicate_rel
            
            if not canonical.exists():
                print(f"[SKIP] Canonical not found: {canonical_rel}")
                continue
            if not duplicate.exists():
                print(f"[SKIP] Duplicate not found: {duplicate_rel}")
                continue
            
            agent_name = canonical.stem
            
            can_lines = count_lines(canonical)
            dup_lines = count_lines(duplicate)
            can_methods = count_methods(canonical)
            dup_methods = count_methods(duplicate)
            can_heal = has_pattern(canonical, 'def heal')
            dup_heal = has_pattern(duplicate, 'def heal')
            can_mcp = has_pattern(canonical, 'MCPHardened')
            dup_mcp = has_pattern(duplicate, 'MCPHardened')
            
            # Determine recommendation
            if can_lines >= dup_lines and can_methods >= dup_methods:
                rec = "✅ DELETE duplicate"
            elif can_heal and not dup_heal:
                rec = "✅ DELETE duplicate (no heal)"
            elif can_mcp and not dup_mcp:
                rec = "✅ DELETE duplicate (no MCP)"
            else:
                rec = "⚠️ REVIEW needed"
            
            print(f"\n[{agent_name}]")
            print(f"  Canonical: {canonical_rel}")
            print(f"    Lines: {can_lines}, Methods: {can_methods}, Heal: {can_heal}, MCP: {can_mcp}")
            print(f"  Duplicate: {duplicate_rel}")
            print(f"    Lines: {dup_lines}, Methods: {dup_methods}, Heal: {dup_heal}, MCP: {dup_mcp}")
            print(f"  → {rec}")
            
            can_short = canonical_rel.split('/')[-2] + '/' + canonical.name
            dup_short = duplicate_rel.split('/')[-2] + '/' + duplicate.name
            
            f.write(f"| {agent_name} | `{can_short}` | `{dup_short}` | {can_lines} | {dup_lines} | ")
            f.write(f"{can_methods} | {dup_methods} | {rec} |\n")
            
            if "DELETE" in rec:
                delete_commands.append(f'git rm "{duplicate_rel}"')
        
        f.write("\n---\n\n")
        f.write("## Delete Commands (After Review)\n\n")
        f.write("```bash\n")
        for cmd in delete_commands:
            f.write(cmd + "\n")
        f.write('git commit -m "chore: remove Phase 2 duplicate agents"\n')
        f.write("```\n")
    
    print(f"\n✅ Report: {report_file}")


if __name__ == "__main__":
    main()
