#!/usr/bin/env python3
"""
Batch script to add heal() methods to L5 safety validators.
Phase 5: Safety Validators - Part 1 (L5 - Critical)
"""

from pathlib import Path
import re

# Template for heal() method
HEAL_METHOD_TEMPLATE = '''
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        [HEALER PROTOCOL] Standardized healing interface for {agent_name} violations.
        
        Args:
            violation: Violation dict with keys: type, file, message, etc.
            
        Returns:
            Dict with keys: status, details, artifacts, errors
        """
        try:
            violation_type = violation.get("type", "")
            file_path = violation.get("file")
            
            if not file_path:
                return {{
                    "status": "failed",
                    "details": "No file path provided in violation",
                    "artifacts": [],
                    "errors": ["Missing file path"],
                }}
            
            # {agent_name} healing logic
            return {{
                "status": "manual_required",
                "details": "{agent_name} requires manual review for healing",
                "artifacts": [],
                "errors": [],
            }}
            
        except Exception as e:
            return {{
                "status": "failed",
                "details": "Exception during healing",
                "artifacts": [],
                "errors": [str(e)],
            }}
'''

# List of remaining high-priority L5 validators to update
TARGET_AGENTS = [
    "AutonomyGuardianAgent",
    "CanonDependencySentinelAgent",
    "CartographerAgent",
    "CognitiveDispositionAgent",
    "CompositeGuardrailAgent",
    "ContextCuratorAgent",
    "CredentialScannerAgent",
    "DDDAlignmentAgent",
    "DependencyDiplomatAgent",
    "DocumentationAgent",
    "DynamicSealAgent",
    "GitAgent",
    "GlobalComplianceAggregatorAgent",
    "HealValidatorAgent",
    "HygieneGuardianAgent",
    "MCPGuardianAgent",
    "MemoryArchitectAgent",
]

def add_heal_method_to_agent(file_path: Path, agent_name: str) -> bool:
    """Add heal() method to an agent file if it doesn't already have one."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Check if heal() method already exists
        if re.search(r'def heal\(self,\s*violation:', content):
            print(f"  ✓ {agent_name} already has heal() method")
            return False
        
        # Find the class definition
        class_pattern = rf'class {agent_name}\([^)]+\):'
        class_match = re.search(class_pattern, content)
        
        if not class_match:
            print(f"  ✗ Could not find class definition for {agent_name}")
            return False
        
        # Find the __init__ or __post_init__ method to insert after
        init_pattern = r'(def __(?:post_)?init__\([^)]+\)[^:]*:.*?)(?=\n    def |\n\nclass |\Z)'
        init_match = re.search(init_pattern, content, re.DOTALL)
        
        if init_match:
            insert_pos = init_match.end()
        else:
            # If no __init__, insert after class docstring
            docstring_pattern = rf'(class {agent_name}\([^)]+\):.*?""".*?""")'
            docstring_match = re.search(docstring_pattern, content, re.DOTALL)
            if docstring_match:
                insert_pos = docstring_match.end()
            else:
                # Insert after class definition line
                insert_pos = class_match.end()
        
        # Generate heal() method
        heal_method = HEAL_METHOD_TEMPLATE.format(agent_name=agent_name)
        
        # Insert the method
        new_content = content[:insert_pos] + heal_method + content[insert_pos:]
        
        # Write back
        file_path.write_text(new_content, encoding='utf-8')
        print(f"  ✓ Added heal() method to {agent_name}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error processing {agent_name}: {e}")
        return False

def main():
    """Main execution function."""
    project_root = Path(__file__).parent
    validators_dir = project_root / "agentic_core" / "L5_safety" / "validators"
    
    print("Phase 5: Adding heal() methods to L5 safety validators...")
    print(f"Target directory: {validators_dir}")
    print(f"Agents to process: {len(TARGET_AGENTS)}\n")
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for agent_name in TARGET_AGENTS:
        file_path = validators_dir / f"{agent_name}.py"
        
        if not file_path.exists():
            print(f"  ✗ File not found: {agent_name}.py")
            error_count += 1
            continue
        
        print(f"Processing {agent_name}...")
        result = add_heal_method_to_agent(file_path, agent_name)
        
        if result:
            updated_count += 1
        else:
            skipped_count += 1
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(TARGET_AGENTS)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
