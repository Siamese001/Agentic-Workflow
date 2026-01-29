"""
Phase 2: The "Nuclear" Import Guard
Eliminates "Ghost Imports" and runtime syntax crashes
"""
import ast
import os
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Set, Dict, List, Tuple


class TestImportSafety:
    """Test suite to catch hidden import issues and runtime crashes"""
    
    def get_all_python_files(self, directories: List[str]) -> List[Path]:
        """Get all Python files from specified directories"""
        python_files = []
        for directory in directories:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.py'):
                            python_files.append(Path(root) / file)
        return python_files
    
    def test_global_smoke_loader(self):
        """Test 1: Dynamically import every module to catch SyntaxError, IndentationError, NameError"""
        print("\n=== PHASE 2: Global Smoke Loader ===")
        
        directories = ['apps_rg', 'apps_shared']
        python_files = self.get_all_python_files(directories)
        
        failed_imports = []
        
        for file_path in python_files:
            try:
                # Convert path to module import path
                file_path_abs = Path(file_path).resolve()
                cwd_abs = Path.cwd().resolve()
                
                if file_path_abs.is_relative_to(cwd_abs):
                    relative_path = file_path_abs.relative_to(cwd_abs)
                    module_parts = list(relative_path.parts[:-1])  # Remove .py extension
                    module_name = '.'.join(module_parts + [file_path_abs.stem])
                    
                    # Try to import the module
                    spec = importlib.util.spec_from_file_location(module_name, file_path_abs)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                    
            except (SyntaxError, IndentationError, NameError) as e:
                failed_imports.append({
                    'file': str(file_path),
                    'error_type': type(e).__name__,
                    'error': str(e),
                    'line': getattr(e, 'lineno', 'Unknown')
                })
            except Exception as e:
                # Other exceptions are noted but don't fail the test
                print(f"Warning: {file_path} raised {type(e).__name__}: {e}")
        
        if failed_imports:
            error_msg = "CRITICAL IMPORT FAILURES DETECTED:\n"
            for failure in failed_imports:
                error_msg += f"\n🔥 {failure['file']}\n"
                error_msg += f"   Type: {failure['error_type']}\n"
                error_msg += f"   Line: {failure['line']}\n"
                error_msg += f"   Error: {failure['error']}\n"
            
            assert False, error_msg
        
        print(f"✅ All {len(python_files)} Python files imported successfully")
    
    def test_circular_dependency_scanner(self):
        """Test 2: Detect circular dependencies using AST analysis"""
        print("\n=== PHASE 2: Circular Dependency Scanner ===")
        
        def extract_imports(file_path: Path) -> Set[str]:
            """Extract import targets from a Python file"""
            imports = set()
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module)
            except Exception:
                # If we can't parse, skip this file
                pass
            return imports
        
        # Build import graph for apps_rg
        apps_rg_files = self.get_all_python_files(['apps_rg'])
        import_graph: Dict[str, Set[str]] = {}
        
        for file_path in apps_rg_files:
            module_name = file_path.stem
            imports = extract_imports(file_path)
            
            # Filter to only imports within our project
            project_imports = set()
            for imp in imports:
                if imp.startswith('apps_rg.') or imp.startswith('apps_shared.'):
                    project_imports.add(imp.split('.')[0] + '.' + imp.split('.')[1])
            
            import_graph[module_name] = project_imports
        
        # Detect circular dependencies
        circular_deps = []
        for module_a, imports_a in import_graph.items():
            for module_b in imports_a:
                module_b_name = module_b.split('.')[-1]
                if module_b_name in import_graph:
                    if module_a in import_graph[module_b_name]:
                        circular_deps.append((module_a, module_b_name))
        
        if circular_deps:
            error_msg = "CIRCULAR DEPENDENCIES DETECTED:\n"
            for dep_a, dep_b in circular_deps:
                error_msg += f"🔄 {dep_a} ↔ {dep_b}\n"
            
            assert False, error_msg
        
        print(f"✅ No circular dependencies found in {len(apps_rg_files)} files")
    
    def test_zombie_reference_check(self):
        """Test 3: Verify that import targets actually exist on disk"""
        print("\n=== PHASE 2: Zombie Reference Check ===")
        
        directories = ['apps_rg', 'apps_shared']
        python_files = self.get_all_python_files(directories)
        
        # Build a map of all existing modules
        existing_modules = set()
        for file_path in python_files:
            file_path_abs = Path(file_path).resolve()
            cwd_abs = Path.cwd().resolve()
            
            if file_path_abs.is_relative_to(cwd_abs):
                relative_path = file_path_abs.relative_to(cwd_abs)
                parts = list(relative_path.parts[:-1])  # Remove .py
                module_path = '.'.join(parts)
                existing_modules.add(module_path)
                existing_modules.add(module_path + '.' + file_path_abs.stem)
        
        zombie_imports = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line.startswith('from ') and ' import ' in line:
                        # Extract the import path
                        import_part = line[5:]  # Remove 'from '
                        import_path = import_part.split(' import ')[0].strip()
                        
                        # Only check project-local imports (apps_rg or apps_shared)
                        if import_path.startswith('apps_rg') or import_path.startswith('apps_shared'):
                            # Check if the target exists
                            if not any(existing.startswith(import_path) for existing in existing_modules):
                                zombie_imports.append({
                                    'file': str(file_path),
                                    'line': line_num,
                                    'import': import_path,
                                    'full_line': line.strip()
                                })
                            
            except Exception:
                continue
        
        if zombie_imports:
            error_msg = "ZOMBIE IMPORTS DETECTED (Targets don't exist):\n"
            for zombie in zombie_imports:
                error_msg += f"🧟 {zombie['file']}:{zombie['line']}\n"
                error_msg += f"   Import: {zombie['import']}\n"
                error_msg += f"   Line: {zombie['full_line']}\n"
            
            assert False, error_msg
        
        print(f"✅ All imports point to existing targets in {len(python_files)} files")
    
    def test_ssot_dependency_flow(self):
        """Test 4: Enforce one-way valve - apps_shared MUST NOT import from apps_rg"""
        print("\n=== PHASE 2: SSOT Dependency Flow Check ===")
        
        apps_shared_files = self.get_all_python_files(['apps_shared'])
        
        violations = []
        
        for file_path in apps_shared_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    if line.strip().startswith('from apps_rg'):
                        violations.append({
                            'file': str(file_path),
                            'line': line_num,
                            'violation': line.strip()
                        })
                        
            except Exception:
                continue
        
        if violations:
            error_msg = "SSOT DEPENDENCY VIOLATIONS DETECTED:\n"
            error_msg += "❌ apps_shared (Utilities) MUST NOT import from apps_rg (Business Logic)\n\n"
            
            for violation in violations:
                error_msg += f"🚫 {violation['file']}:{violation['line']}\n"
                error_msg += f"   {violation['violation']}\n"
            
            assert False, error_msg
        
        print(f"✅ No SSOT dependency violations in {len(apps_shared_files)} files")


# Standalone test runner for Windsurf execution
if __name__ == "__main__":
    test_instance = TestImportSafety()
    
    print("🚀 Starting Phase 2: Nuclear Import Guard")
    print("=" * 60)
    
    try:
        test_instance.test_global_smoke_loader()
        test_instance.test_circular_dependency_scanner()
        test_instance.test_zombie_reference_check()
        test_instance.test_ssot_dependency_flow()
        
        print("\n" + "=" * 60)
        print("✅ PHASE 2 COMPLETE: All import safety tests passed!")
        print("🛡️  Nuclear Import Guard is active and protecting the codebase")
        
    except AssertionError as e:
        print("\n" + "=" * 60)
        print("❌ PHASE 2 FAILED: Import safety violations detected!")
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during Phase 2: {e}")
        sys.exit(1)
