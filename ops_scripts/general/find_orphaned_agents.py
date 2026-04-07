"""
Find Orphaned Agents - Agents flagged for consolidation but never deleted.

Scans the consolidation reports and checks if flagged agents still exist
in the active codebase (not in archives).
"""
import json
import re
from pathlib import Path

PROJECT_ROOT = Path('C:/Git/Agentic-Workflow')
FLAGGED_AGENTS = ['BareExceptValidatorAgent.py', 'DangerousBuiltinsValidatorAgent.py', 'DebuggerValidatorAgent.py', 'EmptyExceptValidatorAgent.py', 'EvalExecValidatorAgent.py', 'AutonomousCheckpointManagerAgent.py', 'AutonomousStateGuardianAgent.py', 'CheckpointManagerAgent.py', 'L4Agent.py', 'ManifestManagerAgent.py', 'MemoryManagerAgent.py', 'BaseClassEnforcerAgent.py', 'HygieneGuardianAgent.py', 'HygieneValidatorAgent.py', 'PatternEnforcerAgent.py', 'TypeHintEnforcementAgent.py']

def find_orphaned_agents():
    """Find agents that were flagged but still exist in active codebase."""
    orphaned = []
    for agent_file in FLAGGED_AGENTS:
        for path in PROJECT_ROOT.rglob(agent_file):
            if any(skip in str(path) for skip in [ARCHIVES_DIR, '.sovereign_healing_backup', '__pycache__']):
                continue
            is_used = check_if_used(path, agent_file)
            orphaned.append({'file': agent_file, 'path': str(path.relative_to(PROJECT_ROOT)), 'absolute_path': str(path), 'is_used': is_used, 'action': 'KEEP' if is_used else 'DELETE'})
    return orphaned

def check_if_used(file_path, agent_file):
    """Check if agent is actually used (imported or inherited from)."""
    agent_class = agent_file.replace('.py', '')
    import_pattern = f'from.*{agent_class} import|import.*{agent_class}'
    inheritance_pattern = f'class.*\\({agent_class}\\)'
    for py_file in PROJECT_ROOT.rglob('*.py'):
        if any(skip in str(py_file) for skip in [ARCHIVES_DIR, '.sovereign_healing_backup', '__pycache__']):
            continue
        if py_file == file_path:
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            if re.search(import_pattern, content) or re.search(inheritance_pattern, content):
                return True
        # guardian: allow-silent-swallow
        except Exception:
            continue
    return False
if __name__ == '__main__':
    print('=' * 80)
    print('ORPHANED AGENT SCAN')
    print('=' * 80)
    print()
    orphaned = find_orphaned_agents()
    if not orphaned:
        print('✅ No orphaned agents found - all flagged agents have been removed.')
    else:
        print(f'Found {len(orphaned)} agents flagged for consolidation:\n')
        to_delete = [a for a in orphaned if a['action'] == 'DELETE']
        to_keep = [a for a in orphaned if a['action'] == 'KEEP']
        if to_delete:
            print(f'🗑️  {len(to_delete)} ORPHANED (safe to delete):')
            for agent in to_delete:
                print(f"  - {agent['file']}")
                print(f"    Path: {agent['path']}")
                print(f"    Used: {agent['is_used']}")
                print()
        if to_keep:
            print(f'⚠️  {len(to_keep)} STILL IN USE (do not delete):')
            for agent in to_keep:
                print(f"  - {agent['file']}")
                print(f"    Path: {agent['path']}")
                print()
        results_file = PROJECT_ROOT / 'orphaned_agents_report.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(orphaned, f, indent=2)
        print(f'\n📄 Full report saved to: {results_file}')
