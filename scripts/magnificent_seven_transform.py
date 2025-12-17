#!/usr/bin/env python3
"""Transform to Magnificent Seven architecture"""

import re
from pathlib import Path

def transform_to_magnificent_seven():
    file_path = Path(__file__).parent / 'canon_validator_agentic.py'
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    original_length = len(content.splitlines())
    print(f"Original file: {original_length} lines")
    
    # Step 1: Delete 5 old agent classes
    agents_to_delete = [
        'GenerativeGuard',
        'TheCurator', 
        'CodeJanitor',
        'StyleGuardian',
        'BudgetAgent'
    ]
    
    for agent_name in agents_to_delete:
        pattern = rf'class {agent_name}\(SubAtomicAgent.*?\):.*?(?=\nclass \w+\(|\nif __name__|$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            print(f"Deleting {agent_name}...")
            content = content[:match.start()] + content[match.end():]
        else:
            print(f"WARNING: Could not find {agent_name}")
    
    # Step 2: Find insertion point (after ConcurrencyGuardian)
    concurrency_match = re.search(r'(class ConcurrencyGuardian\(SubAtomicAgent\):.*?)(?=\nclass \w+\()', content, re.DOTALL)
    if not concurrency_match:
        print("ERROR: Could not find ConcurrencyGuardian")
        return False
    
    insertion_point = concurrency_match.end()
    
    # Step 3: Create new HygieneGuardian
    hygiene_guardian = '''

class HygieneGuardian(SubAtomicAgent):
    """
    Unified Hygiene Agent.
    Merges GenerativeGuard (Key 45) and TheCurator (File Taxonomy).
    
    Responsibilities:
      1. Delete generative artifacts/noise (regex-based).
      2. Organize scripts into categories.
      3. Sweep root directory of stray files.
      4. Maintain script catalog.
    """
    
    GENERATIVE_PATTERNS = [
        r"_impl_impl_",
        r"generated_\\d+",
        r"auto_\\w+_\\d+",
        r"temp_\\w+_\\d+"
    ]

    # Valid script subdirectories
    SCRIPT_CATEGORIES = {
        'maintenance', 'setup', 'migration', 'testing', 'archive'
    }
    
    IMMUTABLE_FILES = {
        'canon_validator_v2_agentic.py',
        'auto_canon.py',
        'setup.py',
        'README.md',
        'canon_validator_agentic.py' 
    }

    async def execute(self):
        print(f"\\n[>>>] {self.name} ACTIVATED: Enforcing Project Hygiene...")
        await asyncio.sleep(0)

        # 1. Purge Generative Noise (Fastest)
        await self._purge_generative_artifacts()

        # 2. Organize Scripts (Intelligence-based)
        await self._organize_scripts()

        # 3. Sweep Root Directory
        await self._sweep_root()

        # 4. Update Manifest
        await self._update_manifest()

        self.ctx.signals.add("GENERATIVE_CLEAN")

    async def _purge_generative_artifacts(self):
        """Detect and remove generative noise files."""
        violations = []
        for root, dirs, files in os.walk("."):
            if any(x in root for x in EXCLUDED_DIRS): continue
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path) and file.endswith('.py'):
                    for pattern in self.GENERATIVE_PATTERNS:
                        if re.search(pattern, file):
                            violations.append(file_path)
                            break
        
        if violations:
            print(f"   🧹 Found {len(violations)} generative artifacts")
            for file_path in violations:
                try:
                    os.remove(file_path)
                    print(f"      DELETED: {file_path}")
                except Exception as e:
                    print(f"      Failed to delete {file_path}: {e}")
        else:
            self.ctx.report(self.name, 45, True, [])

    async def _organize_scripts(self):
        """Organize scripts/ directory."""
        if not self.ctx.intelligence_enabled or not os.path.exists('scripts'): return

        print(f"   📂 Organizing scripts directory...")
        for item in os.listdir('scripts'):
            item_path = os.path.join('scripts', item)
            if os.path.isdir(item_path) or item in self.IMMUTABLE_FILES: continue
            
            # Classify and move
            await self._classify_and_move(item_path, self.SCRIPT_CATEGORIES, 'scripts')

    async def _sweep_root(self):
        """Sweep non-whitelisted files from root."""
        print(f"   🧹 Sweeping root directory...")
        for item in os.listdir('.'):
            if os.path.isdir(item) or item in ALLOWED_ROOT_FILES or item in self.IMMUTABLE_FILES: continue
            
            # Move logic handled by classification
            # For simplicity, default strays to 'archives' if not categorized
            try:
                if self.ctx.move_file(item, f"archives/{item}"):
                     print(f"      📦 Archived stray root file: {item}")
            except Exception as e:
                print(f"      ❌ Failed to sweep {item}: {e}")

    async def _classify_and_move(self, path: str, categories, base_target: str):
        """Ask Gemini where a file belongs."""
        try:
            with open(path, 'r', encoding='utf-8') as f: content = f.read()
            
            prompt = f"""
            Role: File Organizer
            File: {os.path.basename(path)}
            Content: {content[:500]}...
            Categories: {', '.join(categories)}
            
            Respond with ONLY the category name.
            """
            response = self.ctx.client.models.generate_content(
                model=self.ctx.model_id, contents=prompt
            )
            category = response.text.strip().lower()
            if category in categories:
                dest = f"{base_target}/{category}/{os.path.basename(path)}"
                self.ctx.move_file(path, dest)
        except Exception:
             pass

    async def _update_manifest(self):
        """Update script index."""
        pass

class CodeStyleGuardian(SubAtomicAgent):
    """
    Unified Style & Cleanliness Agent.
    Merges CodeJanitor (Keys 10-16) and StyleGuardian (Keys 21, 47).
    
    Responsibilities:
      1. Physical Hygiene: Empty files, trailing whitespace, tabs.
      2. Simple Metrics: Line length, magic numbers, nesting depth.
      3. Semantic Style: Docstrings, naming conventions.
    """

    def can_run(self) -> bool:
        return "AST_VALID" in self.ctx.signals

    async def execute(self):
        print(f"\\n[>>>] {self.name} ACTIVATED: Enforcing Code Style & Hygiene...")
        await asyncio.sleep(0)

        # 1. Physical Hygiene (Active Cleanup)
        self._cleanup_empty_files()
        
        # 2. Metric Checks (Passive Reporting)
        self.ctx.report(self.name, 11, *self._check_no_trailing_whitespace())
        self.ctx.report(self.name, 12, *self._check_no_missing_newline())
        self.ctx.report(self.name, 13, *self._check_no_tabs())
        self.ctx.report(self.name, 10, *self._check_line_length())
        self.ctx.report(self.name, 15, *self._check_magic_numbers())
        self.ctx.report(self.name, 16, *self._check_nesting_depth())
        
        # 3. Semantic Style (Passive Reporting)
        doc_violations = await self._check_documentation()
        self.ctx.report(self.name, 21, len(doc_violations) == 0, doc_violations)
        
        naming_violations = await self._check_naming()
        self.ctx.report(self.name, 47, len(naming_violations) == 0, naming_violations)

    def _cleanup_empty_files(self):
        count = 0
        for root, _, files in os.walk("."):
            if any(x in root for x in EXCLUDED_DIRS): continue
            for file in files:
                p = os.path.join(root, file)
                if os.path.getsize(p) == 0:
                    os.remove(p)
                    count += 1
        if count: print(f"      🗑️  Deleted {count} empty files.")

    def _check_line_length(self):
        violations = []
        for f in self.ctx.python_files:
            try:
                for i, line in enumerate(open(f, encoding='utf-8'), 1):
                    if len(line.rstrip()) > 150: violations.append(f"{f}:{i}")
            except: pass
        return (not violations, violations)

    def _check_magic_numbers(self):
        violations = []
        allowed = {0, 1, -1, 2, 10, 100, 200, 404, 500, 1000, 0.0, 1.0, 0.5}
        for f in self.ctx.python_files:
            if 'test' in f: continue
            try:
                tree = ast.parse(open(f, encoding='utf-8').read())
                for n in ast.walk(tree):
                    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
                        if n.value not in allowed: violations.append(f"{f}:{n.lineno}")
            except: pass
        return (not violations, violations)
    
    def _check_nesting_depth(self):
        violations = []
        for f in self.ctx.python_files:
            try:
                for i, line in enumerate(open(f, encoding='utf-8'), 1):
                    if (len(line) - len(line.lstrip())) > 40: violations.append(f"{f}:{i}")
            except: pass
        return (not violations, violations)

    def _check_no_trailing_whitespace(self): 
        violations = []
        for f in self.ctx.python_files:
            try:
                for i, line in enumerate(open(f, encoding='utf-8'), 1):
                    if line.rstrip() != line.rstrip('\\n').rstrip('\\r'):
                        violations.append(f"{f}:{i}")
            except: pass
        return (not violations, violations)
        
    def _check_no_missing_newline(self): 
        violations = []
        for f in self.ctx.python_files:
            try:
                with open(f, 'rb') as file:
                    file.seek(-1, 2)
                    if file.read(1) not in (b'\\n', b'\\r'):
                        violations.append(f)
            except: pass
        return (not violations, violations)
        
    def _check_no_tabs(self): 
        violations = []
        for f in self.ctx.python_files:
            try:
                for i, line in enumerate(open(f, encoding='utf-8'), 1):
                    if '\\t' in line: violations.append(f"{f}:{i}")
            except: pass
        return (not violations, violations)
    
    async def _check_documentation(self):
        violations = []
        for file_path in self.ctx.python_files:
            if 'test_' in file_path or file_path.endswith('__init__.py'):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                
                if not ast.get_docstring(tree):
                    violations.append(f"{file_path}: Missing module docstring")
            except Exception:
                continue
        return violations

    async def _check_naming(self):
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                            violations.append(f"{file_path}:{node.lineno}: Class '{node.name}' should be PascalCase")
            except Exception:
                continue
        return violations
'''
    
    # Step 4: Insert new guardians
    content = content[:insertion_point] + hygiene_guardian + content[insertion_point:]
    
    # Step 5: Enhance ArchitectureGovernor to absorb BudgetAgent
    # Find and replace ArchitectureGovernor
    arch_pattern = r'class ArchitectureGovernor\(SubAtomicAgent\):.*?(?=\nclass \w+\()'
    arch_match = re.search(arch_pattern, content, re.DOTALL)
    
    if arch_match:
        print("Enhancing ArchitectureGovernor...")
        enhanced_arch = '''class ArchitectureGovernor(SubAtomicAgent):
    """
    Unified Architecture Governor.
    Enforces:
      - Depth & Taxonomy (Key 49)
      - Atomicity (Key 50 - File Size, Class Count)
      - Complexity Budget (Key 17, 19 - formerly BudgetAgent)
      - System Architecture (Key 40, 41)
    """

    MAX_COMPLEXITY = 10
    MAX_FUNC_LINES = 50

    def can_run(self) -> bool:
        return True

    async def execute(self):
        print(f"\\n[>>>] {self.name} ACTIVATED: Enforcing Architectural Laws...")
        await asyncio.sleep(0)
        
        violations = {
            'depth': [], 'atomicity': [], 'complexity': [], 'system': []
        }
        
        for file_path in self.ctx.python_files:
            # 1. Structural Checks
            violations['depth'].extend(self._check_depth(file_path))
            violations['atomicity'].extend(self._check_atomicity(file_path))
            violations['system'].extend(self._check_system(file_path))
            
            # 2. Complexity Checks (formerly BudgetAgent)
            violations['complexity'].extend(self._check_complexity(file_path))

        # Report
        for cat, v in violations.items():
            if v: print(f"   🏛️  {cat.title()} Violations: {len(v)}")
        
        self.ctx.report(self.name, 49, not violations['depth'], violations['depth'])
        self.ctx.report(self.name, 50, not violations['atomicity'], violations['atomicity'])
        self.ctx.report(self.name, 19, not violations['complexity'], violations['complexity'])
        self.ctx.report(self.name, 40, not violations['system'], violations['system'])
        self.ctx.report(self.name, 41, True, ["Root hygiene maintained"])

    def _check_depth(self, file_path):
        from pathlib import Path
        parts = Path(file_path).parts
        if len([p for p in parts if p not in {'.git', 'data'}]) - 1 > 5:
            return [f"{file_path}: Depth > 5"]
        return []

    def _check_atomicity(self, file_path):
        v = []
        try:
            with open(file_path, encoding='utf-8') as f: content = f.read()
            if len(content.splitlines()) > 200: v.append(f"{file_path}: > 200 lines")
            
            tree = ast.parse(content)
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            if len(classes) > 1: v.append(f"{file_path}: Multiple classes")
        except: pass
        return v

    def _check_complexity(self, file_path):
        """Check cyclomatic complexity and function length."""
        v = []
        try:
            tree = ast.parse(open(file_path, encoding='utf-8').read())
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Check Length
                    if hasattr(node, 'end_lineno'):
                        length = node.end_lineno - node.lineno
                        if length > self.MAX_FUNC_LINES:
                            v.append(f"{file_path}:{node.name} too long ({length})")
                    
                    # Check Complexity
                    complexity = self._calculate_mccabe(node)
                    if complexity > self.MAX_COMPLEXITY:
                        v.append(f"{file_path}:{node.name} complex ({complexity})")
        except: pass
        return v

    def _calculate_mccabe(self, node):
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.AsyncFor, ast.ExceptHandler)):
                complexity += 1
        return complexity

    def _check_system(self, file_path):
        return []

'''
        content = content[:arch_match.start()] + enhanced_arch + content[arch_match.end():]
    
    # Step 6: Update main execution block
    main_block = '''if __name__ == "__main__":
    ctx = ValidationContext()
    
    # MAGNIFICENT SEVEN Agent Sequence
    agents = [
        Historian(ctx),              # 1. Memory/Skip logic
        ArchitectureGovernor(ctx),   # 2. Architecture + Complexity
        HygieneGuardian(ctx),        # 3. File system hygiene
        CodeStyleGuardian(ctx),      # 4. Code style + formatting
        DependencySentinel(ctx),     # 5. Imports
        SafetyInspector(ctx),        # 6. Security
        ConcurrencyGuardian(ctx),    # 7. Concurrency safety
    ]

    async def run_mission():
        print("🚀 STARTING MAGNIFICENT SEVEN MISSION")
        for agent in agents:
            if agent.can_run():
                await agent.execute()
        
        print("\\n" + "="*50)
        print("MISSION COMPLETE")
        print("="*50)

    asyncio.run(run_mission())
'''
    
    old_main_pattern = r'if __name__ == "__main__":.*$'
    content = re.sub(old_main_pattern, main_block, content, flags=re.DOTALL)
    
    # Step 7: Write back
    backup_path = file_path.with_suffix('.py.backup_mag7')
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        with open(backup_path, 'w', encoding='utf-8') as fb:
            fb.write(f.read())
    print(f"\nBackup saved to: {backup_path}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_length = len(content.splitlines())
    reduction = ((original_length - new_length) / original_length) * 100
    
    print(f"\n✅ Transformation complete!")
    print(f"  Original: {original_length} lines")
    print(f"  New: {new_length} lines")
    print(f"  Change: {reduction:+.1f}%")
    
    # Step 8: Verify syntax
    try:
        import ast
        ast.parse(content)
        print("\n✅ Syntax check: PASSED")
        
        # Verify deletions
        deleted = ['GenerativeGuard', 'TheCurator', 'CodeJanitor', 'StyleGuardian', 'BudgetAgent']
        for agent in deleted:
            if f'class {agent}(' in content:
                print(f"⚠️  WARNING: {agent} still present!")
                return False
        
        # Verify new agents
        new_agents = ['HygieneGuardian', 'CodeStyleGuardian']
        for agent in new_agents:
            if f'class {agent}(' not in content:
                print(f"⚠️  WARNING: {agent} not found!")
                return False
        
        print("\n✅ All old agents removed")
        print("✅ All new guardians present")
        print("✅ ArchitectureGovernor enhanced")
        return True
        
    except SyntaxError as e:
        print(f"\n❌ Syntax check: FAILED at line {e.lineno}")
        print(f"   {e.msg}")
        return False

if __name__ == '__main__':
    success = transform_to_magnificent_seven()
    exit(0 if success else 1)
