#!/usr/bin/env python3
"""
Migrate plain Agent classes to inherit from SovereignBaseAgent.

This script targets agents that don't have any mixin inheritance but need
to be brought into the Sovereign architecture.
"""

import ast
import subprocess
from pathlib import Path

# Target files that need migration (plain classes without SovereignBaseAgent)
TARGET_FILES = [
    "agentic_core/L5_safety/unified/UnifiedCodeDetectorAgent.py",
    "agentic_core/L5_safety/unified/UnifiedCodeEnforcerAgent.py",
    "agentic_core/L5_safety/unified/UnifiedResourceManagerAgent.py",
    "agentic_core/L5_safety/unified/UnifiedSafetyDetectorAgent.py",
    "agentic_core/L5_safety/unified/UnifiedSafetyExecutorAgent.py",
    "agentic_core/L5_safety/unified/UnifiedSecurityManagerAgent.py",
    "agentic_core/L5_safety/unified/UnifiedStructureEnforcerAgent.py",
    "agentic_core/L5_safety/unified/UnifiedStructureHealerAgent.py",
    "agentic_core/L5_safety/unified/SSOTFolderCleanupAgent.py",
    "agentic_core/L5_safety/unified/StructureEnforcerAgent.py",
    "agentic_core/L5_safety/unified/StructureHealerAgent.py",
    "agentic_core/L2_execution/unified/UnifiedModelRouterAgent.py",
    "agentic_core/L3_orchestration/UnifiedOrchestratorAgent.py",
    "agentic_core/L3_orchestration/workflow_engines/ErrorHandlerAgent.py",
    "agentic_core/L5_safety/cognition/CognitiveDispositionAgent.py",
    "agentic_core/L5_safety/validators/LocationValidatorAgent.py",
    "agentic_core/L6_observability/dashboards/DashboardHandlerAgent.py",
    "agentic_core/observability/TelemetryManagerAgent.py",
    "agentic_core/utils/core_extensions/ErrorRecoveryManagerAgent.py",
]

SOVEREIGN_IMPORT = "from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent"


def migrate_file(file_path: Path) -> bool:
    """Migrate a single file to inherit from SovereignBaseAgent."""
    if not file_path.exists():
        print(f"  ⚠️  File not found: {file_path}")
        return False

    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Check if already has SovereignBaseAgent
        if "SovereignBaseAgent" in content:
            print("  ℹ️  Already has SovereignBaseAgent")
            return True

        # Parse AST to find class definitions
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"  ❌ Syntax error: {e}")
            return False

        # Find Agent classes
        agent_classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                # Check if it's a plain class (no bases or only dataclass-like bases)
                has_sovereign = False
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "SovereignBaseAgent":
                        has_sovereign = True
                if not has_sovereign:
                    agent_classes.append(node.name)

        if not agent_classes:
            print("  ℹ️  No plain Agent classes found")
            return True

        lines = content.split("\n")

        # Step 1: Add import after other imports
        import_added = False
        for i, line in enumerate(lines):
            if line.strip().startswith("from ") or line.strip().startswith("import "):
                continue
            elif (
                line.strip()
                and not line.strip().startswith("#")
                and not line.strip().startswith('"""')
                and not line.strip().startswith("'''")
            ):
                # Found first non-import line
                if not import_added:
                    # Find last import line before this
                    insert_idx = i
                    for j in range(i - 1, -1, -1):
                        if lines[j].strip().startswith("from ") or lines[j].strip().startswith(
                            "import "
                        ):
                            insert_idx = j + 1
                            break
                    lines.insert(insert_idx, SOVEREIGN_IMPORT)
                    import_added = True
                break

        # Step 2: Update class definitions
        modified_content = "\n".join(lines)

        for class_name in agent_classes:
            # Pattern: class ClassName: or class ClassName():
            modified_content = modified_content.replace(
                f"class {class_name}:", f"class {class_name}(SovereignBaseAgent):"
            )
            modified_content = modified_content.replace(
                f"class {class_name}():", f"class {class_name}(SovereignBaseAgent):"
            )

        # Write back
        file_path.write_text(modified_content, encoding="utf-8")

        # Verify compilation
        result = subprocess.run(
            ["python", "-m", "py_compile", str(file_path)], capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"  ❌ Compilation failed: {result.stderr}")
            file_path.write_text(original_content, encoding="utf-8")
            print("  ↩️  Reverted")
            return False

        print(f"  ✅ Migrated: {', '.join(agent_classes)}")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    print("\n" + "=" * 70)
    print("PLAIN CLASS MIGRATION TO SOVEREIGN BASE")
    print("=" * 70 + "\n")

    success = 0
    failed = 0

    for file_str in TARGET_FILES:
        file_path = Path(file_str)
        print(f"📄 {file_path}")

        if migrate_file(file_path):
            success += 1
        else:
            failed += 1

    print("\n" + "=" * 70)
    print(f"MIGRATION COMPLETE: {success} succeeded, {failed} failed")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
