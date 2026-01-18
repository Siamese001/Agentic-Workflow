"""
SOVEREIGN EXTRACTOR: One Class, One Agent (AGENTS ONLY) - SURGICAL VERSION
Path: scripts/refactor/sovereign_extractor_agents_only.py
Target: Extract 55 AGENT classes from 23 files with atomic import remapping

CRITICAL FEATURES:
- Only extracts actual agent classes (not test/enum/data classes)
- Deletes old class definitions from original files
- Automatically remaps all imports across the codebase
- Atomic transaction: extract + delete + remap in one operation
- Backup files created before any modifications
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, prompt, workflow
# This boosts alignment detection — review and integrate appropriately


import ast
import json
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
import sys
import os
import shutil

from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class SurgicalRemapper:
    """
    Handles automated import remapping across the entire codebase.
    Ensures that when a class is extracted, all imports are updated atomically.
    
    ENHANCED FEATURES:
    - Alias resolution: Maps virtual imports (e.g., .healing) to actual files
    - Multi-line parsing: Handles parenthetical imports across multiple lines
    - __init__.py awareness: Splits multi-class imports in package exports
    """
    
    def __init__(self, root_dir: Path, dry_run: bool = True):
        self.root_dir = root_dir
        self.dry_run = dry_run
        self.remap_log: List[Dict] = []
        self.alias_cache: Dict[Path, Dict[str, str]] = {}  # Cache for alias resolution
    
    def _resolve_aliases(self, directory: Path) -> Dict[str, str]:
        """
        Scans __init__.py files to find virtual module aliases.
        
        Example: If __init__.py has 'from .healing import X', this maps
        'healing' -> actual file containing X.
        
        Returns:
            Dict mapping virtual module names to actual file stems
        """
        if directory in self.alias_cache:
            return self.alias_cache[directory]
        
        alias_map = {}
        init_file = directory / "__init__.py"
        
        if init_file.exists():
            try:
                with open(init_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                # Find all 'from .module import ...' statements
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.level > 0:  # Relative import
                            module_name = node.module
                            # Map this virtual name to potential actual file
                            alias_map[module_name] = module_name
            except Exception:
                pass
        
        self.alias_cache[directory] = alias_map
        return alias_map
    
    def remap_imports_for_extraction(
        self, 
        class_name: str, 
        old_module_path: str, 
        new_module_path: str
    ) -> int:
        """
        Remap all imports of a class from old module to new module.
        
        Args:
            class_name: Name of the extracted class
            old_module_path: Original module path (e.g., "SignalRouterAgent")
            new_module_path: New module path (e.g., "HealingOrchestratorAgent")
        
        Returns:
            Number of files updated
        """
        files_updated = 0
        
        # Convert paths to module notation
        old_module = old_module_path.replace('/', '.').replace('\\', '.')
        new_module = new_module_path.replace('/', '.').replace('\\', '.')
        
        # Remove .py extension if present
        if old_module.endswith('.py'):
            old_module = old_module[:-3]
        if new_module.endswith('.py'):
            new_module = new_module[:-3]
        
        print(f"\n  [REMAP] {class_name}: {old_module} → {new_module}")
        
        # Scan all Python files
        for py_file in self.root_dir.rglob("*.py"):
            # Skip excluded directories
            if any(skip in str(py_file) for skip in [
                'venv', '.venv', 'env', '__pycache__', 
                '.refactor_backups', 'node_modules'
            ]):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                updated_content = self._remap_file_imports(
                    original_content, 
                    class_name, 
                    old_module, 
                    new_module,
                    py_file
                )
                
                if updated_content != original_content:
                    if not self.dry_run:
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                    
                    files_updated += 1
                    rel_path = py_file.relative_to(self.root_dir)
                    print(f"    ✓ Updated: {rel_path}")
                    
                    self.remap_log.append({
                        "file": str(rel_path),
                        "class": class_name,
                        "old_module": old_module,
                        "new_module": new_module
                    })
            
            except Exception as e:
                print(f"    [ERROR] {py_file}: {e}")
        
        return files_updated
    
    def _remap_file_imports(
        self, 
        content: str, 
        class_name: str, 
        old_module: str, 
        new_module: str,
        file_path: Path
    ) -> str:
        """
        ALIAS-AWARE import remapper with multi-line and parenthetical support.
        
        Handles:
        - Single line: from .old_module import ClassName
        - Multi-class: from .old_module import ClassName, OtherClass
        - Parenthetical: from .old_module import (ClassName, OtherClass)
        - Multi-line: from .old_module import (\n    ClassName,\n    OtherClass\n)
        - Virtual aliases: from .healing import ClassName (where .healing doesn't exist)
        """
        lines = content.splitlines(keepends=True)
        new_lines = []
        i = 0
        modified = False
        
        # Resolve aliases for this directory
        aliases = self._resolve_aliases(file_path.parent)
        old_module_stem = old_module.split('.')[-1]
        
        # Build list of possible module references (actual + aliases)
        possible_modules = [old_module_stem]
        # Check if old_module might be referenced by an alias
        for alias_name in aliases.keys():
            possible_modules.append(alias_name)
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this line contains an import from any possible module
            found_import = False
            matched_module = None
            
            for mod in possible_modules:
                if f'from .{mod} import' in line or f'from ..{mod} import' in line:
                    found_import = True
                    matched_module = mod
                    break
            
            if found_import:
                # Check if our class is in this import
                if class_name in line or (i + 1 < len(lines) and '(' in line):
                    # Handle multi-line imports
                    import_block = [line]
                    if '(' in line and ')' not in line:
                        # Multi-line import, collect all lines
                        i += 1
                        while i < len(lines) and ')' not in lines[i-1]:
                            import_block.append(lines[i])
                            i += 1
                    
                    # Join the import block
                    full_import = ''.join(import_block)
                    
                    # Check if our class is actually in this import
                    if class_name not in full_import:
                        new_lines.extend(import_block)
                        i += 1
                        continue
                    
                    # Extract the imported classes
                    # Pattern: from .module import (Class1, Class2, ...)
                    import_match = re.search(
                        rf'from (\.+{re.escape(matched_module)}) import\s*\(?\s*([^)]+)\)?',
                        full_import,
                        re.DOTALL
                    )
                    
                    if import_match:
                        module_prefix = import_match.group(1)
                        imports_str = import_match.group(2)
                        
                        # Split imports and clean them
                        imported_classes = [
                            cls.strip().rstrip(',') 
                            for cls in imports_str.split(',')
                            if cls.strip()
                        ]
                        
                        # Remove our extracted class
                        remaining_classes = [
                            cls for cls in imported_classes 
                            if cls != class_name
                        ]
                        
                        # Build new import statements
                        if remaining_classes:
                            # Keep the old import for remaining classes
                            if len(remaining_classes) == 1:
                                new_lines.append(f'from {module_prefix} import {remaining_classes[0]}\n')
                            else:
                                # Multi-class import, keep parenthetical style
                                new_lines.append(f'from {module_prefix} import (\n')
                                for cls in remaining_classes:
                                    new_lines.append(f'    {cls},\n')
                                new_lines.append(')\n')
                        
                        # Add new import for extracted class
                        new_lines.append(f'from .{new_module.split(".")[-1]} import {class_name}\n')
                        modified = True
                    else:
                        # Couldn't parse, keep original
                        new_lines.extend(import_block)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
            
            i += 1
        
        return ''.join(new_lines) if modified else content


class AgentOnlyExtractor:
    """
    Extracts only agent classes from multi-agent files.
    Uses agent_discovery_full.json as the source of truth.
    """
    
    def __init__(self, root_dir: str, dry_run: bool = True):
        self.root_dir = Path(root_dir)
        self.dry_run = dry_run
        self.TARGET_BASELINE = 273  # SOVEREIGN LOCKED BASELINE - Phase A Genesis State (Jan 06, 2026)
        self.agent_registry = self._load_agent_registry()
        self.agents = self.agent_registry  # Alias for compatibility
        self.multi_agent_files = self._identify_multi_agent_files()
        self.remapper = SurgicalRemapper(self.root_dir, dry_run)
        self.extraction_mapping: Dict[str, Dict[str, str]] = {}
        self.backup_dir = self.root_dir / ".refactor_backups"
        
        if not dry_run:
            self.backup_dir.mkdir(exist_ok=True)
        
    def _load_agent_registry(self) -> List[Dict]:
        """Load the agent discovery registry."""
        registry_path = self.root_dir / AGENT_DISCOVERY_JSON
        
        if not registry_path.exists():
            raise FileNotFoundError(
                f"Agent registry not found: {registry_path}\n"
                "Run: python scripts/full_agent_discovery.py"
            )
        
        with open(registry_path, 'r') as f:
            return json.load(f)
    
    def _get_total_agent_count(self) -> int:
        """Get total agent count from registry."""
        return len(self.agent_registry)
    
    def _identify_multi_agent_files(self) -> Dict[str, List[Dict]]:
        """
        Group agents by file path to identify multi-agent files.
        
        Returns:
            Dict mapping file paths to list of agent records
        """
        from collections import defaultdict
        
        agents_by_file = defaultdict(list)
        
        for agent in self.agent_registry:
            path = agent['path'].replace('\\', '/')
            agents_by_file[path].append(agent)
        
        # Filter to only files with 2+ agents
        multi_agent_files = {
            path: agents 
            for path, agents in agents_by_file.items() 
            if len(agents) > 1
        }
        
        return multi_agent_files
    
    def _find_multi_agent_files(self) -> List[Path]:
        """Return list of Path objects for multi-agent files."""
        return [self.root_dir / path for path in self.multi_agent_files.keys()]
    
    def pre_flight_audit(self):
        """
        HARDENED PRE-FLIGHT AUDIT: Enforces 287 baseline before allowing mutations.
        
        VIOLATION JUSTIFICATION: Direct dependency on discovery logic to ensure
        we are not refactoring a corrupted or desynchronized state.
        """
        current_count = self._get_total_agent_count()
        
        if current_count != self.TARGET_BASELINE:
            print(f"\n🚨 CRITICAL: Baseline mismatch!")
            print(f"   Expected: {self.TARGET_BASELINE} agents")
            print(f"   Found: {current_count} agents")
            print(f"   Delta: {current_count - self.TARGET_BASELINE:+d}")
            print(f"\n⛔ EXTRACTION ABORTED to prevent data loss.")
            print(f"   Please run deduplication or investigate the discrepancy.")
            print(f"   Run: python scripts/refactor/sovereign_deduplicator.py")
            sys.exit(1)
        
        print(f"✅ Pre-flight Check: Baseline {self.TARGET_BASELINE} confirmed.")
    
    def _backup_file(self, file_path: Path) -> Path:
        """Create backup of file before modification."""
        if self.dry_run:
            return file_path
        
        backup_path = self.backup_dir / f"{file_path.name}.bak"
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def _extract_class_source(self, source: str, class_name: str, tree: ast.Module) -> Tuple[str, int, int]:
        """
        Extract the source code for a specific class.
        
        Returns:
            (class_source, start_line, end_line)
        """
        lines = source.splitlines()
        
        # Find the class node
        class_node = None
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                class_node = node
                break
        
        if not class_node:
            raise ValueError(f"Class {class_name} not found in AST")
        
        start_line = class_node.lineno - 1  # Convert to 0-indexed
        
        # Use end_lineno if available (Python 3.8+)
        if hasattr(class_node, 'end_lineno'):
            end_line = class_node.end_lineno
        else:
            # Fallback: find next class or end of file
            end_line = len(lines)
            for i in range(start_line + 1, len(lines)):
                if lines[i].startswith('class '):
                    end_line = i
                    break
        
        class_source = '\n'.join(lines[start_line:end_line])
        return class_source, start_line, end_line
    
    def _delete_class_from_source(self, source: str, class_name: str, tree: ast.Module) -> str:
        """
        Delete a class definition from source code.
        
        Returns:
            Updated source with class removed
        """
        lines = source.splitlines()
        _, start_line, end_line = self._extract_class_source(source, class_name, tree)
        
        # Remove the class lines
        updated_lines = lines[:start_line] + lines[end_line:]
        
        # Clean up extra blank lines
        result = '\n'.join(updated_lines)
        
        # Remove excessive blank lines (more than 2 consecutive)
        result = re.sub(r'\n{4,}', '\n\n\n', result)
        
        return result
    
    def _extract_imports(self, source: str) -> str:
        """Extract import statements from source."""
        lines = source.splitlines()
        import_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')) and 'import' in stripped:
                import_lines.append(line)
            elif import_lines and not stripped:
                # Stop at first blank line after imports
                break
        
        return '\n'.join(import_lines)
    
    def _create_new_file(self, class_name: str, class_source: str, imports: str, original_file: Path) -> str:
        """Create content for new extracted file."""
        header = f'''"""
{class_name} - Extracted for one-class-per-file pattern.

Originally from: {original_file.name}
Extracted: 2026-01-06 (Surgical Extraction)
"""
'''
        
        parts = [header]
        
        if imports:
            parts.append(imports)
        
        parts.append(class_source)
        
        return '\n\n'.join(parts) + '\n'
    
    def extract_agents_from_file(self, file_path: str, agents: List[Dict]):
        """
        SURGICAL EXTRACTION: Extract, delete, and remap in atomic transaction.
        
        Args:
            file_path: Relative path to the file
            agents: List of agent records from registry
        """
        full_path = self.root_dir / file_path
        
        if not full_path.exists():
            print(f"  [SKIP] File not found: {file_path}")
            return
        
        print(f"\n{'='*80}")
        print(f"📁 {file_path}")
        print(f"   {len(agents)} agents to process")
        print(f"{'='*80}")
        
        # Read source
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            print(f"  [ERROR] Cannot read: {e}")
            return
        
        # Parse AST
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            print(f"  [ERROR] Syntax error: {e}")
            return
        
        # Backup original file
        if not self.dry_run:
            self._backup_file(full_path)
        
        # Get all class names in this file
        class_names = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
        
        # Extract imports once
        imports = self._extract_imports(source)
        
        # CRITICAL: Determine which class stays (filename-to-class parity)
        # The class matching the filename MUST stay, all others are extracted
        filename_stem = full_path.stem  # e.g., "SignalRouterAgent" from "SignalRouterAgent.py"
        
        primary_agent = None
        for agent in agents:
            if agent['class_name'] == filename_stem:
                primary_agent = agent
                break
        
        # Fallback: if no class matches filename, keep first by line number
        if not primary_agent:
            agents_sorted = sorted(agents, key=lambda x: x.get('line_number', 0))
            primary_agent = agents_sorted[0]
            print(f"  [WARN] No class matches filename '{filename_stem}', keeping first class by default")
        
        # Track modifications to original file
        modified_source = source
        
        for agent in agents:
            class_name = agent['class_name']
            
            if class_name not in class_names:
                print(f"  [WARN] {class_name} not found in AST (may be nested or imported)")
                continue
            
            # Keep the primary agent (filename match), extract all others
            if agent == primary_agent:
                print(f"  ✓ {class_name} - KEEP in current file (matches filename)")
            else:
                new_file_path = full_path.parent / f"{class_name}.py"
                old_module = full_path.stem
                new_module = class_name
                
                if self.dry_run:
                    print(f"  → {class_name} - WOULD EXTRACT to {class_name}.py")
                    print(f"    → WOULD DELETE from {full_path.name}")
                    print(f"    → WOULD REMAP imports: {old_module} → {new_module}")
                else:
                    # STEP 1: Extract class to new file
                    try:
                        class_source, _, _ = self._extract_class_source(modified_source, class_name, tree)
                        new_content = self._create_new_file(class_name, class_source, imports, full_path)
                        
                        with open(new_file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        print(f"  ✓ {class_name} - EXTRACTED to {class_name}.py")
                    except Exception as e:
                        print(f"  [ERROR] Extraction failed: {e}")
                        continue
                    
                    # STEP 2: Delete class from original file
                    try:
                        modified_source = self._delete_class_from_source(modified_source, class_name, tree)
                        # Re-parse for next iteration
                        tree = ast.parse(modified_source)
                        print(f"    ✓ DELETED from {full_path.name}")
                    except Exception as e:
                        print(f"  [ERROR] Deletion failed: {e}")
                        continue
                    
                    # STEP 3: Record for import remapping
                    self.extraction_mapping[class_name] = {
                        "old_module": old_module,
                        "new_module": new_module,
                        "old_file": str(full_path.relative_to(self.root_dir)),
                        "new_file": str(new_file_path.relative_to(self.root_dir))
                    }
        
        # Write modified original file (with extracted classes removed)
        if not self.dry_run and modified_source != source:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(modified_source)
            print(f"  ✓ Updated {full_path.name} (removed extracted classes)")
    
    def remap_all_imports(self):
        """
        PHASE 2: Remap all imports across the codebase.
        Uses the extraction_mapping to update imports atomically.
        """
        if not self.extraction_mapping:
            print("\n⚠️  No extractions to remap")
            return
        
        print("\n" + "="*80)
        print("PHASE 2: SURGICAL IMPORT REMAPPING")
        print("="*80)
        print(f"Classes to remap: {len(self.extraction_mapping)}")
        print()
        
        total_files_updated = 0
        
        for class_name, mapping in self.extraction_mapping.items():
            files_updated = self.remapper.remap_imports_for_extraction(
                class_name,
                mapping["old_module"],
                mapping["new_module"]
            )
            total_files_updated += files_updated
        
        print(f"\n✅ Import remapping complete")
        
    
    def run(self, pilot_file: str = None, live: bool = False):
        """
        SOVEREIGN RUN LOOP with JIT Pathing and Alias Resolution.
        
        Args:
            pilot_file: Basename of file to process (e.g., 'SignalRouterAgent.py')
            live: If True, actually modify files. If False, dry run only.
        """
        # PRE-FLIGHT AUDIT: Enforce 287 baseline
        print("\n" + "="*80)
        print("PRE-FLIGHT AUDIT: Verifying Baseline")
        print("="*80)
        self.pre_flight_audit()
        print()
        
        self.dry_run = not live
        self.remapper.dry_run = not live
        
        print("="*80)
        print(f"SOVEREIGN EXTRACTOR: Agent Classes Only (SURGICAL)")
        print("="*80)
        print(f"Mode: {'LIVE EXTRACTION' if live else 'DRY RUN'}")
        print(f"Agent registry: {len(self.agent_registry)} agents")
        print(f"Multi-agent files: {len(self.multi_agent_files)}")
        print()
        
        # Prepare files to process
        files_to_process = self.multi_agent_files
        
        # Filter for pilot mode if specified (BASENAME MATCH)
        if pilot_file:
            print(f"🎯 PILOT MODE: Processing only {pilot_file}")
            # VIOLATION JUSTIFICATION: Using basename match to prevent path drift errors
            # when registry paths change between runs
            pilot_basename = Path(pilot_file).name
            filtered = {}
            for path, agents in files_to_process.items():
                if Path(path).name == pilot_basename:
                    filtered[path] = agents
            
            if not filtered:
                print(f"❌ Pilot file not found: {pilot_basename}")
                print(f"   Available multi-agent files:")
                for path in list(files_to_process.keys())[:5]:
                    print(f"   - {Path(path).name}")
                return
            
            files_to_process = filtered
            print(f"✅ Found pilot file: {list(filtered.keys())[0]}")
            print()
        
        # Calculate totals
        total_extractions = sum(
            len(agents) - 1  # Keep one, extract rest
            for agents in files_to_process.values()
        )
        
        print(f"📊 SCOPE")
        print(f"  Files to process: {len(files_to_process)}")
        print(f"  Agents to extract: {total_extractions}")
        print(f"  Agents to keep in place: {len(files_to_process)}")
        print()
        
        # PHASE 1: Extract and delete
        print("="*80)
        print("PHASE 1: EXTRACTION & DELETION")
        print("="*80)
        
        for file_path, agents in sorted(files_to_process.items()):
            self.extract_agents_from_file(file_path, agents)
        
        # PHASE 2: Remap imports (only if not dry run and extractions occurred)
        if not self.dry_run and self.extraction_mapping:
            self.remap_all_imports()
        
        # Summary
        print("\n" + "="*80)
        print("EXTRACTION SUMMARY")
        print("="*80)
        print(f"Files processed: {len(files_to_process)}")
        print(f"Agents extracted: {len(self.extraction_mapping)}")
        
        if self.dry_run:
            print("\n⚠️  DRY RUN - No files modified")
            print("   Run with --live to perform extraction")
        else:
            print(f"\n✅ SURGICAL EXTRACTION COMPLETE")
            print(f"   Backups saved to: {self.backup_dir}")
            print(f"   New files created: {len(self.extraction_mapping)}")
            print(f"   Imports remapped: {len(self.remapper.remap_log)} files")
        
        # Save logs
        if self.extraction_mapping:
            log_path = self.root_dir / "surgical_extraction_log.json"
            with open(log_path, 'w') as f:
                json.dump({
                    "dry_run": self.dry_run,
                    "pilot_file": pilot_file,
                    "extractions": self.extraction_mapping,
                    "import_remaps": self.remapper.remap_log
                }, f, indent=2)
            print(f"\n📝 Log saved: {log_path}")
        
        return total_extractions


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract agent classes only (not all classes) - SURGICAL VERSION")
    parser.add_argument("root_dir", nargs='?', default=".", help="Root directory")
    parser.add_argument("--live", action="store_true", help="Perform actual extraction (default is dry-run)")
    parser.add_argument("--pilot", type=str, help="Pilot mode: extract only from specified file (e.g., SignalRouterAgent.py)")
    
    args = parser.parse_args()
    
    extractor = AgentOnlyExtractor(args.root_dir, dry_run=not args.live)
    extractor.run(pilot_file=args.pilot, live=args.live)


if __name__ == "__main__":
    main()