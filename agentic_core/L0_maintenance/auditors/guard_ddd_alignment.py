"""
Sovereign Guardian: DDD Alignment
Enforces Bounded Contexts and Aggregate Root access.
"""
import ast
from pathlib import Path
from typing import List, Tuple
from agentic_core.domain.sovereign_domain_constitution import BOUNDED_CONTEXTS, UBIQUITOUS_LANGUAGE

def check_bounded_contexts(filepath: Path) -> List[str]:
    issues = []
    file_str = str(filepath).replace("\\", "/")
    
    # Determine current context
    current_context = next((ctx for ctx, paths in BOUNDED_CONTEXTS.items() if any(p in file_str for p in paths)), None)
    if not current_context: return [] # Skip files outside mapped contexts

    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                # Phase 9A: Allow SharedContracts imports (neutral interface layer)
                if "apps_shared.base_agents" in node.module:
                    continue  # SharedContracts are allowed across all contexts
                
                # Check for illegal cross-context imports
                for ctx, paths in BOUNDED_CONTEXTS.items():
                    if ctx == current_context: continue
                    if ctx == "SharedContracts": continue  # SharedContracts can be imported anywhere
                    
                    if any(p.replace("/", ".") in node.module for p in paths):
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
        issues.extend([f"{path.name}: {i}" for i in check_bounded_contexts(path)])

    score = 100.0
    if issues:
        score = max(0, 100 - (len(issues) * 2)) # Deduction per violation
    
    return score, issues
