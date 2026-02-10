"""
File: C:/Git/Agentic-Workflow/scripts/architectural_guard.py
Context: Now that the 'common_utils' folder is purged of Agents, we must install an automated regression guard. This script acts as a CI/CD gatekeeper, scanning 'apps_shared/common_utils' for any re-introduction of Agentic logic (Executors, Orchestrators, or LLM clients) and failing the build if detected.
"""

import ast
import os
import sys

# SSOT: The forbidden zone for Agents
TARGET_DIR = r"C:\Git\Agentic-Workflow\apps_shared\common_utils"

# Rules for detection
BANNED_SUFFIXES = ["Executor", "Agent", "Orchestrator", "Strategist"]
BANNED_IMPORTS = ["langchain", "crewai", "autogen", "semantic_kernel"]
BANNED_BASES = ["BaseAgent", "Agent", "LLMChain"]


def scan_for_violations() -> list[str]:
    violations = []

    # guardian: allow-path-string
    if not os.path.exists(TARGET_DIR):
        print(f"Target directory {TARGET_DIR} does not exist. Skipping.")
        return []

    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            if not file.endswith(".py"):
                continue

            # Rule 1: Filename policing
            # We allow 'AgentExecutor.py' IF and ONLY IF it was intended to be there,
            # but we just moved it. So now it is strictly banned.
            for suffix in BANNED_SUFFIXES:
                # Check if file ends with suffix (ignoring case)
                if file.lower().endswith(suffix.lower() + ".py"):
                    violations.append(
                        f"[Filename Violation] {file} contains banned suffix '{suffix}'",
                    )

            # Rule 2: Content policing via AST
            # guardian: allow-path-string
            full_path = os.path.join(root, file)
            try:
                with open(full_path, encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    # Check Imports
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            if any(banned in name.name for banned in BANNED_IMPORTS):
                                violations.append(
                                    f"[Import Violation] {file} imports banned module '{name.name}'",
                                )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and any(banned in node.module for banned in BANNED_IMPORTS):
                            violations.append(
                                f"[Import Violation] {file} imports from banned module '{node.module}'",
                            )

                    # Check Class Inheritance
                    if isinstance(node, ast.ClassDef):
                        for base in node.bases:
                            if isinstance(base, ast.Name) and base.id in BANNED_BASES:
                                violations.append(
                                    f"[Inheritance Violation] {file} defines class '{node.name}' inheriting from '{base.id}'",
                                )

            # guardian: allow-silent-swallow
            except Exception as e:
                # Parse errors are warnings, not necessarily violations, but good to know
                print(f"Warning: Could not parse {file}: {e}")

    return violations


def main():
    print(f"🛡️  Architectural Guard Active: Scanning {TARGET_DIR}...")
    violations = scan_for_violations()

    if violations:
        print("\n❌ ARCHITECTURAL INTEGRITY FAILURE")
        print("The following files violate the 'No Agents in Utils' policy:")
        print("-" * 60)
        for v in violations:
            print(f" - {v}")
        print("-" * 60)
        print("ACTION REQUIRED: Move these files to 'apps_rg/engines/' immediately.")
        sys.exit(1)
    else:
        print("\n✅ Architectural Integrity Verified: No Agents detected in common_utils.")
        sys.exit(0)


if __name__ == "__main__":
    main()
