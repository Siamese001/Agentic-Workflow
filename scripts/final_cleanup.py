#!/usr/bin/env python3
"""Final cleanup - delete old concurrency agents and update main execution"""

import re
from pathlib import Path

def final_cleanup():
    file_path = Path(__file__).parent / 'canon_validator_agentic.py'
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    original_length = len(lines)
    print(f"Original file: {original_length} lines")
    
    # Step 1: Find exact line ranges for each old agent class
    class_starts = {}
    class_pattern = re.compile(r'^class (\w+)\(')
    
    for i, line in enumerate(lines):
        match = class_pattern.match(line)
        if match:
            class_name = match.group(1)
            class_starts[class_name] = i
    
    # Find the 3 old agents to delete
    agents_to_delete = ['RaceConditionDetector', 'LivelockPreventionAgent', 'StarvationPreventionAgent']
    deletion_ranges = []
    
    for agent_name in agents_to_delete:
        if agent_name in class_starts:
            start_line = class_starts[agent_name]
            
            # Find the end (next class definition)
            end_line = len(lines)
            for class_name, class_line in class_starts.items():
                if class_line > start_line and class_line < end_line:
                    end_line = class_line
            
            deletion_ranges.append((agent_name, start_line, end_line))
            print(f"Found {agent_name}: lines {start_line+1}-{end_line}")
    
    # Step 2: Delete in reverse order to preserve line numbers
    deletion_ranges.sort(key=lambda x: x[1], reverse=True)
    
    for agent_name, start, end in deletion_ranges:
        print(f"Deleting {agent_name} (lines {start+1}-{end})...")
        del lines[start:end]
    
    # Step 3: Update main execution block
    # Find the main block
    main_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith('if __name__ == "__main__":'):
            main_start = i
            break
    
    if main_start is not None:
        print(f"Updating main execution block at line {main_start+1}...")
        
        # Delete old main block
        del lines[main_start:]
        
        # Add new main block
        new_main = '''if __name__ == "__main__":
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
        lines.append(new_main)
    
    # Step 4: Write back
    backup_path = file_path.with_suffix('.py.backup_final')
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        with open(backup_path, 'w', encoding='utf-8') as fb:
            fb.write(f.read())
    print(f"\nBackup saved to: {backup_path}")
    
    content = ''.join(lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_length = len(lines)
    reduction = ((original_length - new_length) / original_length) * 100
    
    print(f"\n✅ Refactoring complete!")
    print(f"  Original: {original_length} lines")
    print(f"  New: {new_length} lines")
    print(f"  Reduction: {reduction:.1f}%")
    
    # Step 5: Verify syntax
    try:
        import ast
        ast.parse(content)
        print("\n✅ Syntax check: PASSED")
        
        # Verify old agents are gone
        old_agents = ['RaceConditionDetector', 'LivelockPreventionAgent', 'StarvationPreventionAgent']
        for agent in old_agents:
            if f'class {agent}(' in content:
                print(f"⚠️  WARNING: {agent} still present!")
                return False
        
        # Verify new guardians exist
        new_guardians = ['ConcurrencyGuardian', 'ArchitectureGovernor', 'StyleGuardian']
        for guardian in new_guardians:
            if f'class {guardian}(' not in content:
                print(f"⚠️  WARNING: {guardian} not found!")
                return False
        
        print("\n✅ All old agents removed")
        print("✅ All new guardians present")
        return True
        
    except SyntaxError as e:
        print(f"\n❌ Syntax check: FAILED at line {e.lineno}")
        print(f"   {e.msg}")
        return False

if __name__ == '__main__':
    success = final_cleanup()
    exit(0 if success else 1)
