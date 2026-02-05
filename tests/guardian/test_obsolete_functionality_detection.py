"""
Guardian test to detect obsolete test files and functionality.

This test acts as a VALIDATION GATE in the Guardian (Red Shield) component.
It is COMPLEMENTARY to unit/e2e/integration tests - it does NOT replace them.

Architecture Position:
- Guardian tests = Red Shield (Validation Gate) between Contextual Router and Symmetric Validator-Healer
- Unit/E2E/Integration tests = Standard test coverage under tests/ folder
- Guardian validates architectural compliance; unit tests validate functionality

Detection Strategy (AST-based, NOT string regex):
1. Parse files with AST to verify imports resolve to existing modules
2. Use fuzzy matching to detect references to renamed/moved code
3. Check if test classes/functions reference existing production code
4. NEVER delete based on filename alone (e.g., "phase1" in name)

Design Pattern: Guardian tests are VALIDATION GATES that call VALIDATORS (agents).
"""

import ast
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from difflib import SequenceMatcher

import pytest

# Import existing agents for validation
try:
    from agentic_core.L5_safety.validators.file_classification_agent import FileClassificationAgent
    from agentic_core.L5_safety.validators.location_agent import LocationAgent
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False


class TestObsoleteFunctionalityDetection:
    """
    Guardian validation gate for obsolete functionality detection.
    
    IMPORTANT: This is COMPLEMENTARY to unit/e2e tests, not a replacement.
    Guardian tests validate architectural compliance.
    Unit/E2E tests validate functional correctness.
    """

    @pytest.fixture
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    def collect_test_files_all_levels(self, tests_root: Path) -> Dict[str, List[Path]]:
        """
        Collect test files at ALL levels of the tests/ hierarchy.
        
        Returns dict with keys for each level:
        - 'tests_root': tests/*.py
        - 'tests_unit': tests/unit/*.py
        - 'tests_unit_agentic_core': tests/unit/agentic_core/*.py
        - 'tests_unit_agentic_core_L0': tests/unit/agentic_core/L0_maintenance/*.py
        - etc.
        """
        result = {}
        
        # Level 1: tests/ root
        root_tests = list(tests_root.glob("test_*.py"))
        if root_tests:
            result['tests_root'] = root_tests
        
        # Level 2: tests/unit/, tests/e2e/, tests/integration/, etc.
        for subdir in tests_root.iterdir():
            if subdir.is_dir() and not subdir.name.startswith(('__', '.')):
                level2_tests = list(subdir.glob("test_*.py"))
                if level2_tests:
                    result[f'tests_{subdir.name}'] = level2_tests
                
                # Level 3: tests/unit/agentic_core/, etc.
                for subsubdir in subdir.iterdir():
                    if subsubdir.is_dir() and not subsubdir.name.startswith(('__', '.')):
                        level3_tests = list(subsubdir.glob("test_*.py"))
                        if level3_tests:
                            result[f'tests_{subdir.name}_{subsubdir.name}'] = level3_tests
                        
                        # Level 4: tests/unit/agentic_core/L0_maintenance/, etc.
                        for subsubsubdir in subsubdir.iterdir():
                            if subsubsubdir.is_dir() and not subsubsubdir.name.startswith(('__', '.')):
                                level4_tests = list(subsubsubdir.glob("test_*.py"))
                                if level4_tests:
                                    result[f'tests_{subdir.name}_{subsubdir.name}_{subsubsubdir.name}'] = level4_tests
        
        return result

    def collect_test_files(self, test_dir: Path) -> List[Path]:
        """Collect all Python test files in directory recursively."""
        return list(test_dir.rglob("test_*.py"))
    
    def check_naming_violations(self, file_path: Path, project_root: Path) -> List[str]:
        """Use FileClassificationAgent to detect naming violations."""
        issues = []
        
        if not AGENTS_AVAILABLE:
            # Fallback: Basic PascalCase detection
            if file_path.stem != file_path.stem.lower():
                issues.append(f"PascalCase naming detected: {file_path.name}")
            return issues
        
        try:
            # Call existing agent for validation
            agent = FileClassificationAgent(project_root)
            violations = agent.detect_naming_violations([file_path])
            
            for violation in violations:
                issues.append(f"Naming violation: {violation}")
        except Exception as e:
            # Fallback to basic check
            if file_path.stem != file_path.stem.lower():
                issues.append(f"PascalCase naming detected: {file_path.name}")
        
        return issues
    
    def check_location_violations(self, file_path: Path, project_root: Path) -> List[str]:
        """Use LocationAgent to detect depth/placement violations."""
        issues = []
        
        if not AGENTS_AVAILABLE:
            return issues
        
        try:
            # Call existing agent for validation
            agent = LocationAgent(project_root, healing_enabled=False)
            violations = agent.validate_file_location(file_path)
            
            if violations:
                for violation in violations:
                    issues.append(f"Location violation: {violation}")
        except Exception:
            # Skip if agent not available
            pass
        
        return issues

    def check_imports_exist(self, file_path: Path) -> List[str]:
        """Check if all imports in a test file actually exist."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name
                        try:
                            importlib.import_module(module_name)
                        except ImportError:
                            issues.append(f"Missing import: {module_name}")
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module
                        try:
                            importlib.import_module(module_name)
                        except ImportError:
                            issues.append(f"Missing from-import: {module_name}")
        
        except Exception as e:
            issues.append(f"Error parsing {file_path}: {e}")
        
        return issues

    def check_file_references(self, file_path: Path, project_root: Path) -> List[str]:
        """Check if files referenced in tests actually exist."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for common file reference patterns
            patterns = [
                'PROJECT_ROOT / "',
                'Path("',
                'open("',
                'with open("',
            ]
            
            for pattern in patterns:
                start = 0
                while True:
                    idx = content.find(pattern, start)
                    if idx == -1:
                        break
                    
                    # Extract the path
                    start = idx + len(pattern)
                    end = content.find('"', start)
                    if end == -1:
                        end = content.find("'", start)
                    if end == -1:
                        break
                    
                    path_str = content[start:end]
                    
                    # Try to resolve the path
                    if pattern == 'PROJECT_ROOT / "':
                        full_path = project_root / path_str
                    elif pattern.startswith('Path('):
                        full_path = project_root / path_str
                    else:
                        # Relative path from test file
                        full_path = file_path.parent / path_str
                    
                    if not full_path.exists():
                        issues.append(f"Missing file reference: {path_str}")
                    
                    start = end + 1
        
        except Exception as e:
            issues.append(f"Error checking file references in {file_path}: {e}")
        
        return issues

    def analyze_with_ast(self, file_path: Path, project_root: Path) -> Dict[str, Any]:
        """
        Use AST analysis to determine if a test file is obsolete.
        
        This is the CORRECT approach - analyze actual code structure,
        NOT string patterns in filenames or content.
        
        Returns:
            Dict with 'is_obsolete', 'confidence', 'reasons', 'imports_status'
        """
        result = {
            'is_obsolete': False,
            'confidence': 0.0,
            'reasons': [],
            'imports_status': [],
            'classes_found': [],
            'functions_found': [],
            'references_checked': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Extract all imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(('import', alias.name, node.lineno))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(('from', node.module, node.lineno))
            
            # Check each import with AST verification
            broken_imports = []
            valid_imports = []
            for import_type, module_name, lineno in imports:
                try:
                    # Try to find the module spec (doesn't execute the module)
                    spec = importlib.util.find_spec(module_name.split('.')[0])
                    if spec is None:
                        broken_imports.append((module_name, lineno))
                    else:
                        valid_imports.append(module_name)
                except (ModuleNotFoundError, ImportError, ValueError):
                    broken_imports.append((module_name, lineno))
            
            result['imports_status'] = {
                'valid': valid_imports,
                'broken': broken_imports
            }
            
            # Extract test classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test'):
                        result['classes_found'].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        result['functions_found'].append(node.name)
            
            # Determine obsolescence based on AST analysis
            # A file is ONLY obsolete if:
            # 1. ALL imports are broken (not just some)
            # 2. AND no valid test classes/functions exist
            # 3. OR the file is empty/has no executable code
            
            total_imports = len(imports)
            broken_count = len(broken_imports)
            
            if total_imports > 0 and broken_count == total_imports:
                # ALL imports are broken - high confidence obsolete
                result['is_obsolete'] = True
                result['confidence'] = 0.9
                result['reasons'].append(f"All {broken_count} imports are broken")
            elif broken_count > 0 and broken_count >= total_imports * 0.8:
                # Most imports broken - medium confidence
                result['confidence'] = 0.6
                result['reasons'].append(f"{broken_count}/{total_imports} imports are broken")
            
            # Check if file has no test content
            if not result['classes_found'] and not result['functions_found']:
                result['reasons'].append("No test classes or functions found")
                result['confidence'] = max(result['confidence'], 0.5)
            
        except SyntaxError as e:
            result['reasons'].append(f"Syntax error - file may be corrupted: {e}")
            result['confidence'] = 0.7
        except Exception as e:
            result['reasons'].append(f"Analysis error: {e}")
        
        return result
    
    def fuzzy_match_module(self, broken_module: str, project_root: Path) -> List[Tuple[str, float]]:
        """
        Use fuzzy matching to find similar module names that might be the correct target.
        
        This helps identify if a module was renamed rather than deleted.
        """
        matches = []
        
        # Get all Python files in agentic_core
        agentic_core = project_root / "agentic_core"
        if not agentic_core.exists():
            return matches
        
        # Extract the class/module name from the broken import
        parts = broken_module.split('.')
        target_name = parts[-1] if parts else broken_module
        
        # Search for similar names
        for py_file in agentic_core.rglob("*.py"):
            file_stem = py_file.stem
            
            # Calculate similarity
            ratio = SequenceMatcher(None, target_name.lower(), file_stem.lower()).ratio()
            
            if ratio > 0.6:  # 60% similarity threshold
                matches.append((str(py_file.relative_to(project_root)), ratio))
        
        # Sort by similarity
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:5]  # Return top 5 matches
    
    def detect_obsolete_patterns(self, file_path: Path) -> List[str]:
        """
        DEPRECATED: This method used string regex which is NOT acceptable.
        Use analyze_with_ast() instead for proper AST-based analysis.
        
        This method now returns empty list - obsolescence detection
        should ONLY be done via AST analysis.
        """
        # DO NOT use string regex for obsolescence detection
        # Filename patterns like "phase1", "phase2" are NOT sufficient
        # to determine if a file should be deleted
        return []

    def test_detect_obsolete_tests(self, project_root):
        """
        Guardian gate: Validate test files using AST-based analysis.
        
        IMPORTANT:
        - This test scans ALL levels of tests/ folder (root, unit, e2e, etc.)
        - Uses AST analysis, NOT string regex
        - NEVER deletes based on filename alone (e.g., "phase1" in name)
        - Guardian tests are COMPLEMENTARY to unit/e2e tests, not replacements
        """
        tests_root = project_root / "tests"
        
        if not tests_root.exists():
            pytest.skip(f"Tests directory not found: {tests_root}")
        
        # Collect test files at ALL levels
        all_test_files_by_level = self.collect_test_files_all_levels(tests_root)
        
        print("\n=== GUARDIAN GATE: AST-BASED TEST FILE ANALYSIS ===")
        print(f"Scanning tests/ folder at ALL levels...")
        
        # Report what we found at each level
        for level, files in all_test_files_by_level.items():
            print(f"\n  {level}: {len(files)} test files")
        
        # Analyze each file with AST
        analysis_results = {}
        high_confidence_obsolete = []
        needs_review = []
        healthy_files = []
        
        for level, test_files in all_test_files_by_level.items():
            for test_file in test_files:
                rel_path = str(test_file.relative_to(project_root))
                
                # Use AST-based analysis (NOT string regex)
                ast_result = self.analyze_with_ast(test_file, project_root)
                
                # Also check naming violations via agents
                naming_issues = self.check_naming_violations(test_file, project_root)
                
                analysis_results[rel_path] = {
                    'ast_analysis': ast_result,
                    'naming_issues': naming_issues,
                    'level': level
                }
                
                # Categorize based on AST analysis confidence
                if ast_result['is_obsolete'] and ast_result['confidence'] >= 0.8:
                    high_confidence_obsolete.append(rel_path)
                elif ast_result['confidence'] >= 0.5:
                    needs_review.append(rel_path)
                else:
                    healthy_files.append(rel_path)
        
        # Report findings
        print(f"\n=== ANALYSIS SUMMARY ===")
        print(f"Total files analyzed: {len(analysis_results)}")
        print(f"Healthy files: {len(healthy_files)}")
        print(f"Needs review (medium confidence): {len(needs_review)}")
        print(f"High confidence obsolete: {len(high_confidence_obsolete)}")
        
        # Report files that need review (NOT auto-delete)
        if needs_review:
            print(f"\n=== FILES NEEDING MANUAL REVIEW ({len(needs_review)}) ===")
            print("These files have potential issues but require human verification:")
            for rel_path in needs_review[:20]:  # Limit output
                result = analysis_results[rel_path]
                print(f"\n  {rel_path}:")
                for reason in result['ast_analysis']['reasons']:
                    print(f"    - {reason}")
                
                # Show fuzzy matches for broken imports
                broken = result['ast_analysis'].get('imports_status', {}).get('broken', [])
                for module, lineno in broken[:3]:
                    matches = self.fuzzy_match_module(module, project_root)
                    if matches:
                        print(f"    - Broken import '{module}' (line {lineno})")
                        print(f"      Possible matches: {[m[0] for m in matches[:2]]}")
        
        # Report high confidence obsolete (still require confirmation)
        if high_confidence_obsolete:
            print(f"\n=== HIGH CONFIDENCE OBSOLETE ({len(high_confidence_obsolete)}) ===")
            print("These files appear obsolete based on AST analysis:")
            print("IMPORTANT: Manual verification required before deletion!")
            for rel_path in high_confidence_obsolete:
                result = analysis_results[rel_path]
                print(f"\n  {rel_path}:")
                for reason in result['ast_analysis']['reasons']:
                    print(f"    - {reason}")
        
        # Report naming issues separately (these are NOT obsolescence)
        naming_violations = [
            (path, result['naming_issues'])
            for path, result in analysis_results.items()
            if result['naming_issues']
        ]
        if naming_violations:
            print(f"\n=== NAMING VIOLATIONS ({len(naming_violations)}) ===")
            print("These are naming convention issues, NOT obsolescence:")
            for path, issues in naming_violations[:10]:
                print(f"\n  {path}:")
                for issue in issues:
                    print(f"    - {issue}")
        
        # DO NOT auto-generate deletion script
        # Deletion requires human verification
        if high_confidence_obsolete:
            print(f"\n=== ACTION REQUIRED ===")
            print("High confidence obsolete files detected.")
            print("Please manually verify before deletion.")
            print("DO NOT delete based on filename patterns alone.")
        
        # This test is INFORMATIONAL - it reports findings but does not fail
        # Guardian tests validate architectural compliance, not delete files
        print(f"\n=== GUARDIAN GATE: ANALYSIS COMPLETE ===")
        print(f"This is an INFORMATIONAL report. Guardian tests are COMPLEMENTARY to unit/e2e tests.")
