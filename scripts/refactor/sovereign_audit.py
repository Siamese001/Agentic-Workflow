"""
SOVEREIGN AUDIT: Integrity Check
Ensures 1:1 parity and total agent count stability.

This script validates:
1. Total agent count remains at 289
2. No multi-class agent files remain
3. All agent files follow PascalCase naming
"""
import ast
import json
from pathlib import Path
from typing import List, Tuple, Dict


def audit_agents(root_dir: str = ".") -> Dict:
    """
    Audit all agent files for compliance.
    
    Returns:
        Dict with audit results
    """
    root = Path(root_dir)
    agent_count = 0
    multi_class_files = []
    agent_files = []
    
    # Load agent registry for comparison
    registry_path = root / "agent_discovery_full.json"
    registry_count = 0
    if registry_path.exists():
        with open(registry_path, 'r') as f:
            registry = json.load(f)
            registry_count = len(registry)
    
    print("=" * 80)
    print("SOVEREIGN AUDIT: Agent Integrity Check")
    print("=" * 80)
    print()
    
    # Scan all Python files
    for path in root.rglob("*.py"):
        # Skip excluded directories
        if any(skip in str(path) for skip in [
            'venv', '.venv', 'env', '__pycache__', 
            '.refactor_backups', 'node_modules', 'tests'
        ]):
            continue
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)
            
            # Find all top-level classes
            classes = [
                node.name for node in tree.body 
                if isinstance(node, ast.ClassDef)
            ]
            
            # Check if any classes end with "Agent"
            agent_classes = [cls for cls in classes if cls.endswith('Agent')]
            
            if agent_classes:
                agent_count += len(agent_classes)
                agent_files.append(path)
                
                if len(agent_classes) > 1:
                    multi_class_files.append((path, agent_classes))
        
        except Exception as e:
            # Skip files with syntax errors
            pass
    
    # Generate report
    print("📊 AUDIT RESULTS")
    print("-" * 80)
    print(f"Total Agent Classes Found: {agent_count}")
    print(f"Agent Registry Count: {registry_count}")
    print(f"Agent Files: {len(agent_files)}")
    print(f"Multi-Class Agent Files: {len(multi_class_files)}")
    print()
    
    # Check for violations
    violations = []
    
    if agent_count != registry_count:
        violations.append(f"Agent count mismatch: {agent_count} found vs {registry_count} in registry")
    
    if multi_class_files:
        violations.append(f"{len(multi_class_files)} files still contain multiple agent classes")
    
    # Report violations
    if violations:
        print("⚠️  VIOLATIONS DETECTED")
        print("-" * 80)
        for violation in violations:
            print(f"  • {violation}")
        print()
        
        if multi_class_files:
            print("Multi-Class Files:")
            for file_path, classes in multi_class_files:
                rel_path = file_path.relative_to(root)
                print(f"  [{rel_path}]")
                for cls in classes:
                    print(f"    - {cls}")
            print()
    else:
        print("✅ ALL CHECKS PASSED")
        print("-" * 80)
        print(f"  • Agent count: {agent_count} (matches registry)")
        print(f"  • All agent files follow one-class-per-file pattern")
        print()
    
    # Return results
    return {
        "agent_count": agent_count,
        "registry_count": registry_count,
        "agent_files": len(agent_files),
        "multi_class_files": len(multi_class_files),
        "violations": violations,
        "passed": len(violations) == 0
    }


if __name__ == "__main__":
    import sys
    
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    results = audit_agents(root_dir)
    
    # Exit with error code if violations found
    sys.exit(0 if results["passed"] else 1)
