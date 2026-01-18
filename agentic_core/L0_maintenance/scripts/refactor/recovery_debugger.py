"""
RECOVERY DEBUGGER: Phantom Agent Locator
Identifies exactly which agents were lost during the L3 extraction.
"""
import ast
from pathlib import Path
from typing import Set, Dict, List

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
from agentic_core.utils.sovereign_index import SovereignIndex
from agentic_core.utils.file_utils import safe_read_file, safe_write_file


def get_agents_from_file(path: Path) -> Set[str]:
    """Extract agent class names from a Python file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content)
            
        agents = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class ends with 'Agent' (our naming convention)
                if node.name.endswith('Agent'):
                    agents.add(node.name)
        
        return agents
    except Exception as e:
        return set()


def find_phantom_agents(backup_dir: str = ".refactor_backups", current_dir: str = ".") -> Dict:
    """
    Compare backup files with current state to find lost agents.
    
    Returns:
        Dict with 'lost', 'gained', and 'analysis' keys
    """
    backup_root = Path(backup_dir)
    current_root = Path(current_dir)
    
    backup_agents: Dict[str, List[Path]] = {}  # agent_name -> [file_paths]
    current_agents: Dict[str, List[Path]] = {}
    
    print("="*80)
    print("RECOVERY DEBUGGER: Scanning for Phantom Agents")
    print("="*80)
    print()
    
    # Scan backups
    print(f"📂 Scanning backups in {backup_dir}...")
    backup_files = list(backup_root.rglob("*.bak"))
    for backup_path in backup_files:
        agents = get_agents_from_file(backup_path)
        for agent in agents:
            if agent not in backup_agents:
                backup_agents[agent] = []
            backup_agents[agent].append(backup_path)
    
    print(f"   Found {len(backup_agents)} unique agents in {len(backup_files)} backup files")
    
    # Scan current state
    print(f"📂 Scanning current state in {current_dir}...")
    current_files = []
    for path in current_root.rglob("*.py"):
        # Skip excluded directories
        if any(skip in str(path) for skip in [
            '.refactor_backups', 'venv', '.venv', 'env', 
            '__pycache__', 'node_modules', ARCHIVES_DIR
        ]):
            continue
        
        current_files.append(path)
        agents = get_agents_from_file(path)
        for agent in agents:
            if agent not in current_agents:
                current_agents[agent] = []
            current_agents[agent].append(path)
    
    print(f"   Found {len(current_agents)} unique agents in {len(current_files)} current files")
    print()
    
    # Calculate differences
    backup_set = set(backup_agents.keys())
    current_set = set(current_agents.keys())
    
    lost = backup_set - current_set
    gained = current_set - backup_set
    
    # Generate report
    print("="*80)
    print("PHANTOM AGENT REPORT")
    print("="*80)
    print()
    
    print(f"📊 SUMMARY")
    print(f"  Backup agents:  {len(backup_set)}")
    print(f"  Current agents: {len(current_set)}")
    print(f"  Lost agents:    {len(lost)}")
    print(f"  Gained agents:  {len(gained)}")
    print()
    
    if lost:
        print("🚨 LOST AGENTS (Present in backup, missing in current)")
        print("-"*80)
        for agent in sorted(lost):
            backup_locations = backup_agents[agent]
            print(f"  ❌ {agent}")
            for loc in backup_locations:
                # Show original file path (remove .bak extension)
                original = str(loc).replace('.bak', '').replace('.refactor_backups\\', '').replace('.refactor_backups/', '')
                print(f"     Was in: {original}")
        print()
    else:
        print("✅ No agents lost")
        print()
    
    if gained:
        print("➕ GAINED AGENTS (New in current, not in backup)")
        print("-"*80)
        for agent in sorted(gained):
            current_locations = current_agents[agent]
            print(f"  ✓ {agent}")
            for loc in current_locations:
                rel_path = loc.relative_to(current_root)
                print(f"     Now in: {rel_path}")
        print()
    
    # Detailed analysis
    if lost:
        print("="*80)
        print("DETAILED ANALYSIS")
        print("="*80)
        print()
        
        for agent in sorted(lost):
            print(f"Agent: {agent}")
            backup_files = backup_agents[agent]
            
            # Check if agent was supposed to be extracted
            print(f"  Backup locations: {len(backup_files)}")
            for bf in backup_files:
                original_name = bf.name.replace('.bak', '')
                print(f"    - {original_name}")
            
            # Check if it exists in any current file
            if agent in current_agents:
                print(f"  ⚠️  Found in current state (shouldn't be in 'lost' list)")
            else:
                print(f"  ❌ Completely missing from current state")
                
                # Check if a file with this agent's name exists
                expected_file = current_root / f"{agent}.py"
                if expected_file.exists():
                    print(f"  📄 File exists: {expected_file}")
                    print(f"     But agent class not found inside (extraction error?)")
                else:
                    print(f"  📄 Expected file doesn't exist: {expected_file}")
            print()
    
    return {
        "lost": lost,
        "gained": gained,
        "backup_count": len(backup_set),
        "current_count": len(current_set),
        "backup_agents": backup_agents,
        "current_agents": current_agents
    }


if __name__ == "__main__":
    results = find_phantom_agents()
    
    if results["lost"]:
        print("="*80)
        print("⚠️  CRITICAL: Agents were deleted during extraction")
        print("   Manual intervention required to restore lost agents")
        print("="*80)
        exit(1)
    else:
        print("="*80)
        print("✅ SUCCESS: No agents lost in comparison")
        print("="*80)
        exit(0)
