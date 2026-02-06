r"""
File: scripts/discover_agents.py
Path: C:\Git\Agentic-Workflow\scripts\discover_agents.py
Status: Post-Migration Validation Tool
Rationale:
    Referenced in DEPLOYMENT_PROTOCOL.md.
    This script verifies that the "Pascal Sovereignty" migration was successful by:
    1. Finding all files ending in 'Agent.py'.
    2. attempting to import them (verifying paths/imports are healthy).
    3. Confirming the internal class name matches the filename.
"""

import ast
import importlib.util
import sys
from pathlib import Path

# Ensure repo root is in sys.path
REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L5_safety.validators.structure_blueprint_config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.utils.ssot_discovery_validator import get_python_files


class SovereigntyAuditor:
    def __init__(self):
        self.agents_found = 0
        self.import_failures = []
        self.naming_violations = []

    def audit_file(self, path: Path):
        # 1. Check File Name Compliance
        if not path.name.endswith("Agent.py"):
            return

        self.agents_found += 1
        module_name = path.stem

        # 2. Structural/AST Check (Static Analysis)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

            # Rule: Primary class must match filename
            if module_name not in classes:
                self.naming_violations.append(
                    f"{path.name}: Expected class '{module_name}' not found. Found: {classes}",
                )
        except Exception as e:
            self.naming_violations.append(f"{path.name}: AST Parse Error - {e}")

        # 3. Runtime Import Check (Dynamic Analysis)
        # This confirms that all imports INSIDE the agent file are valid after migration
        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
        except ImportError as e:
            self.import_failures.append(f"{path.name}: {e}")
        except Exception as e:
            # Catch runtime errors during module init (e.g. missing env vars)
            # We log but strictly speaking only ImportErrors confirm "orphaned imports"
            self.import_failures.append(f"{path.name}: Runtime Error - {e}")

    def run(self):
        print("=" * 60)
        print("PASCAL SOVEREIGNTY: POST-MIGRATION AUDIT")
        print("=" * 60)

        target_dirs = [REPO_ROOT / d for d in [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]]

        # Use SSOT discovery if available, else fallback
        files = []
        for d in target_dirs:
            if d.exists():
                files.extend(get_python_files(d))

        print(f"Scanning {len(files)} files for Agents...")

        for f in files:
            self.audit_file(f)

        print("\n" + "=" * 60)
        print(f"Agents Found: {self.agents_found}")
        print(f"Naming Violations: {len(self.naming_violations)}")
        print(f"Import Failures:   {len(self.import_failures)}")

        if self.naming_violations:
            print("\n[!] NAMING VIOLATIONS (Class name != Filename):")
            for v in self.naming_violations:
                print(f"  - {v}")

        if self.import_failures:
            print("\n[!] IMPORT FAILURES (Broken References):")
            for f in self.import_failures:
                print(f"  - {f}")

        # Exit code 1 if critical failures found
        if self.import_failures:
            sys.exit(1)

        print("\n[PASS] Architecture Integrity Verified.")
        sys.exit(0)


if __name__ == "__main__":
    SovereigntyAuditor().run()
