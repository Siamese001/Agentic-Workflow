#!/usr/bin/env python3
"""
Bulk fix script to replace hardcoded dashboard paths with SSOT imports.
"""
import re
from pathlib import Path

# Files to fix (from validation output)
FILES_TO_FIX = [
    "scripts/analyze_dashboard_color_bug.py",
    "scripts/debug_dashboard_rendering.py",
    "scripts/fix_duplicate_realagentdata.py",
    "scripts/rca_dashboard_row_collapse.py",
    "scripts/rca_table_rendering.py",
    "scripts/remove_duplicate_lines.py",
    "scripts/test_dashboard_end_to_end.py",
    "scripts/test_dashboard_visual.py",
    "scripts/verify_no_mock_data.py",
]

IMPORT_STATEMENT = """# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.L5_safety.validators.structure_blueprint_2 import DASHBOARD_DIR, get_validated_project_root
"""

def fix_file(file_path: Path) -> bool:
    """Fix a single file by replacing hardcoded paths with SSOT."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Check if already has SSOT import
        has_ssot_import = 'from agentic_core.L5_safety.validators.structure_blueprint_2 import' in content
        
        # Add import if not present
        if not has_ssot_import:
            # Find the last import statement
            lines = content.split('\n')
            last_import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    last_import_idx = i
            
            # Insert SSOT import after last import
            lines.insert(last_import_idx + 1, '')
            lines.insert(last_import_idx + 2, IMPORT_STATEMENT.strip())
            content = '\n'.join(lines)
        
        # Replace hardcoded paths
        replacements = [
            (
                r'Path\(["\']C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard\.html["\']\)',
                'get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"'
            ),
            (
                r'Path\(["\']C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards["\']\)',
                'get_validated_project_root() / DASHBOARD_DIR'
            ),
            (
                r"Path\('C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard\.html'\)",
                'get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"'
            ),
            (
                r'Path\("C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard\.html"\)',
                'get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"'
            ),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Write back if changed
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            print(f"⏭️  Skipped (no changes needed): {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    project_root = Path(__file__).parent.parent
    fixed_count = 0
    
    print("=" * 80)
    print("DASHBOARD HARDCODING FIX")
    print("=" * 80)
    print(f"\nFixing {len(FILES_TO_FIX)} files...\n")
    
    for file_rel_path in FILES_TO_FIX:
        file_path = project_root / file_rel_path
        if file_path.exists():
            if fix_file(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("\n" + "=" * 80)
    print(f"✅ Fixed {fixed_count} files")
    print("=" * 80)

if __name__ == "__main__":
    main()
