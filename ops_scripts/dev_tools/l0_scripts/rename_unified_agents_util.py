"""
Rename Unified agents in L5_safety/unified directory.

Removes "Unified" prefix from file names and class names,
then updates all imports across the codebase.
"""

from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    ARCHIVES_DIR,
    L5_SAFETY_DIR,
    TESTS_DIR,
    get_validated_project_root,
)

PROJECT_ROOT = get_validated_project_root()
RENAMES = {
    "CodeDetectorAgent.py": "CodeDetectorAgent.py",
    "CodeEnforcerAgent.py": "CodeEnforcerAgent.py",
    "CodeHealerAgent.py": "CodeHealerAgent.py",
    "CodeValidatorAgent.py": "CodeValidatorAgent.py",
    "ResourceManagerAgent.py": "ResourceManagerAgent.py",
    "SafetyDetectorAgent.py": "SafetyDetectorAgent.py",
    "SafetyExecutorAgent.py": "SafetyExecutorAgent.py",
    "SecurityManagerAgent.py": "SecurityManagerAgent.py",
    "StructureEnforcerAgent.py": "StructureEnforcerAgent.py",
    "StructureHealerAgent.py": "StructureHealerAgent.py",
}
CLASS_RENAMES = {
    "CodeDetectorAgent": "CodeDetectorAgent",
    "CodeEnforcerAgent": "CodeEnforcerAgent",
    "CodeHealerAgent": "CodeHealerAgent",
    "CodeValidatorAgent": "CodeValidatorAgent",
    "ResourceManagerAgent": "ResourceManagerAgent",
    "SafetyDetectorAgent": "SafetyDetectorAgent",
    "SafetyExecutorAgent": "SafetyExecutorAgent",
    "SecurityManagerAgent": "SecurityManagerAgent",
    "StructureEnforcerAgent": "StructureEnforcerAgent",
    "StructureHealerAgent": "StructureHealerAgent",
}
UNIFIED_DIR = PROJECT_ROOT / L5_SAFETY_DIR / "unified"


def rename_files():
    """Rename the files in the unified directory."""
    for old_name, new_name in RENAMES.items():
        old_path = UNIFIED_DIR / old_name
        new_path = UNIFIED_DIR / new_name
        if old_path.exists():
            old_path.rename(new_path)


def update_class_names_in_unified():
    """Update class names inside the unified directory files."""
    for py_file in UNIFIED_DIR.glob("*.py"):
        if py_file.name == "__pycache__":
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
            original = content
            for old_class, new_class in CLASS_RENAMES.items():
                content = content.replace(old_class, new_class)
            if content != original:
                py_file.write_text(content, encoding="utf-8")
        # guardian: allow-silent-swallow
        except Exception:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            pass


def update_imports_codebase():
    """Update imports across the entire codebase (excluding archives)."""
    scan_dirs = [
        PROJECT_ROOT / AGENTIC_CORE_DIR,
        PROJECT_ROOT / TESTS_DIR,
        PROJECT_ROOT / "scripts",
        PROJECT_ROOT / APPS_RG_DIR,
        PROJECT_ROOT / APPS_SHARED_DIR,
    ]
    files_updated = 0
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for py_file in scan_dir.rglob("*.py"):
            if ARCHIVES_DIR in str(py_file) or "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                original = content
                for old_name, new_name in RENAMES.items():
                    old_module = old_name.replace(".py", "")
                    new_module = new_name.replace(".py", "")
                    content = content.replace(
                        f"from agentic_core.L5_safety.reasoning.{old_module}",
                        f"from agentic_core.L5_safety.reasoning.{new_module}",
                    )
                    content = content.replace(
                        f"import agentic_core.L5_safety.reasoning.{old_module}",
                        f"import agentic_core.L5_safety.reasoning.{new_module}",
                    )
                for old_class, new_class in CLASS_RENAMES.items():
                    content = content.replace(old_class, new_class)
                if content != original:
                    py_file.write_text(content, encoding="utf-8")
                    files_updated += 1
            # guardian: allow-silent-swallow
            except Exception:
                # TODO: Handle specific exception properly
                raise  # Re-raise after logging/handling
                pass


