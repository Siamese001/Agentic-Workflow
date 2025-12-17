#!/usr/bin/env python3
"""Finish the refactoring by removing old agents and updating main execution"""

import re
from pathlib import Path

def finish_refactor():
    file_path = Path(__file__).parent / 'canon_validator_agentic.py'
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    original_length = len(content.splitlines())
    
    # Step 1: Remove old concurrency agents
    old_agents = [
        'RaceConditionDetector',
        'LivelockPreventionAgent',
        'StarvationPreventionAgent'
    ]
    
    for agent_name in old_agents:
        # Find the class definition and remove it
        pattern = rf'class {agent_name}\(SubAtomicAgent\):.*?(?=\nclass \w+\(|\nif __name__|$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            print(f"Removing old {agent_name} class (lines {content[:match.start()].count(chr(10))+1}-{content[:match.end()].count(chr(10))+1})...")
            content = content[:match.start()] + content[match.end():]
        else:
            print(f"WARNING: Could not find {agent_name} class")
    
    # Step 2: Update main execution block
    main_block = '''if __name__ == "__main__":
    ctx = ValidationContext()
    
    # Unified Agent Sequence (10 agents instead of 50+)
    agents = [
        Historian(ctx),              # 1. Memory/Skip logic
        ArchitectureGovernor(ctx),   # 2. Architecture governance
        GenerativeGuard(ctx),        # 3. Clean noise
        CodeJanitor(ctx),            # 4. Basic formatting
        DependencySentinel(ctx),     # 5. Imports
        SafetyInspector(ctx),        # 6. Security
        StyleGuardian(ctx),          # 7. Style checks
        ConcurrencyGuardian(ctx),    # 8. Concurrency safety
        BudgetAgent(ctx),            # 9. Complexity budgets
        TheCurator(ctx),             # 10. Final cleanup
    ]

    async def run_mission():
        print("🚀 STARTING UNIFIED AGENTIC MISSION")
        for agent in agents:
            if agent.can_run():
                await agent.execute()
        
        print("\\n" + "="*50)
        print("MISSION COMPLETE")
        print("="*50)

    asyncio.run(run_mission())
'''
    
    # Find and replace the old main block
    old_main_pattern = r'if __name__ == "__main__":.*$'
    content = re.sub(old_main_pattern, main_block, content, flags=re.DOTALL)
    
    # Step 3: Write back
    backup_path = file_path.with_suffix('.py.backup3')
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        with open(backup_path, 'w', encoding='utf-8') as fb:
            fb.write(f.read())
    print(f"\nBackup saved to: {backup_path}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_length = len(content.splitlines())
    reduction = ((original_length - new_length) / original_length) * 100
    
    print(f"\nRefactoring complete!")
    print(f"  Original: {original_length} lines")
    print(f"  New: {new_length} lines")
    print(f"  Reduction: {reduction:.1f}%")
    
    # Step 4: Verify syntax
    try:
        import ast
        ast.parse(content)
        print("\n✅ Syntax check: PASSED")
        return True
    except SyntaxError as e:
        print(f"\n❌ Syntax check: FAILED at line {e.lineno}")
        print(f"   {e.msg}")
        return False

if __name__ == '__main__':
    success = finish_refactor()
    exit(0 if success else 1)
