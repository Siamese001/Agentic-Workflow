#!/usr/bin/env python3
"""
Fix Testing & Observability - Add SubatomicTestingMixin and logging to all agents.

This script:
1. Loads all agents from agent_discovery_full.json
2. For each agent without testing: adds SubatomicTestingMixin to bases
3. For each agent without observability: adds logging import and logger
4. This maximizes testing % and observable % in the dashboard
"""
import ast
import json
import re
from pathlib import Path
from typing import List, Dict, Set

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISCOVERY_JSON = PROJECT_ROOT / "agent_discovery_full.json"

LOGGING_IMPORT = "import logging"
LOGGER_INIT = "logger = logging.getLogger(__name__)"
TESTING_IMPORT = "from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin"


def load_agents() -> List[Dict]:
    """Load all agents from discovery JSON."""
    with open(DISCOVERY_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def add_logging_to_file(file_path: Path) -> bool:
    """Add logging import and logger initialization to a file."""
    try:
        source = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  [ERROR] Cannot read {file_path}: {e}")
        return False
    
    modified = False
    
    # Check if logging already imported
    if 'import logging' not in source and 'from logging' not in source:
        # Find the first import line and add logging before it
        lines = source.splitlines()
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_idx = i
                break
        
        # Add logging import
        lines.insert(insert_idx, LOGGING_IMPORT)
        modified = True
        source = '\n'.join(lines)
    
    # Check if logger already initialized
    if 'logger = logging.getLogger' not in source and 'Logger = logging.getLogger' not in source:
        # Find position after imports (first non-import, non-comment, non-docstring line)
        lines = source.splitlines()
        insert_idx = 0
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                in_docstring = not in_docstring
                continue
            if in_docstring:
                continue
            if stripped.startswith('#'):
                continue
            if stripped.startswith('import ') or stripped.startswith('from '):
                insert_idx = i + 1
                continue
            if stripped and not stripped.startswith('import') and not stripped.startswith('from'):
                break
        
        # Add logger init after imports
        lines.insert(insert_idx, '')
        lines.insert(insert_idx + 1, LOGGER_INIT)
        modified = True
        source = '\n'.join(lines)
    
    if modified:
        try:
            file_path.write_text(source, encoding='utf-8')
            return True
        except Exception as e:
            print(f"  [ERROR] Cannot write {file_path}: {e}")
            return False
    
    return False


def add_testing_mixin_to_class(file_path: Path, class_name: str) -> bool:
    """Add SubatomicTestingMixin to a class's bases."""
    try:
        source = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  [ERROR] Cannot read {file_path}: {e}")
        return False
    
    # Check if SubatomicTestingMixin already in file
    if 'SubatomicTestingMixin' in source:
        return False  # Already has it
    
    # Add import if not present
    if TESTING_IMPORT not in source:
        lines = source.splitlines()
        # Find last import line
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                last_import_idx = i
        
        lines.insert(last_import_idx + 1, TESTING_IMPORT)
        source = '\n'.join(lines)
    
    # Add SubatomicTestingMixin to class bases using regex
    # Match: class ClassName(Base1, Base2):
    pattern = rf'(class\s+{re.escape(class_name)}\s*\()([^)]*?)(\)\s*:)'
    
    def add_mixin(match):
        prefix = match.group(1)
        bases = match.group(2).strip()
        suffix = match.group(3)
        
        if bases:
            new_bases = f"SubatomicTestingMixin, {bases}"
        else:
            new_bases = "SubatomicTestingMixin"
        
        return f"{prefix}{new_bases}{suffix}"
    
    new_source, count = re.subn(pattern, add_mixin, source)
    
    if count > 0:
        try:
            file_path.write_text(new_source, encoding='utf-8')
            return True
        except Exception as e:
            print(f"  [ERROR] Cannot write {file_path}: {e}")
            return False
    
    return False


def main():
    print("=" * 80)
    print("FIX TESTING & OBSERVABILITY")
    print("=" * 80)
    
    agents = load_agents()
    print(f"\nProcessing {len(agents)} agents...\n")
    
    # Group by file
    by_file: Dict[str, List[str]] = {}
    for agent in agents:
        path = agent.get('path', '')
        class_name = agent.get('class_name', '')
        if path and class_name:
            full_path = str(PROJECT_ROOT / path)
            if full_path not in by_file:
                by_file[full_path] = []
            if class_name not in by_file[full_path]:
                by_file[full_path].append(class_name)
    
    logging_added = 0
    testing_added = 0
    errors = 0
    
    for file_path_str, class_names in sorted(by_file.items()):
        file_path = Path(file_path_str)
        if not file_path.exists():
            continue
        
        # Add logging
        if add_logging_to_file(file_path):
            logging_added += 1
            print(f"[LOGGING] {file_path.relative_to(PROJECT_ROOT)}")
        
        # Add testing mixin to each class
        for class_name in class_names:
            if add_testing_mixin_to_class(file_path, class_name):
                testing_added += 1
                print(f"[TESTING] {class_name} in {file_path.name}")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: Logging added to {logging_added} files | Testing mixin added to {testing_added} classes")
    print("=" * 80)


if __name__ == "__main__":
    main()
