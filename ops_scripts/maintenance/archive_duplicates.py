import shutil
import sys
from datetime import datetime
from pathlib import Path

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent.parent
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
ARCHIVE_BASE = PROJECT_ROOT / "archives" / "consolidated_duplicates" / f"batch_{TIMESTAMP}"

# The exact list of 13 files identified in the Agent Overlap Analysis Report
TARGETS = [
    # 1. The 11 Unified Agents (from guardrails)
    "agentic_core/L5_safety/guardrails/CodeDetectorAgent.py",
    "agentic_core/L5_safety/guardrails/CodeEnforcerAgent.py",
    "agentic_core/L5_safety/guardrails/CodeHealerAgent.py",
    "agentic_core/L5_safety/guardrails/CodeValidatorAgent.py",
    "agentic_core/L5_safety/guardrails/ResourceManagerAgent.py",
    "agentic_core/L5_safety/guardrails/SafetyDetectorAgent.py",
    "agentic_core/L5_safety/guardrails/SafetyExecutorAgent.py",
    "agentic_core/L5_safety/guardrails/SecurityManagerAgent.py",
    "agentic_core/L5_safety/guardrails/StructureEnforcerAgent.py",
    "agentic_core/L5_safety/guardrails/StructureHealerAgent.py",
    "agentic_core/L5_safety/guardrails/StructureValidatorAgent.py",
    # 2. The Duplicate Model router (from tool_registry)
    "agentic_core/L2_execution/tool_registry/ModelRouterAgent.py",
    # 3. The Duplicate Hygiene Agent (from apps_shared)
    "apps_shared/base_agents/HygieneGuardianAgent.py",
]


def main():
    print(f"[*] Starting Archive Operation: {TIMESTAMP}")
    print(f"[*] Archive Destination: {ARCHIVE_BASE}")

    # Ensure archive directory exists
    if not ARCHIVE_BASE.exists():
        try:
            ARCHIVE_BASE.mkdir(parents=True, exist_ok=True)
            print("[+] Created archive directory.")
        except Exception as e:
            print(f"[!] Critical Error: Could not create archive directory: {e}")
            sys.exit(1)

    moved_count = 0
    missing_count = 0

    for rel_path in TARGETS:
        source_path = PROJECT_ROOT / rel_path
        filename = source_path.name

        # Handle path conflicts if multiple files have same name
        dest_path = ARCHIVE_BASE / filename
        if dest_path.exists():
            # Append parent dir name to filename to avoid overwrite
            parent_name = source_path.parent.name
            dest_path = ARCHIVE_BASE / f"{parent_name}_{filename}"

        if source_path.exists():
            try:
                shutil.move(str(source_path), str(dest_path))
                print(f"[+] Archived: {rel_path}")
                moved_count += 1
            except Exception as e:
                print(f"[!] Failed to move {rel_path}: {e}")
        else:
            print(f"[-] Skipped (Not Found): {rel_path}")
            missing_count += 1

    print("-" * 50)
    print("SUMMARY:")
    print(f"  Moved:   {moved_count}")
    print(f"  Missing: {missing_count}")
    print("-" * 50)

    if moved_count > 0:
        print("✅ Archive operation completed successfully.")
    else:
        print("⚠️  No files were moved.")


if __name__ == "__main__":
    main()
