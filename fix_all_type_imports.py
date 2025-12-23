"""
Fix all missing type imports in agentic_core implementation files.
Adds proper imports from corresponding *_types.py files.
"""
import re
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

# Map of implementation files to their required type imports
TYPE_IMPORT_FIXES = {
    "agent_gym_impl.py": {
        "module": "agentic_core.L3_orchestration.training.agent_gym_types",
        "types": ["GoldenStateEvaluator", "JudgeEvaluator", "TrainingScenario", "BenchmarkResult", "PerformanceMetrics"]
    },
}

def fix_type_imports():
    print("[*] FIXING ALL TYPE IMPORTS...")
    fixed = 0
    
    for impl_file, config in TYPE_IMPORT_FIXES.items():
        # Find all instances of this file
        for py_file in CORE.rglob(impl_file):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if import already exists
                if f"from {config['module']}" in content:
                    print(f"  [SKIP] {py_file.relative_to(CORE)} - already has imports")
                    continue
                
                # Find the import section (after initial imports, before first class)
                import_pattern = r"(import logging\s+from typing[^\n]+\s+)"
                
                # Build the import statement
                types_str = ", ".join(config['types'])
                new_import = f"from {config['module']} import {types_str}\n\n"
                
                # Insert after logging imports
                if "LOGGER = logging.getLogger" in content:
                    content = content.replace(
                        "LOGGER = logging.getLogger(__name__)",
                        f"from {config['module']} import {types_str}\n\nLOGGER = logging.getLogger(__name__)"
                    )
                else:
                    # Insert after typing imports
                    content = re.sub(
                        r"(from typing import[^\n]+\n)",
                        f"\\1{new_import}",
                        content
                    )
                
                # Remove commented star import if present
                content = re.sub(r"# from \.\w+_types import \*.*\n", "", content)
                
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"  [✓] Fixed: {py_file.relative_to(CORE)}")
                fixed += 1
                
            except Exception as e:
                print(f"  [!] Error fixing {py_file.name}: {e}")
    
    print(f"\n[OK] Fixed {fixed} files")

if __name__ == "__main__":
    fix_type_imports()
