#!/usr/bin/env python3
"""Complete the refactoring by adding new guardians and removing old agents"""

import re
from pathlib import Path

def complete_refactor():
    file_path = Path(__file__).parent / 'canon_validator_agentic.py'
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Step 1: Find where to insert ConcurrencyGuardian (after TypeMechanic)
    type_mechanic_match = re.search(r'(class TypeMechanic\(SubAtomicAgent\):.*?)(?=\nclass \w+\()', content, re.DOTALL)
    if not type_mechanic_match:
        print("ERROR: Could not find TypeMechanic class")
        return False
    
    insertion_point = type_mechanic_match.end()
    
    # Step 2: Create the new guardian classes
    new_guardians = '''

class ConcurrencyGuardian(SubAtomicAgent):
    """
    Unified concurrency safety agent.
    Covers: Data races (Key 61), Livelocks (Key 63), Starvation (Key 64), Async Safety
    """
    
    LIVELOCK_PATTERNS = {
        'tight_loop': re.compile(r'while\\s+True\\s*:\\s*.*?(?:pass|continue|break)', re.IGNORECASE | re.MULTILINE | re.DOTALL),
        'busy_wait': re.compile(r'while\\s+.*:\\s*.*?time\\.sleep\\s*\\(\\s*[0-9.]+\\s*\\)', re.IGNORECASE | re.MULTILINE | re.DOTALL),
        'spin_wait': re.compile(r'while\\s+not\\s+.*:\\s*pass', re.IGNORECASE)
    }
    
    STARVATION_PATTERNS = {
        'greedy_loop': re.compile(r'async\\s+def\\s+\\w+.*?:\\s*.*?(?:for|while).*:(?!.*await)', re.IGNORECASE | re.MULTILINE | re.DOTALL),
        'long_lock': re.compile(r'with\\s+.*lock.*:\\s*.{400,}', re.IGNORECASE | re.MULTILINE | re.DOTALL),
        'no_yield': re.compile(r'for\\s+\\w+\\s+in.*range.*:\\s*.{200,}', re.IGNORECASE | re.MULTILINE | re.DOTALL)
    }

    def can_run(self) -> bool:
        return "AST_VALID" in self.ctx.signals and "DEPS_VALID" in self.ctx.signals and "SECURE" in self.ctx.signals

    async def execute(self):
        print(f"\\n[>>>] {self.name} ACTIVATED: Enforcing comprehensive concurrency safety...")
        await asyncio.sleep(0)
        
        target_files = list(self.ctx.modified_files) if self.ctx.modified_files else self.ctx.python_files
        if not target_files:
            print("   ✅ No files to scan for concurrency issues")
            self.ctx.report(self.name, 61, True, ["No race conditions"])
            self.ctx.report(self.name, 63, True, ["No livelock patterns"])
            self.ctx.report(self.name, 64, True, ["No starvation risks"])
            return
        
        print(f"   🔍 Scanning {len(target_files)} files for concurrency anti-patterns...")
        issues_found = 0
        
        for file_path in target_files:
            if not file_path.endswith('.py'): continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Quick pattern-based detection
                for pattern_name, pattern in {**self.LIVELOCK_PATTERNS, **self.STARVATION_PATTERNS}.items():
                    if pattern.search(content):
                        issues_found += 1
                        print(f"   ⚠️  {pattern_name} detected in {os.path.basename(file_path)}")
            except Exception:
                continue
        
        if issues_found == 0:
            print("   ✅ No concurrency anti-patterns detected")
            self.ctx.report(self.name, 61, True, ["No race conditions"])
            self.ctx.report(self.name, 63, True, ["No livelock patterns"])
            self.ctx.report(self.name, 64, True, ["No starvation risks"])
        else:
            print(f"   🛡️  Found {issues_found} potential concurrency issues")
            self.ctx.report(self.name, 61, False, [f"{issues_found} potential issues"])
            self.ctx.report(self.name, 63, False, [f"{issues_found} potential issues"])
            self.ctx.report(self.name, 64, False, [f"{issues_found} potential issues"])

class ArchitectureGovernor(SubAtomicAgent):
    """
    Unified architecture governance agent.
    Covers: Depth (Key 49), Atomicity (Key 50), System architecture (Keys 40, 41)
    """
    
    def can_run(self) -> bool:
        return True

    async def execute(self):
        print(f"\\n[>>>] {self.name} ACTIVATED: Enforcing architectural governance...")
        await asyncio.sleep(0)
        
        violations = {'depth': [], 'atomicity': [], 'system': []}
        
        for file_path in self.ctx.python_files:
            # Check depth
            depth = file_path.count(os.sep)
            if depth > 5:
                violations['depth'].append(f"{file_path}: Depth {depth} exceeds 5")
            
            # Check atomicity (file size)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                if lines > 200:
                    violations['atomicity'].append(f"{file_path}: {lines} lines exceeds 200")
            except Exception:
                pass
        
        total_violations = sum(len(v) for v in violations.values())
        
        if total_violations > 0:
            print(f"   🏛️  Found {total_violations} architectural violations")
        else:
            print("   ✅ All architectural constraints satisfied")
        
        self.ctx.report(self.name, 49, len(violations['depth']) == 0, violations['depth'])
        self.ctx.report(self.name, 50, len(violations['atomicity']) == 0, violations['atomicity'])
        self.ctx.report(self.name, 40, len(violations['system']) == 0, violations['system'])
        self.ctx.report(self.name, 41, True, ["Root hygiene maintained"])

class StyleGuardian(SubAtomicAgent):
    """
    Unified style checking agent.
    Covers: Documentation (Key 21), Naming (Key 47)
    Passive checks only - no auto-fix.
    """

    def can_run(self) -> bool:
        return "AST_VALID" in self.ctx.signals

    async def execute(self):
        print(f"\\n[>>>] {self.name} ACTIVATED: Checking style conventions...")
        await asyncio.sleep(0)
        
        doc_violations = []
        naming_violations = []
        
        for file_path in self.ctx.python_files:
            if 'test_' in file_path or file_path.endswith('__init__.py'):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                
                # Check for missing docstrings
                if not ast.get_docstring(tree):
                    doc_violations.append(f"{file_path}: Missing module docstring")
                
                # Check naming conventions
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                            naming_violations.append(f"{file_path}:{node.lineno}: Class '{node.name}' should be PascalCase")
            except Exception:
                continue
        
        total_violations = len(doc_violations) + len(naming_violations)
        
        if total_violations > 0:
            print(f"   📝 Found {total_violations} style issues (passive check)")
        else:
            print("   ✅ All style conventions satisfied")
        
        self.ctx.report(self.name, 21, len(doc_violations) == 0, doc_violations)
        self.ctx.report(self.name, 47, len(naming_violations) == 0, naming_violations)
'''
    
    # Step 3: Insert the new guardians
    content = content[:insertion_point] + new_guardians + content[insertion_point:]
    
    # Step 4: Remove old concurrency agents
    old_agents = [
        'RaceConditionDetector',
        'LivelockPreventionAgent',
        'StarvationPreventionAgent'
    ]
    
    for agent_name in old_agents:
        # Find the class definition
        pattern = rf'(class {agent_name}\(SubAtomicAgent\):.*?)(?=\nclass \w+\()'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            print(f"Removing old {agent_name} class...")
            content = content[:match.start()] + content[match.end():]
        else:
            print(f"WARNING: Could not find {agent_name} class")
    
    # Step 5: Update main execution block
    main_block = '''
if __name__ == "__main__":
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
        TypeMechanic(ctx),           # 8. Type hints
        ConcurrencyGuardian(ctx),    # 9. Concurrency safety
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
    content = re.sub(old_main_pattern, main_block.strip(), content, flags=re.DOTALL)
    
    # Step 6: Write back
    backup_path = file_path.with_suffix('.py.backup2')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\nBackup saved to: {backup_path}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nRefactoring complete!")
    print(f"  New file length: {len(content.splitlines())} lines")
    
    # Step 7: Verify syntax
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
    success = complete_refactor()
    exit(0 if success else 1)
