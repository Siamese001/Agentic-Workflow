"""
plan_table_inventory.py — W1.1 format audit script

Read-only scan of .windsurf/plans/*.md to inventory table patterns.
Outputs JSON artifact for plan-format-simplification-rca-d4f8e2 W1.1.
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class PlanInventory:
    plan_name: str
    total_tables: int
    status_tables: int  # Tables with 🔲, ✅, 🔄, ❌ in cells
    artifact_tables: int  # Tables with "Artifact" or "Path" headers
    acceptance_tables: int  # Tables with "Acceptance" or "Criteria" headers
    nested_tables: int  # Tables within tables (approximate)
    has_status_in_table: bool  # Status emojis found inside table cells
    has_simplified_markers: bool  # WAVE_STATUS, PHASE_STATUS markers outside tables
    compatible: bool  # Already compatible with simplified format


def extract_tables(content: str) -> List[str]:
    """Extract table blocks from markdown content."""
    tables = []
    lines = content.split('\n')
    in_table = False
    table_lines = []
    
    for line in lines:
        if line.startswith('|') and '|' in line[1:]:
            in_table = True
            table_lines.append(line)
        elif in_table and line.strip() == '':
            in_table = False
            if table_lines:
                tables.append('\n'.join(table_lines))
                table_lines = []
        elif in_table:
            table_lines.append(line)
    
    if table_lines:
        tables.append('\n'.join(table_lines))
    
    return tables


def is_status_table(table: str) -> bool:
    """Check if table contains status emojis in cells."""
    status_emojis = ['🔲', '✅', '🔄', '❌']
    lines = table.split('\n')
    for line in lines:
        if line.startswith('|'):
            for emoji in status_emojis:
                if emoji in line:
                    return True
    return False


def is_artifact_table(table: str) -> bool:
    """Check if table appears to be an artifact listing."""
    artifact_keywords = ['artifact', 'path', 'file', 'output', 'produced']
    header = table.split('\n')[0].lower() if table else ''
    return any(kw in header for kw in artifact_keywords)


def is_acceptance_table(table: str) -> bool:
    """Check if table appears to be acceptance criteria."""
    acceptance_keywords = ['acceptance', 'criteria', 'metric', 'target', 'verification']
    header = table.split('\n')[0].lower() if table else ''
    return any(kw in header for kw in acceptance_keywords)


def has_nested_tables(content: str, tables: List[str]) -> int:
    """Approximate nested table detection (tables close together)."""
    if len(tables) <= 1:
        return 0
    
    # Count table blocks separated by only whitespace
    nested = 0
    lines = content.split('\n')
    table_indices = []
    
    for i, line in enumerate(lines):
        if line.startswith('|') and '|' in line[1:]:
            table_indices.append(i)
    
    # If tables are within 3 lines of each other, consider nested
    for i in range(len(table_indices) - 1):
        if table_indices[i + 1] - table_indices[i] < 4:
            nested += 1
    
    return nested


def has_simplified_markers(content: str) -> bool:
    """Check if plan has WAVE_STATUS / PHASE_STATUS markers outside tables."""
    has_wave_status = re.search(r'^WAVE_STATUS:\s*\w+', content, re.MULTILINE) is not None
    has_phase_status = re.search(r'PHASE_STATUS:\s*\w+', content) is not None
    return has_wave_status and has_phase_status


def has_status_in_table_cells(content: str, tables: List[str]) -> bool:
    """Check if any table has status emojis in cells."""
    for table in tables:
        if is_status_table(table):
            return True
    return False


def analyze_plan(plan_path: Path) -> PlanInventory:
    """Analyze a single plan file."""
    content = plan_path.read_text(encoding='utf-8')
    tables = extract_tables(content)
    
    status_tables = sum(1 for t in tables if is_status_table(t))
    artifact_tables = sum(1 for t in tables if is_artifact_table(t))
    acceptance_tables = sum(1 for t in tables if is_acceptance_table(t))
    nested = has_nested_tables(content, tables)
    
    has_status_in_table = has_status_in_table_cells(content, tables)
    has_simplified = has_simplified_markers(content)
    
    # Compatible if it has simplified markers AND no status in tables
    compatible = has_simplified and not has_status_in_table
    
    return PlanInventory(
        plan_name=plan_path.name,
        total_tables=len(tables),
        status_tables=status_tables,
        artifact_tables=artifact_tables,
        acceptance_tables=acceptance_tables,
        nested_tables=nested,
        has_status_in_table=has_status_in_table,
        has_simplified_markers=has_simplified,
        compatible=compatible
    )


def main():
    repo_root = Path(__file__).resolve().parents[2]
    plans_dir = repo_root / '.windsurf' / 'plans'
    artifact_dir = repo_root / 'artifacts'
    artifact_dir.mkdir(parents=True, exist_ok=True)
    
    # Scan all .md files in plans directory
    plan_files = list(plans_dir.glob('*.md'))
    
    inventories = []
    for plan_file in plan_files:
        if plan_file.name.startswith('_'):  # Skip _archive, _orphan_review
            continue
        try:
            inv = analyze_plan(plan_file)
            inventories.append(asdict(inv))
        except Exception as e:
            print(f"Error analyzing {plan_file}: {e}")
    
    # Calculate summary statistics
    total_plans = len(inventories)
    total_tables = sum(p['total_tables'] for p in inventories)
    plans_with_status_in_table = sum(1 for p in inventories if p['has_status_in_table'])
    plans_with_simplified = sum(1 for p in inventories if p['has_simplified_markers'])
    compatible_plans = sum(1 for p in inventories if p['compatible'])
    
    # Build output
    output = {
        'scan_timestamp': '2026-05-12',
        'plan_slug': 'plan-format-simplification-rca-d4f8e2',
        'wave': 'W1.1',
        'summary': {
            'total_plans_scanned': total_plans,
            'total_tables_found': total_tables,
            'plans_with_status_in_table': plans_with_status_in_table,
            'plans_with_simplified_markers': plans_with_simplified,
            'already_compatible': compatible_plans,
            'migration_required': total_plans - compatible_plans
        },
        'plans': inventories
    }
    
    # Write artifact
    artifact_path = artifact_dir / 'plan_format_inventory.json'
    artifact_path.write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(f"Wrote {artifact_path}")
    print(f"Scanned {total_plans} plans, {total_tables} tables total")
    print(f"Migration required: {total_plans - compatible_plans} plans")


if __name__ == '__main__':
    main()
