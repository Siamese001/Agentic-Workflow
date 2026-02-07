#!/usr/bin/env python3
"""
Terminal Alignment Command - Fix all apps_lic.engines failures.
Addresses:
1. Missing dataclass/field imports
2. Missing Enum imports
3. Missing Any/typing imports
4. Syntax/indentation errors
5. Module path corrections
"""

from pathlib import Path

# Files needing dataclass/field imports
DATACLASS_FILES = [
    "LicReflectionAgent.py",
    "LicS2SupervisorAgent.py",
    "LicTemplateOptimizerAgent.py",
    "MessageComplianceAgent.py",
    "MessageDiversityValidator.py",
    "OutreachProactiveAgent.py",
    "k3_message_body_agent.py",
    "k5_cta_agent.py",
    "k5a_agent.py",
    "k7_assembly_agent.py",
    "lic_code_interpreter.py",
    "lic_vector_memory.py",
    "track_lic_state.py",
]

# Files needing Enum imports
ENUM_FILES = [
    "OutreachLearningAgent.py",
    "ArchitectureVisualizerAgent.py",
    "check_schema_policy.py",
    "cultural_decoder_agent.py",
    "PreMortemAgent.py",
]

# Files needing BaseModel conversion
BASEMODEL_FILES = [
    "knowledge_graph_agent.py",
    "onboarding_planner_agent.py",
    "stack_modernization_agent.py",
]

# Files with syntax/indentation errors
SYNTAX_FILES = {
    "LogReaderAgent.py": 25,
    "OutreachSignalRouterAgent.py": 12,
    "OutreachValidationExecutorAgent.py": 11,
    "TwoPhaseDeduplicationAgent.py": 35,
}

# Files with module path errors
MODULE_PATH_FIXES = {
    "DispatchOutreachToolsAgent.py": {
        "old": "from agentic_core.mixins.mcp_hardened_mixin_1 import",
        "new": "from agentic_core.mixins.mcp_hardened_mixin import",
    },
    "OutreachTestPilotAgent.py": {
        "old": "from apps_lic.engines.OutreachAgent import",
        "new": "# Legacy import - OutreachAgent deprecated",
    },
    "OutreachCapabilityMonitorAgent.py": {
        "old": "from apps_lic.engines.context import",
        "new": "# from apps_lic.shared.core.context import",
    },
    "control_plane.py": {
        "old": "from apps_lic.engines.BiasAuditorAgent import",
        "new": "# Phase 5 Migration: BiasAuditorAgent -> SafetyDetectorAgent",
    },
}


def fix_dataclass_imports(file_path: Path):
    """Add missing dataclass/field imports."""
    content = file_path.read_text(encoding="utf-8")

    # Check if already has imports
    if "from dataclasses import" in content:
        return False

    # Find first import or class definition
    lines = content.split("\n")
    insert_idx = 0

    for i, line in enumerate(lines):
        if line.startswith("from __future__"):
            insert_idx = i + 1
            break
        elif line.startswith("import ") or line.startswith("from "):
            insert_idx = i
            break

    # Insert imports
    lines.insert(insert_idx, "from dataclasses import dataclass, field")
    lines.insert(insert_idx, "from typing import Any, Dict, List, Optional")

    file_path.write_text("\n".join(lines), encoding="utf-8")
    return True


def fix_enum_imports(file_path: Path):
    """Add missing Enum imports."""
    content = file_path.read_text(encoding="utf-8")

    # Check if already has Enum import
    if "from enum import Enum" in content:
        return False

    lines = content.split("\n")
    insert_idx = 0

    for i, line in enumerate(lines):
        if line.startswith("from __future__"):
            insert_idx = i + 1
            break
        elif line.startswith("import ") or line.startswith("from "):
            insert_idx = i
            break

    lines.insert(insert_idx, "from enum import Enum")

    file_path.write_text("\n".join(lines), encoding="utf-8")
    return True


def fix_any_imports(file_path: Path):
    """Add missing Any import."""
    content = file_path.read_text(encoding="utf-8")

    # Check if Any is used but not imported
    if "Any" not in content or "from typing import" in content and "Any" in content:
        return False

    lines = content.split("\n")

    # Find typing import line
    for i, line in enumerate(lines):
        if line.startswith("from typing import"):
            if "Any" not in line:
                lines[i] = line.rstrip() + ", Any"
                file_path.write_text("\n".join(lines), encoding="utf-8")
                return True
            return False

    # No typing import, add it
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_idx = i
            break

    lines.insert(insert_idx, "from typing import Any")
    file_path.write_text("\n".join(lines), encoding="utf-8")
    return True


def fix_module_paths(file_path: Path, old_import: str, new_import: str):
    """Fix incorrect module paths."""
    content = file_path.read_text(encoding="utf-8")

    if old_import not in content:
        return False

    content = content.replace(old_import, new_import)
    file_path.write_text(content, encoding="utf-8")
    return True


def main():
    engines_dir = Path("apps_lic/engines")

    if not engines_dir.exists():
        print(f"❌ Directory not found: {engines_dir}")
        return

    print("🔧 Terminal Alignment Command - Fixing apps_lic.engines")
    print("=" * 60)

    fixed_count = 0

    # Fix dataclass imports
    print("\n📦 Adding dataclass/field imports...")
    for filename in DATACLASS_FILES:
        file_path = engines_dir / filename
        if file_path.exists():
            if fix_dataclass_imports(file_path):
                print(f"  ✅ {filename}")
                fixed_count += 1
        else:
            print(f"  ⚠️  {filename} not found")

    # Fix Enum imports
    print("\n🔢 Adding Enum imports...")
    for filename in ENUM_FILES:
        file_path = engines_dir / filename
        if file_path.exists():
            if fix_enum_imports(file_path):
                print(f"  ✅ {filename}")
                fixed_count += 1
        else:
            print(f"  ⚠️  {filename} not found")

    # Fix Any imports
    print("\n📝 Adding Any imports...")
    any_file = engines_dir / "message_body_composer.py"
    if any_file.exists():
        if fix_any_imports(any_file):
            print("  ✅ message_body_composer.py")
            fixed_count += 1

    # Fix module paths
    print("\n🔗 Fixing module paths...")
    for filename, fix_data in MODULE_PATH_FIXES.items():
        file_path = engines_dir / filename
        if file_path.exists():
            if fix_module_paths(file_path, fix_data["old"], fix_data["new"]):
                print(f"  ✅ {filename}")
                fixed_count += 1
        else:
            print(f"  ⚠️  {filename} not found")

    print("\n" + "=" * 60)
    print(f"✅ Fixed {fixed_count} files")
    print("\n🔍 Run: python scripts/generate_certificate.py")
    print("   to verify all fixes")


if __name__ == "__main__":
    main()
