"""
Sovereign Guardian: DDD Alignment
Enforces Bounded Contexts and Aggregate Root access.
"""
import ast
from pathlib import Path
from typing import List, Tuple
from agentic_core.L1_cognition.P2_domain.sovereign_domain_constitution import BOUNDED_CONTEXTS, UBIQUITOUS_LANGUAGE

def check_bounded_contexts(filepath: Path) -> List[str]:
    issues = []
    file_str = str(filepath).replace("\\", "/")
    
    # Determine current context - Phase 10 Constitution Update (Dict[str, Dict])
    # BOUNDED_CONTEXTS is now {Name: {"path": "...", "rank": X}}
    current_context = next(
        (ctx for ctx, info in BOUNDED_CONTEXTS.items() if info.get("path") in file_str), 
        None
    )
    if not current_context: return [] # Skip files outside mapped contexts

    # Standard library modules to exclude from DDD checks
    stdlib_modules = {
        'pathlib', 'os', 'sys', 'json', 'logging', 'typing', 'datetime', 
        'collections', 'itertools', 'functools', 're', 'asyncio', 'abc',
        'dataclasses', 'enum', 'copy', 'io', 'time', 'uuid', 'hashlib'
    }

    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                # Skip standard library imports
                module_root = node.module.split('.')[0]
                if module_root in stdlib_modules:
                    continue
                
                # Phase 9A: Allow SharedContracts imports (neutral interface layer)
                if "apps_shared.base_agents" in node.module:
                    continue  # SharedContracts are allowed across all contexts
                
                # Check for illegal cross-context imports
                for ctx, info in BOUNDED_CONTEXTS.items():
                    if ctx == current_context: continue
                    if ctx == "SharedContracts": continue
                    
                    target_path = info.get("path", "")
                    if target_path.replace("/", ".") in node.module:
                        # Allow imports from contracts/interfaces, flag logic imports
                        if "contracts" not in node.module and "interfaces" not in node.module:
                            issues.append(f"Potential Context Violation: Importing {ctx} logic ({node.module}) into {current_context}")
    except Exception:
        pass
    return issues

def validate_ddd_alignment(target_dir: str) -> Tuple[float, List[str]]:
    issues = []
    total_files = 0
    
    for path in Path(target_dir).rglob("*.py"):
        if "tests" in str(path): continue
        total_files += 1
        # Use full path instead of just filename
        issues.extend([f"{str(path)}: {i}" for i in check_bounded_contexts(path)])

    score = 100.0
    if issues:
        score = max(0, 100 - (len(issues) * 2)) # Deduction per violation
    
    return score, issues
