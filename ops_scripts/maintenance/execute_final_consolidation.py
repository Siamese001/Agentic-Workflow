"""
Final Consolidation Script - The End of Sprawl

1. Scans the codebase for imports pointing to deleted "Imposter" files.
2. Rewrites them to point to the "Canon" locations.
3. Runs the final ArchGuard verification.
"""

import os
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

IMPORT_REDIRECTS = {
    r"agentic_core\.L5_safety\.guardrails\.cached_safety_shield": "agentic_core.L5_safety.validators.cached_safety_shield",
    r"agentic_core\.L5_safety\.guardrails\.NeuralAutoImmuneAgent": "agentic_core.L5_safety.validators.NeuralAutoImmuneAgent",
    r"agentic_core\.L5_safety\.validators\.DependencyDiplomatAgent": "agentic_core.L0_maintenance.scripts.DependencyDiplomatAgent",
    r"agentic_core\.L5_safety\.validators\.SemanticTerritoryMapperAgent": "agentic_core.L1_cognition.reasoning.SemanticTerritoryMapperAgent",
    r"agentic_core\.L2_execution\.tool_registry\.L2ExecutionBase": "agentic_core.L2_execution.L2ExecutionBase",
}


def fix_imports():
    print("--- STARTING FINAL IMPORT REWIRING ---")
    fixed_count = 0

    for root, _dirs, files in os.walk(PROJECT_ROOT / "agentic_core"):
        if "archived" in root:
            continue

        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = Path(root) / file
            try:
                content = file_path.read_text(encoding="utf-8")
                original_content = content

                for bad_pattern, good_path in IMPORT_REDIRECTS.items():
                    if re.search(bad_pattern, content):
                        content = re.sub(bad_pattern, good_path, content)

                if content != original_content:
                    file_path.write_text(content, encoding="utf-8")
                    print(f"[FIXED] Rewired imports in {file}")
                    fixed_count += 1
            except Exception as e:
                print(f"[ERROR] processing {file}: {e}")

    print(f"--- REWIRING COMPLETE: {fixed_count} files updated ---")


def run_verification():
    print("\n--- RUNNING FINAL VERIFICATION ---")
    try:
        result = subprocess.run(
            ["pytest", "tests/integration/test_arch_guard.py"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.returncode == 0:
            print("\n✅ SYSTEM IS GREEN. 100% SOVEREIGN COMPLIANCE.")
        else:
            print("\n⚠️ SYSTEM HAS REMAINING ISSUES. SEE OUTPUT ABOVE.")
            print(result.stderr)
    except Exception as e:
        print(f"Verification failed to run: {e}")


if __name__ == "__main__":
    fix_imports()
    run_verification()
