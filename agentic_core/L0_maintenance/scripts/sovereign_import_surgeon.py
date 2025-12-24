"""
SOVEREIGN IMPORT SURGEON
Scans all .py files and identifies import statements that need updating
to match the new Depth-3 hierarchy.

DRY RUN MODE: Lists all files requiring changes before applying fixes.
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from typing import Any, Optional, Protocol, Dict, List
from collections import defaultdict

# Exclusion patterns
EXCLUDE_DIRS = {'.venv', '__pycache', '.git', 'node_modules', 'archives'}
EXCLUDE_FILES = {'sovereign_import_surgeon.py'}

class ImportViolation:
    """Represents a single import violation."""
    def __init__(self, file_path: str, line_num: int, line: str, violation_type: str, suggested_fix: str):
        self.file_path = file_path
        self.line_num = line_num
        self.line = line
        self.violation_type = violation_type
        self.suggested_fix = suggested_fix
    
    def __repr__(self):
        return f"{self.file_path}:{self.line_num} [{self.violation_type}]\n  OLD: {self.line.strip()}\n  NEW: {self.suggested_fix}"


class SovereignImportSurgeon:
    """Scans and fixes import statements across the codebase."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.violations: Dict[str, List[ImportViolation]] = defaultdict(list)
        
        # Define import transformation rules
        # GRAVITY FIX: L0_maintenance cannot reference any higher layers
        self.import_patterns = [
            # Typo fix only (no layer references)
            (r'L0_maintancne', 'L0_maintenance', 'TYPO_FIX'),
        ]
        
        # Files that should NOT be modified (test files using relative imports are OK)
        self.test_file_pattern = re.compile(r'[\\/]tests?[\\/]|[\\/]test_.*\.py$')
        
        # Patterns for commented-out imports that should be uncommented and fixed
        self.commented_import_pattern = re.compile(r'^\s*#\s*(from\s+\.\.|from\s+agentic_core)')
        
        # Pattern for relative imports (from ..)
        self.relative_import_pattern = re.compile(r'^(\s*)from\s+\.\.')
        
        # Pattern for apps_shared imports that need P1_core
        self.apps_shared_pattern = re.compile(r'from\s+apps_shared\s+import')
        
        # Pattern for apps_rg/apps_lic imports that need depth adjustment
        self.apps_engines_pattern = re.compile(r'from\s+(apps_rg|apps_lic)\.engines\s+import')
        self.apps_templates_pattern = re.compile(r'from\s+(apps_rg|apps_lic)\.templates\s+import')
        
        # Patterns for relative imports that need absolute conversion
        self.relative_import_pattern = re.compile(r'^from\s+\.\.')
    
    def scan_file(self, file_path: Path) -> List[ImportViolation]:
        """Scan a single Python file for import violations."""
        violations = []
        
        # Skip test files - they can use relative imports
        if self.test_file_pattern.search(str(file_path)):
            return violations
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, start=1):
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Check standard patterns (memory, cognition, typos)
                for pattern, replacement, vtype in self.import_patterns:
                    if re.search(pattern, line):
                        suggested = re.sub(pattern, replacement, line).strip()
                        violations.append(ImportViolation(
                            str(file_path),
                            line_num,
                            line,
                            vtype,
                            suggested
                        ))
                
                # Check for commented-out relative imports that should be fixed
                if self.commented_import_pattern.search(line):
                    # Extract the import and suggest fixing it
                    match = re.search(r'#\s*(from\s+\.\.(\w+)\s+import\s+.+)', line)
                    if match:
                        import_stmt = match.group(1)
                        module = match.group(2)
                        suggested = self._convert_relative_to_absolute(import_stmt, file_path)
                        violations.append(ImportViolation(
                            str(file_path),
                            line_num,
                            line,
                            'COMMENTED_IMPORT',
                            suggested
                        ))
                
                # Check for relative imports in apps_shared/P1_core (not commented)
                if 'apps_shared' in str(file_path) and 'P1_core' in str(file_path):
                    if not line.strip().startswith('#') and self.relative_import_pattern.search(line):
                        suggested = self._convert_relative_to_absolute(line.strip(), file_path)
                        if suggested != line.strip():
                            violations.append(ImportViolation(
                                str(file_path),
                                line_num,
                                line,
                                'RELATIVE_TO_ABSOLUTE',
                                suggested
                            ))
                
                # Check for apps_shared imports missing P1_core
                if not line.strip().startswith('#') and self.apps_shared_pattern.search(line):
                    # Should be: from apps_shared.P1_core import
                    suggested = line.replace('from apps_shared import', 'from apps_shared.P1_core import')
                    if suggested != line:
                        violations.append(ImportViolation(
                            str(file_path),
                            line_num,
                            line,
                            'APP_STAGING',
                            suggested.strip()
                        ))
        
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")
        
        return violations
    
    def _convert_relative_to_absolute(self, line: str, file_path: Path) -> str:
        """Convert relative imports to absolute imports."""
        # Pattern: from ..module_name import X
        
        match = re.match(r'from\s+\.\.(\w+)\s+import\s+(.+)', line)
        if match:
            module_name = match.group(1)
            imports = match.group(2)
        
        return line.strip()
    
    def scan_all_files(self):
        """Scan all Python files in the project."""
        print(f"🔍 Scanning {self.root_path} for import violations...\n")
        
        py_files = []
        for root, dirs, files in os.walk(self.root_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file.endswith('.py') and file not in EXCLUDE_FILES:
                    py_files.append(Path(root) / file)
        
        print(f"📁 Found {len(py_files)} Python files to scan\n")
        
        for py_file in py_files:
            violations = self.scan_file(py_file)
            if violations:
                self.violations[str(py_file)] = violations
    
    def generate_report(self) -> str:
        """Generate a detailed dry run report."""
        if not self.violations:
            return "✅ NO IMPORT VIOLATIONS FOUND - Your imports are already sovereign-compliant!"
        
        # Group by violation type
        by_type: Dict[str, List[ImportViolation]] = defaultdict(list)
        for file_violations in self.violations.values():
            for v in file_violations:
                by_type[v.violation_type].append(v)
        
        report = []
        report.append("=" * 80)
        report.append("SOVEREIGN IMPORT SURGERY - DRY RUN REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        total_violations = sum(len(v) for v in self.violations.values())
        report.append(f"📊 SUMMARY:")
        report.append(f"   Files affected: {len(self.violations)}")
        report.append(f"   Total violations: {total_violations}")
        report.append("")
        
        # By violation type
        report.append("📋 VIOLATIONS BY TYPE:")
        for vtype, violations in sorted(by_type.items()):
            report.append(f"   {vtype}: {len(violations)} violations")
        report.append("")
        
        # Detailed breakdown
        report.append("=" * 80)
        report.append("DETAILED VIOLATIONS")
        report.append("=" * 80)
        report.append("")
        
        for vtype in sorted(by_type.keys()):
            report.append(f"\n{'=' * 80}")
            report.append(f"VIOLATION TYPE: {vtype}")
            report.append(f"{'=' * 80}\n")
            
            # Group by file
            files_with_type = defaultdict(list)
            for v in by_type[vtype]:
                files_with_type[v.file_path].append(v)
            
            for file_path in sorted(files_with_type.keys()):
                report.append(f"\n📄 {file_path}")
                report.append("-" * 80)
                for v in files_with_type[file_path]:
                    report.append(f"  Line {v.line_num}:")
                    report.append(f"    OLD: {v.line.strip()}")
                    report.append(f"    NEW: {v.suggested_fix}")
                    report.append("")
        
        # Files to modify list
        report.append("\n" + "=" * 80)
        report.append("FILES TO MODIFY")
        report.append("=" * 80)
        report.append("")
        for i, file_path in enumerate(sorted(self.violations.keys()), 1):
            count = len(self.violations[file_path])
            report.append(f"{i:3d}. {file_path} ({count} violation{'s' if count > 1 else ''})")
        
        report.append("\n" + "=" * 80)
        report.append("⚠️  DRY RUN COMPLETE - NO CHANGES APPLIED")
        report.append("=" * 80)
        report.append("\nTo apply these changes, confirm with the user first.")
        
        return "\n".join(report)
    
    def apply_fixes(self):
        """Apply all identified fixes (ONLY after user confirmation)."""
        print("🔧 APPLYING FIXES...\n")
        
        fixed_count = 0
        for file_path, violations in self.violations.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Apply fixes in reverse order to maintain line numbers
                for v in sorted(violations, key=lambda x: x.line_num, reverse=True):
                    lines[v.line_num - 1] = v.suggested_fix + '\n'
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                fixed_count += 1
                print(f"✅ Fixed: {file_path}")
            
            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")
        
        print(f"\n✅ SURGERY COMPLETE: {fixed_count} files modified")


def main():
    """Main entry point."""
    project_root = "C:/Git/Agentic-Workflow"
    
    surgeon = SovereignImportSurgeon(project_root)
    surgeon.scan_all_files()
    
    # Generate and print report
    report = surgeon.generate_report()
    print(report)
    
    # Save report to file
    report_path = Path(project_root) / "08_scripts" / "import_surgery_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_path}")
    print("\n⚠️  This was a DRY RUN. No files were modified.")
    print("Review the report and confirm before applying changes.")


if __name__ == "__main__":
    main()