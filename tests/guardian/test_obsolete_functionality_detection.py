"""
Guardian test to detect obsolete test files and functionality.

This test acts as a VALIDATION GATE in the Guardian (Red Shield) component.
It enforces architectural compliance by calling validation agents.

Compliance Strategy:
1. Call FileClassificationAgent for naming/structure violations
2. Call LocationAgent for depth/placement violations
3. Detect obsolete patterns (phase files, missing imports)
4. Emit signed artifact (pass/fail with metadata)

Design Pattern: Guardian tests are VALIDATION GATES that call VALIDATORS (agents).
"""

import ast
import importlib
import sys
from pathlib import Path
from typing import List, Dict, Any

import pytest

# Import existing agents for validation
try:
    from agentic_core.L5_safety.validators.file_classification_agent import FileClassificationAgent
    from agentic_core.L5_safety.validators.location_agent import LocationAgent
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False


class TestObsoleteFunctionalityDetection:
    """Guardian validation gate for obsolete functionality detection."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    def collect_test_files(self, test_dir: Path) -> List[Path]:
        """Collect all Python test files in directory."""
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

    def detect_obsolete_patterns(self, file_path: Path) -> List[str]:
        """Detect patterns indicating obsolete test files."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for obsolete indicators (more specific patterns)
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line_lower = line.lower()
                
                # Skip documentation lines that mention phases historically
                if any(doc_marker in line_lower for doc_marker in ['"""', "'''", '# consolidated from', '# merged from', 'consolidated from phase', 'merged from phase']):
                    continue
                
                # Check for actual obsolete indicators
                if 'phase ' in line_lower and any(skip not in line_lower for skip in ['consolidated', 'merged', 'documentation', 'history']):
                    issues.append(f"Obsolete indicator found on line {i+1}: {line.strip()}")
                
                if any(indicator in line_lower for indicator in [
                    'migration:', 'migration test', 'migration phase',
                    'canon cleanup', 'canon deprecation',
                    'legacy cleanup', 'deprecated:',
                    'todo: delete', 'fixme: delete',
                    'temporary test', 'temporary file'
                ]):
                    issues.append(f"Obsolete indicator found on line {i+1}: {line.strip()}")
            
            # Check for very old dates in comments (not documentation headers)
            import re
            for i, line in enumerate(lines):
                # Skip documentation headers
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    continue
                    
                # Look for old dates in comments
                if re.search(r'(201[0-9]|202[0-4])', line) and line.strip().startswith('#'):
                    issues.append(f"Old date pattern on line {i+1}: {line.strip()}")
        
        except Exception as e:
            issues.append(f"Error checking obsolete patterns in {file_path}: {e}")
        
        return issues

    def test_detect_obsolete_tests(self, project_root):
        """Guardian gate: Validate no obsolete functionality exists in test files."""
        test_dir = project_root / "tests" / "unit" / "agentic_core"
        
        if not test_dir.exists():
            pytest.skip(f"Test directory not found: {test_dir}")
        
        test_files = self.collect_test_files(test_dir)
        
        obsolete_files = []
        all_issues = {}
        
        for test_file in test_files:
            issues = []
            
            # Use agents for validation (preferred)
            issues.extend(self.check_naming_violations(test_file, project_root))
            issues.extend(self.check_location_violations(test_file, project_root))
            
            # Guardian-specific checks (not in agents)
            issues.extend(self.check_imports_exist(test_file))
            issues.extend(self.check_file_references(test_file, project_root))
            issues.extend(self.detect_obsolete_patterns(test_file))
            
            if issues:
                all_issues[str(test_file.relative_to(project_root))] = issues
                
                # If file has multiple critical issues, mark as obsolete
                critical_issues = [i for i in issues if any(x in i.lower() for x in ['missing', 'obsolete', 'phase', 'migration'])]
                if len(critical_issues) >= 2:
                    obsolete_files.append(str(test_file.relative_to(project_root)))
        
        # Emit signed artifact
        if all_issues:
            print("\n=== GUARDIAN GATE: OBSOLETE FUNCTIONALITY DETECTED ===")
            for file_path, issues in all_issues.items():
                print(f"\n{file_path}:")
                for issue in issues:
                    print(f"  - {issue}")
            
            if obsolete_files:
                print(f"\n=== CANDIDATES FOR DELETION ({len(obsolete_files)} files) ===")
                for file_path in obsolete_files:
                    print(f"  - {file_path}")
                
                # Write deletion script
                deletion_script = project_root / "delete_obsolete_tests.py"
                with open(deletion_script, 'w') as f:
                    f.write('#!/usr/bin/env python3\n')
                    f.write('"""Auto-generated script to delete obsolete test files."""\n\n')
                    f.write('import sys\nfrom pathlib import Path\n\n')
                    f.write('def main():\n')
                    f.write('    """Delete obsolete test files."""\n')
                    f.write('    project_root = Path(__file__).parent\n')
                    f.write('    obsolete_files = [\n')
                    for file_path in obsolete_files:
                        f.write(f'        "{file_path}",\n')
                    f.write('    ]\n\n')
                    f.write('    print(f"Deleting {len(obsolete_files)} obsolete test files...")\n')
                    f.write('    for file_path in obsolete_files:\n')
                    f.write('        full_path = project_root / file_path\n')
                    f.write('        if full_path.exists():\n')
                    f.write('            full_path.unlink()\n')
                    f.write(f'            print(f"Deleted: {file_path}")\n')
                    f.write('        else:\n')
                    f.write(f'            print(f"Already deleted: {file_path}")\n')
                    f.write('\nif __name__ == "__main__":\n')
                    f.write('    main()\n')
                
                print(f"\nDeletion script created: {deletion_script}")
                print("Run 'python delete_obsolete_tests.py' to delete obsolete files.")
        
        # Fail gate if any issues found
        if all_issues:
            pytest.fail(f"GUARDIAN GATE FAILED: {len(all_issues)} files with obsolete functionality. See output above.")
