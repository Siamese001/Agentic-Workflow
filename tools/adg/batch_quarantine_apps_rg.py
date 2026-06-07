"""Batch quarantine all apps_rg runtime files violating AG-RGGOV-8.

Quarantines all non-ingress files in apps_rg that have runtime authority violations.
"""

from __future__ import annotations

import os
from pathlib import Path


def quarantine_file(file_path: Path, reason: str) -> None:
    """Quarantine a single file with RuntimeError notice."""
    rel_path = file_path.relative_to(Path("c:/Git/Agentic-Workflow-FRESH/apps_rg"))
    
    module_path = str(rel_path).replace('/', '.').replace('\\', '.').replace('.py', '')
    
    quarantine_content = f'''"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT contain runtime authority code.

Original: apps_rg/{rel_path}
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — {reason}

Importing this module raises RuntimeError immediately.
Core owns all runtime authority.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/{rel_path}.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.{module_path} is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core owns all runtime. "
    "See: docs/archive/windsurf/legacy-tree/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
'''
    
    # Archive original first
    archive_dir = Path(f"c:/Git/Agentic-Workflow-FRESH/archives/apps_rg/quarantine_w4_20260509/{rel_path.parent}")
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{rel_path.name}.ORIGINAL"
    
    if file_path.exists() and not archive_path.exists():
        try:
            original_content = file_path.read_text(encoding="utf-8")
            archive_path.write_text(original_content, encoding="utf-8")
        except Exception:
            pass
    
    # Write quarantine notice
    file_path.write_text(quarantine_content, encoding="utf-8")
    print(f"Quarantined: {rel_path}")


def main() -> int:
    """Batch quarantine all violating files."""
    apps_rg_path = Path("c:/Git/Agentic-Workflow-FRESH/apps_rg")
    
    # Directories to quarantine entirely (they contain runtime authority)
    quarantine_dirs = [
        "engines",
        "reasoning", 
        "validators",
        "types",
        "outputs",
        "scripts",
        "bootstrap_runtime.py",
        "config/reasoning_toggles_config.py",
    ]
    
    # Specific tools to quarantine (ones with lifecycle imports)
    tools_to_quarantine = [
        "PrepareResumeContext.py",
        "query_past_generations.py", 
        "RefineResumeRanking.py",
        "AdjustSectionWeights.py",
        "context_formatter_tool.py",
        "create_experience_bullets.py",
        "EvaluateResumeEffectiveness.py",
        "execute_message_generation.py",
        "fetch_user_preferences.py",
        "InspectResumeQuality.py",
        "invoke_generation_service.py",
        "local_workflow_loader.py",
        "OptimizeContentOrder.py",
    ]
    
    # Quarantine entire directories
    for dir_name in quarantine_dirs:
        dir_path = apps_rg_path / dir_name
        if dir_path.exists():
            for py_file in dir_path.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                quarantine_file(py_file, f"{dir_name}/ contains runtime authority")
    
    # Quarantine specific tools
    tools_dir = apps_rg_path / "tools"
    for tool_name in tools_to_quarantine:
        tool_path = tools_dir / tool_name
        if tool_path.exists():
            quarantine_file(tool_path, "lifecycle_trace_contract import")
    
    print("\nBatch quarantine complete.")
    return 0


if __name__ == "__main__":
    exit(main())