def add_backward_compat_aliases():
    """Add backward compatibility aliases to __init__.py."""
    init_file = UNIFIED_DIR / "__init__.py"
    new_init = '"""\nUnified L5 Safety/Validation Agents\n\n[PHASE 33c UPGRADE 2026-01-21]: Removed "Unified" prefix from agent names.\nBackward compatibility aliases maintained for existing imports.\n\nAgents:\n- CodeValidatorAgent: Single-pass AST validation (syntax, canon, async, print)\n- StructuralValidatorAgent: Gravity, hygiene, registry, contract validation\n- CodeDetectorAgent: Code pattern detection\n- CodeEnforcerAgent: Code pattern enforcement\n- CodeHealerAgent: Code healing operations\n- ResourceManagerAgent: Resource management\n- SafetyDetectorAgent: Safety pattern detection\n- SafetyExecutorAgent: Safety execution\n- SecurityManagerAgent: Security management\n- StructureEnforcerAgent: Structure enforcement\n- StructureHealerAgent: Structure healing\n"""\n\nfrom agentic_core.L5_safety.reasoning.CodeDetectorAgent import CodeDetectorAgent\nfrom agentic_core.L5_safety.reasoning.CodeEnforcerAgent import CodeEnforcerAgent\nfrom agentic_core.L5_safety.reasoning.CodeHealerAgent import CodeHealerAgent\nfrom agentic_core.L5_safety.reasoning.CodeValidatorAgent import (\n    CodeValidatorAgent,\n    RuleSet,\n    ValidationReport,\n    Violation,\n    ViolationType,\n    create_legacy_async_validator,\n    create_legacy_canon_validator,\n    create_legacy_print_validator,\n    create_legacy_syntax_validator,\n)\nfrom agentic_core.L5_safety.reasoning.ResourceManagerAgent import ResourceManagerAgent\nfrom agentic_core.L5_safety.reasoning.SafetyDetectorAgent import SafetyDetectorAgent\nfrom agentic_core.L5_safety.reasoning.SafetyExecutorAgent import SafetyExecutorAgent\nfrom agentic_core.L5_safety.reasoning.SecurityManagerAgent import SecurityManagerAgent\nfrom agentic_core.L5_safety.reasoning.StructuralValidatorAgent_types import (\n    StructuralValidatorAgent,\n    StructureConfig,\n    StructureReport,\n    StructureViolation,\n    StructureViolationType,\n    StructureValidatorAgent,  # Backward compat alias\n    create_legacy_gravity_validator,\n    create_legacy_hygiene_validator,\n    create_legacy_registry_validator,\n)\nfrom agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent\nfrom agentic_core.L5_safety.reasoning.StructureHealerAgent_types import StructureHealerAgent\n\n# Backward compatibility aliases (DEPRECATED - use new names)\nCodeDetectorAgent = CodeDetectorAgent\nCodeEnforcerAgent = CodeEnforcerAgent\nCodeHealerAgent = CodeHealerAgent\nCodeValidatorAgent = CodeValidatorAgent\nResourceManagerAgent = ResourceManagerAgent\nSafetyDetectorAgent = SafetyDetectorAgent\nSafetyExecutorAgent = SafetyExecutorAgent\nSecurityManagerAgent = SecurityManagerAgent\nStructureEnforcerAgent = StructureEnforcerAgent\nStructureHealerAgent = StructureHealerAgent\n\n__all__ = [\n    # New canonical names\n    "CodeDetectorAgent",\n    "CodeEnforcerAgent",\n    "CodeHealerAgent",\n    "CodeValidatorAgent",\n    "ResourceManagerAgent",\n    "SafetyDetectorAgent",\n    "SafetyExecutorAgent",\n    "SecurityManagerAgent",\n    "StructuralValidatorAgent",\n    "StructureEnforcerAgent",\n    "StructureHealerAgent",\n    # Legacy aliases (backward compat - DEPRECATED)\n    "CodeDetectorAgent",\n    "CodeEnforcerAgent",\n    "CodeHealerAgent",\n    "CodeValidatorAgent",\n    "ResourceManagerAgent",\n    "SafetyDetectorAgent",\n    "SafetyExecutorAgent",\n    "SecurityManagerAgent",\n    "StructureEnforcerAgent",\n    "StructureHealerAgent",\n    "StructureValidatorAgent",\n    # Data classes\n    "RuleSet",\n    "ValidationReport",\n    "Violation",\n    "ViolationType",\n    "StructureConfig",\n    "StructureReport",\n    "StructureViolation",\n    "StructureViolationType",\n    # Factory methods\n    "create_legacy_syntax_validator",\n    "create_legacy_canon_validator",\n    "create_legacy_async_validator",\n    "create_legacy_print_validator",\n    "create_legacy_gravity_validator",\n    "create_legacy_hygiene_validator",\n    "create_legacy_registry_validator",\n]\n'
    init_file.write_text(new_init, encoding="utf-8")


if __name__ == "__main__":
    rename_files()
    update_class_names_in_unified()
    update_imports_codebase()
    add_backward_compat_aliases()
