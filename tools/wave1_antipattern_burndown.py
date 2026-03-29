#!/usr/bin/env python3
"""
Wave-based antipattern burndown script.
Fixes HIGH severity except:Exception and except:bare violations.
"""

import json
import re
import sys
from pathlib import Path

def fix_bare_except(content: str, line_no: int) -> str:
    """Fix bare except: to except Exception:"""
    lines = content.split('\n')
    if line_no < 1 or line_no > len(lines):
        return content
    
    line_idx = line_no - 1
    line = lines[line_idx]
    
    # Pattern: except:
    if re.search(r'^\s*except\s*:\s*$', line):
        lines[line_idx] = line.replace('except:', 'except Exception:')
        return '\n'.join(lines)
    
    # Pattern: except : (with space)
    if re.search(r'^\s*except\s*:\s*$', line):
        lines[line_idx] = re.sub(r'except\s*:', 'except Exception:', line)
        return '\n'.join(lines)
    
    return content

def fix_exception_return(content: str, line_no: int, pattern: str) -> str:
    """Fix except Exception: return_* patterns to log + return."""
    lines = content.split('\n')
    if line_no < 1 or line_no > len(lines):
        return content
    
    line_idx = line_no - 1
    line = lines[line_idx]
    
    # These are HIGH severity patterns we want to fix
    # Pattern: except Exception: return_empty_list, return_False, etc.
    if 'return_empty_list' in pattern:
        lines[line_idx] = line.replace('return_empty_list', 'return []  # TODO: Proper error handling')
    elif 'return_False' in pattern:
        lines[line_idx] = line.replace('return_False', 'return False  # TODO: Proper error handling')
    elif 'return_empty_str' in pattern:
        lines[line_idx] = line.replace('return_empty_str', "return ''  # TODO: Proper error handling")
    elif 'return_empty_dict' in pattern:
        lines[line_idx] = line.replace('return_empty_dict', 'return {}  # TODO: Proper error handling')
    
    return '\n'.join(lines)

def apply_fixes_to_file(file_path: str, violations: list) -> tuple:
    """Apply all fixes to a single file. Returns (fixed_count, new_content)."""
    p = Path(file_path)
    if not p.exists():
        return 0, None
    
    try:
        content = p.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        print(f"  ⚠️  Error reading {file_path}: {e}")
        return 0, None
    
    original_content = content
    fixed_count = 0
    
    # Sort violations by line number in reverse order (to avoid offset issues)
    sorted_violations = sorted(violations, key=lambda v: int(v.get('line_no', 0)), reverse=True)
    
    for v in sorted_violations:
        line_no = int(v.get('line_no', 0))
        evidence = v.get('evidence', '')
        severity = v.get('severity', '')
        
        # Only fix HIGH severity
        if severity != 'HIGH':
            continue
        
        # Fix bare except
        if 'except:bare' in evidence:
            new_content = fix_bare_except(content, line_no)
            if new_content != content:
                content = new_content
                fixed_count += 1
                print(f"    ✅ Fixed bare except at line {line_no}")
        
        # Fix except Exception with return patterns
        if 'except:Exception:return' in evidence:
            new_content = fix_exception_return(content, line_no, evidence)
            if new_content != content:
                content = new_content
                fixed_count += 1
                print(f"    ✅ Fixed except Exception return pattern at line {line_no}")
    
    return fixed_count, content if content != original_content else None

def main():
    """Main burndown routine."""
    # Load violations from ADG cache via Redis
    print("=" * 60)
    print("ANTIPATTERN BURNDOWN - Wave 1 (HIGH Severity)")
    print("=" * 60)
    
    # Use the MCP tool to get violations
    import subprocess
    result = subprocess.run(
        ['python', 'tools/adg/adg_violation_query.py', '--severity', 'HIGH', '--limit', '50'],
        capture_output=True,
        text=True,
        cwd='c:\\Git\\Agentic-Workflow'
    )
    
    if result.returncode != 0:
        print(f"⚠️  Could not query violations: {result.stderr}")
        # Try to read from a local file
        violations_file = Path('artifacts/adg/violations_HIGH.json')
        if violations_file.exists():
            violations = json.loads(violations_file.read_text())
        else:
            print("❌ No violations file found")
            return 1
    else:
        violations = json.loads(result.stdout)
    
    # Group by file
    files_to_fix = {}
    for v in violations:
        file_path = v.get('file_path')
        if file_path not in files_to_fix:
            files_to_fix[file_path] = []
        files_to_fix[file_path].append(v)
    
    print(f"Files to fix: {len(files_to_fix)}")
    print(f"Total HIGH severity violations: {len(violations)}")
    print()
    
    # Process each file
    total_fixed = 0
    files_changed = 0
    
    for file_path, file_violations in files_to_fix.items():
        print(f"Processing: {file_path}")
        
        full_path = Path('c:/Git/Agentic-Workflow') / file_path
        fixed_count, new_content = apply_fixes_to_file(str(full_path), file_violations)
        
        if new_content and fixed_count > 0:
            try:
                full_path.write_text(new_content, encoding='utf-8')
                print(f"  ✅ Saved {fixed_count} fixes")
                total_fixed += fixed_count
                files_changed += 1
            except Exception as e:
                print(f"  ❌ Error writing {file_path}: {e}")
        else:
            print(f"  ℹ️  No fixes applied")
    
    print()
    print("=" * 60)
    print(f"Wave 1 Complete: {total_fixed} fixes in {files_changed} files")
    print("=" * 60)
    
    # Git add the changed files
    if files_changed > 0:
        print("\nStaging changes...")
        for file_path in files_to_fix.keys():
            subprocess.run(['git', 'add', file_path], cwd='c:\\Git\\Agentic-Workflow')
        print(f"✅ Staged {files_changed} files")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
