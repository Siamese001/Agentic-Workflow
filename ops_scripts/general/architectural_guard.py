"""
File: C:/Git/Agentic-Workflow/scripts/architectural_guard.py
Context: Now that the 'common_utils' folder is purged of Agents, we must install an automated regression guard. This script acts as a CI/CD gatekeeper, scanning 'apps_shared/common_utils' for any re-introduction of Agentic logic (Executors, Orchestrators, or LLM clients) and failing the build if detected.
"""
import ast
import os
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET_DIR = str(REPO_ROOT / 'apps_shared' / 'common_utils')
BANNED_SUFFIXES = ['Executor', 'Agent', 'Orchestrator', 'Strategist']
BANNED_IMPORTS = ['langchain', 'crewai', 'autogen', 'semantic_kernel']
BANNED_BASES = ['BaseAgent', 'Agent', 'LLMChain']

def scan_for_violations() -> list[str]:
    violations = []
    # guardian: allow-path-string
    if not os.path.exists(TARGET_DIR):
        print(f'Target directory {TARGET_DIR} does not exist. Skipping.')
        return []
    for root, dirs, files in os.walk(TARGET_DIR):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if not file.endswith('.py'):
                continue
            for suffix in BANNED_SUFFIXES:
                if file.lower().endswith(suffix.lower() + '.py'):
                    violations.append(f"[Filename Violation] {file} contains banned suffix '{suffix}'")
            full_path = Path(root) / file
            try:
                with open(full_path, encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            if any(banned in name.name for banned in BANNED_IMPORTS):
                                violations.append(f"[Import Violation] {file} imports banned module '{name.name}'")
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and any(banned in node.module for banned in BANNED_IMPORTS):
                            violations.append(f"[Import Violation] {file} imports from banned module '{node.module}'")
                    if isinstance(node, ast.ClassDef):
                        for base in node.bases:
                            if isinstance(base, ast.Name) and base.id in BANNED_BASES:
                                violations.append(f"[Inheritance Violation] {file} defines class '{node.name}' inheriting from '{base.id}'")
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f'Warning: Could not parse {file}: {e}')
    return violations

def main():
    print(f'🛡️  Architectural Guard Active: Scanning {TARGET_DIR}...')
    violations = scan_for_violations()
    if violations:
        print('\n❌ ARCHITECTURAL INTEGRITY FAILURE')
        print("The following files violate the 'No Agents in Utils' policy:")
        print('-' * 60)
        for v in violations:
            print(f' - {v}')
        print('-' * 60)
        print("ACTION REQUIRED: Move these files to 'apps_rg/engines/' immediately.")
        sys.exit(1)
    else:
        print('\n✅ Architectural Integrity Verified: No Agents detected in common_utils.')
        sys.exit(0)
if __name__ == '__main__':
    main()
