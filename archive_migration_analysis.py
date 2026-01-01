#!/usr/bin/env python3
"""
ULTRA ZERO-LOSS ARCHIVE MIGRATION ANALYSIS
Scans all archive directories, performs AST analysis, hash computation,
and generates migration recommendations.
"""

import ast
import hashlib
import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class FileAnalysis:
    path: str
    size: int
    loc: int
    classes: list = field(default_factory=list)
    functions: list = field(default_factory=list)
    imports: list = field(default_factory=list)
    hash: str = ""
    snippet: str = ""
    docstring: str = ""
    issues: list = field(default_factory=list)
    action: str = ""
    justification: str = ""
    target_path: str = ""
    risk: str = ""

def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8', errors='replace')).hexdigest()[:16]

def count_loc(content: str) -> int:
    return len([l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')])

def parse_python_file(content: str) -> dict:
    """Parse Python file with AST and extract classes, functions, imports."""
    result = {
        'classes': [],
        'functions': [],
        'imports': [],
        'docstring': '',
        'issues': []
    }
    try:
        tree = ast.parse(content)
        result['docstring'] = ast.get_docstring(tree) or ''
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [getattr(b, 'id', getattr(b, 'attr', str(b))) for b in node.bases]
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                result['classes'].append({
                    'name': node.name,
                    'bases': bases,
                    'methods': methods[:10]  # Limit methods
                })
                # Check sovereignty - PascalCase
                if not node.name[0].isupper() or '_' in node.name:
                    result['issues'].append(f"snake_case class: {node.name}")
            
            elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                result['functions'].append(node.name)
            
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result['imports'].append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                result['imports'].append(module)
                
    except SyntaxError as e:
        result['issues'].append(f"SyntaxError: {e}")
    except Exception as e:
        result['issues'].append(f"ParseError: {e}")
    
    return result

def check_sovereignty_issues(content: str, file_path: str) -> list:
    """Check for sovereignty violations."""
    issues = []
    
    # Check for hardcoded credentials
    cred_patterns = ['api_key=', 'password=', 'secret=', 'token=', 'sk-', 'Bearer ']
    for pattern in cred_patterns:
        if pattern.lower() in content.lower():
            issues.append(f"Potential hardcoded credential: {pattern}")
    
    # Check for raw prompt strings (not SSOT)
    if 'prompt =' in content.lower() and ('"""' in content or "'''" in content):
        issues.append("Raw prompt string detected (not SSOT)")
    
    # Check MCP usage
    if 'mcp' in content.lower():
        if 'MCPHardenedMixin' not in content and 'mcp_hardened' not in content.lower():
            issues.append("MCP usage without hardening mixin")
    
    return issues

def analyze_file(file_path: Path) -> Optional[FileAnalysis]:
    """Analyze a single file."""
    try:
        # Skip binary files and __pycache__
        if '__pycache__' in str(file_path) or file_path.suffix == '.pyc':
            return None
        
        content = file_path.read_text(encoding='utf-8', errors='replace')
        
        analysis = FileAnalysis(
            path=str(file_path.relative_to(Path('C:/Git/Agentic-Workflow'))),
            size=file_path.stat().st_size,
            loc=count_loc(content),
            hash=compute_hash(content),
            snippet=content[:200].replace('\n', '\\n')
        )
        
        if file_path.suffix == '.py':
            parsed = parse_python_file(content)
            analysis.classes = parsed['classes']
            analysis.functions = parsed['functions']
            analysis.imports = parsed['imports']
            analysis.docstring = parsed['docstring'][:100] if parsed['docstring'] else ''
            analysis.issues.extend(parsed['issues'])
            analysis.issues.extend(check_sovereignty_issues(content, str(file_path)))
        
        return analysis
        
    except Exception as e:
        return FileAnalysis(
            path=str(file_path),
            size=0,
            loc=0,
            hash="ERROR",
            snippet=f"Error reading: {e}"
        )

def scan_archives():
    """Scan all archive directories."""
    base = Path('C:/Git/Agentic-Workflow/archives')
    
    # Target directories
    target_dirs = [
        'apps_lic', 'apps_rg', 'apps_shared', 'config', 
        'prompt_governance', 'observability', 'shared',
        'monolithic_configs_20260101', 'core_contracts_monolithic_20260101',
        'runtime'
    ]
    
    all_files = []
    
    # Scan with rglob
    extensions = {'.py', '.yaml', '.yml', '.json', '.md', '.txt', '.toml', '.ini', ''}
    
    for item in base.rglob('*'):
        if item.is_file():
            if '__pycache__' in str(item) or '.pyc' in str(item):
                continue
            if item.suffix in extensions or item.suffix == '':
                analysis = analyze_file(item)
                if analysis:
                    all_files.append(analysis)
    
    return all_files

def find_modern_equivalent(archive_path: str) -> tuple:
    """Find modern equivalent for archived file."""
    modern_base = Path('C:/Git/Agentic-Workflow')
    
    # Mapping rules
    mappings = {
        'archives/apps_lic/': 'apps_lic/',
        'archives/apps_rg/': 'apps_rg/',
        'archives/apps_shared/': 'apps_shared/',
        'archives/config/': 'agentic_core/config/',
        'archives/prompt_governance/': 'agentic_core/prompt_governance/',
        'archives/observability/': 'agentic_core/observability/',
        'archives/shared/mcp/': 'agentic_core/L2_execution/mcp/',
        'archives/shared/safety/': 'agentic_core/L5_safety/',
        'archives/shared/resilience/': 'agentic_core/L4_resilience/',
        'archives/shared/reasoning/': 'agentic_core/L1_cognition/reasoning/',
    }
    
    for archive_prefix, modern_prefix in mappings.items():
        if archive_path.startswith(archive_prefix):
            potential = archive_path.replace(archive_prefix, modern_prefix)
            full_path = modern_base / potential
            if full_path.exists():
                return (potential, True)
            # Check for similar files in the directory
            parent = full_path.parent
            if parent.exists():
                similar = list(parent.glob(f"*{full_path.stem}*"))
                if similar:
                    return (str(similar[0].relative_to(modern_base)), True)
            return (potential, False)
    
    return ("", False)

def classify_action(analysis: FileAnalysis, modern_equiv: str, modern_exists: bool) -> tuple:
    """Classify the action for a file."""
    
    # Check if file is empty or stub
    if analysis.loc < 5:
        return ("DELETE", "Empty/stub file", "LOW")
    
    # Check for deprecated markers
    if 'deprecated' in analysis.path.lower() or 'deprecated' in analysis.snippet.lower():
        return ("DELETE", "Marked as deprecated", "LOW")
    
    # Check for hardcoded credentials
    cred_issues = [i for i in analysis.issues if 'credential' in i.lower()]
    if cred_issues:
        return ("REWRITE", f"Security: {cred_issues[0]}", "HIGH")
    
    # Check for sovereignty issues
    if analysis.issues:
        return ("REWRITE", f"Sovereignty issues: {len(analysis.issues)} found", "MEDIUM")
    
    # Check if modern equivalent exists
    if modern_exists:
        return ("DELETE", f"Modern equivalent exists: {modern_equiv}", "LOW")
    
    # Unique logic - should migrate
    if analysis.classes or (analysis.functions and analysis.loc > 50):
        return ("MIGRATE", "Unique logic to preserve", "MEDIUM")
    
    # Config files
    if analysis.path.endswith(('.yaml', '.yml', '.json')):
        if 'config' in analysis.path.lower() or 'prompt' in analysis.path.lower():
            return ("MERGE", "Config to merge with modern SSOT", "MEDIUM")
    
    return ("MIGRATE", "Review for integration", "LOW")

def generate_report(analyses: list):
    """Generate the migration report."""
    
    print("\n" + "="*100)
    print("STEP 1: ZERO-LOSS DISCOVERY RESULTS")
    print("="*100)
    
    # Summary stats
    total_files = len(analyses)
    total_loc = sum(a.loc for a in analyses)
    py_files = [a for a in analyses if a.path.endswith('.py')]
    config_files = [a for a in analyses if a.path.endswith(('.yaml', '.yml', '.json'))]
    
    print(f"\nTotal Files: {total_files}")
    print(f"Total LOC: {total_loc}")
    print(f"Python Files: {len(py_files)}")
    print(f"Config Files: {len(config_files)}")
    
    # Table output
    print("\n| Path | Size | LOC | Classes | Hash | Snippet |")
    print("|------|------|-----|---------|------|---------|")
    
    for a in sorted(analyses, key=lambda x: x.path):
        classes_str = ', '.join([c['name'] for c in a.classes][:3]) if a.classes else '-'
        snippet = a.snippet[:50].replace('|', '\\|') + '...' if len(a.snippet) > 50 else a.snippet.replace('|', '\\|')
        print(f"| {a.path} | {a.size} | {a.loc} | {classes_str} | {a.hash} | {snippet} |")
    
    print("\n" + "="*100)
    print("STEP 2: SOVEREIGNTY ANALYSIS")
    print("="*100)
    
    issues_count = 0
    for a in analyses:
        if a.issues:
            issues_count += 1
            print(f"\n{a.path}:")
            for issue in a.issues:
                print(f"  - {issue}")
    
    print(f"\nFiles with sovereignty issues: {issues_count}/{total_files}")
    
    print("\n" + "="*100)
    print("STEP 3: MIGRATION RECOMMENDATIONS")
    print("="*100)
    
    recommendations = []
    for a in analyses:
        modern_equiv, modern_exists = find_modern_equivalent(a.path)
        action, justification, risk = classify_action(a, modern_equiv, modern_exists)
        a.action = action
        a.justification = justification
        a.risk = risk
        a.target_path = modern_equiv
        recommendations.append(a)
    
    # Summary by action
    actions = {}
    for r in recommendations:
        actions[r.action] = actions.get(r.action, 0) + 1
    
    print("\nAction Summary:")
    for action, count in sorted(actions.items()):
        print(f"  {action}: {count} files")
    
    print("\n| Archive File | Size/LOC | Modern Equivalent | Action | Justification | Risk | Target Path |")
    print("|--------------|----------|-------------------|--------|---------------|------|-------------|")
    
    for r in sorted(recommendations, key=lambda x: (x.action, x.path)):
        print(f"| {r.path} | {r.size}/{r.loc} | {r.target_path or 'N/A'} | {r.action} | {r.justification} | {r.risk} | {r.target_path or 'TBD'} |")
    
    return recommendations

def generate_implementation_diffs(recommendations: list):
    """Generate implementation commands."""
    
    print("\n" + "="*100)
    print("STEP 4: IMPLEMENTATION DIFFS")
    print("="*100)
    
    print("\n# Branch creation")
    print("git checkout -b refactor/migrate-all-archives-2026")
    
    print("\n# DELETE actions (obsolete files)")
    for r in recommendations:
        if r.action == "DELETE":
            print(f"git rm {r.path}  # {r.justification}")
    
    print("\n# MIGRATE actions (preserve history)")
    for r in recommendations:
        if r.action == "MIGRATE" and r.target_path:
            print(f"git mv {r.path} {r.target_path}  # Unique logic")
    
    print("\n# REWRITE actions (security/sovereignty fixes needed)")
    for r in recommendations:
        if r.action == "REWRITE":
            print(f"# MANUAL REVIEW: {r.path}")
            print(f"#   Issues: {r.justification}")
            print(f"#   Target: {r.target_path or 'TBD'}")
    
    print("\n# MERGE actions (combine with modern)")
    for r in recommendations:
        if r.action == "MERGE":
            print(f"# MERGE: {r.path} -> {r.target_path or 'TBD'}")

def main():
    print("="*100)
    print("ULTRA ZERO-LOSS ARCHIVE MIGRATION ANALYSIS")
    print("Generated: 2026-01-01")
    print("="*100)
    
    analyses = scan_archives()
    recommendations = generate_report(analyses)
    generate_implementation_diffs(recommendations)
    
    print("\n" + "="*100)
    print("STEP 5: VALIDATION PLAN")
    print("="*100)
    print("""
# Post-migration validation commands:
python canon_validator_agentic_v2_thin.py --target .
pytest apps_lic/ apps_rg/ apps_shared/ -v
mypy apps_lic/ apps_rg/ apps_shared/ --ignore-missing-imports

# Agent discovery verification:
python -c "from agentic_core import discover_agents; print(f'Agents: {len(discover_agents())}')"

# Rollback if needed:
git reset --hard origin/main
""")
    
    print("\n" + "="*100)
    print("STEP 6: FINAL SUMMARY")
    print("="*100)
    
    total = len(recommendations)
    by_action = {}
    by_risk = {}
    total_loc = 0
    
    for r in recommendations:
        by_action[r.action] = by_action.get(r.action, 0) + 1
        by_risk[r.risk] = by_risk.get(r.risk, 0) + 1
        total_loc += r.loc
    
    print(f"""
MIGRATION SUMMARY:
- Total archived files analyzed: {total}
- Total LOC in archives: {total_loc}

BY ACTION:
{chr(10).join(f'  - {k}: {v} files' for k, v in sorted(by_action.items()))}

BY RISK:
{chr(10).join(f'  - {k}: {v} files' for k, v in sorted(by_risk.items()))}

SOVEREIGNTY GAINS (after migration):
- All snake_case classes → PascalCase
- All raw prompts → SSOT templates
- All MCP usage → Hardened mixins
- All hardcoded creds → Environment variables
""")
    
    # Save JSON report
    report_data = [{
        'path': r.path,
        'size': r.size,
        'loc': r.loc,
        'classes': r.classes,
        'hash': r.hash,
        'issues': r.issues,
        'action': r.action,
        'justification': r.justification,
        'risk': r.risk,
        'target_path': r.target_path
    } for r in recommendations]
    
    with open('archive_migration_report.json', 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print("\nJSON report saved to: archive_migration_report.json")

if __name__ == '__main__':
    main()
