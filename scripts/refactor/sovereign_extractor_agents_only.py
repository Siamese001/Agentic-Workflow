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

import ast
import json
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
import sys
import os
import shutil

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class SurgicalRemapper:
    """
    Handles automated import remapping across the entire codebase.
    Ensures that when a class is extracted, all imports are updated atomically.
    """
    
    def __init__(self, root_dir: Path, dry_run: bool = True):
        self.root_dir = root_dir
        self.dry_run = dry_run
        self.remap_log: List[Dict] = []
    
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
        Remap imports in a single file.
        
        Handles various import patterns:
        - from .old_module import ClassName
        - from ..old_module import ClassName
        - from package.old_module import ClassName
        - from .old_module import ClassName, OtherClass
        """
        updated = content
        
        # Pattern 1: Relative import - from .old_module import ClassName
        pattern1 = rf'from \.{re.escape(old_module.split(".")[-1])} import ([^;\n]*{re.escape(class_name)}[^;\n]*)'
        
        def replace1(match):
            imports = match.group(1)
            # If multiple imports, only replace the specific class
            if ',' in imports:
                # Keep other imports from old module, add new import for extracted class
                other_imports = [imp.strip() for imp in imports.split(',') if imp.strip() != class_name]
                result = f'from .{old_module.split(".")[-1]} import {", ".join(other_imports)}\n'
                result += f'from .{new_module.split(".")[-1]} import {class_name}'
                return result
            else:
                # Single import, just update the module
                return f'from .{new_module.split(".")[-1]} import {class_name}'
        
        updated = re.sub(pattern1, replace1, updated)
        
        # Pattern 2: Absolute import - from package.module import ClassName
        # Extract the base package from old_module
        old_parts = old_module.split('.')
        new_parts = new_module.split('.')
        
        # Find common prefix
        for i in range(min(len(old_parts), len(new_parts))):
            if old_parts[i] != new_parts[i]:
                break
        
        # Build absolute import patterns
        for depth in range(len(old_parts)):
            old_abs = '.'.join(old_parts[:len(old_parts)-depth])
            new_abs = '.'.join(new_parts[:len(new_parts)-depth])
            
            if old_abs:
                pattern_abs = rf'from {re.escape(old_abs)} import ([^;\n]*{re.escape(class_name)}[^;\n]*)'
                
                def replace_abs(match):
                    imports = match.group(1)
                    if ',' in imports:
                        other_imports = [imp.strip() for imp in imports.split(',') if imp.strip() != class_name]
                        if other_imports:
                            result = f'from {old_abs} import {", ".join(other_imports)}\n'
                            result += f'from {new_abs} import {class_name}'
                            return result
                        else:
                            return f'from {new_abs} import {class_name}'
                    else:
                        return f'from {new_abs} import {class_name}'
                
                updated = re.sub(pattern_abs, replace_abs, updated)
        
        return updated


class AgentOnlyExtractor:
    """
    Extracts only agent classes from multi-agent files.
    Uses agent_discovery_full.json as the source of truth.
    """
    
    def __init__(self, root_dir: str, dry_run: bool = True):
        self.root_dir = Path(root_dir)
        self.dry_run = dry_run
        self.agent_registry = self._load_agent_registry()
        self.multi_agent_files = self._identify_multi_agent_files()
        self.remapper = SurgicalRemapper(self.root_dir, dry_run)
        self.extraction_mapping: Dict[str, Dict[str, str]] = {}
        self.backup_dir = self.root_dir / ".refactor_backups"
        
        if not dry_run:
            self.backup_dir.mkdir(exist_ok=True)
        
    def _load_agent_registry(self) -> List[Dict]:
        """Load the agent discovery registry."""
        registry_path = self.root_dir / "agent_discovery_full.json"
        
        if not registry_path.exists():
            raise FileNotFoundError(
                f"Agent registry not found: {registry_path}\n"
                "Run: python scripts/full_agent_discovery.py"
            )
        
        with open(registry_path, 'r') as f:
            return json.load(f)
    
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
        print(f"   Files updated: {total_files_updated}")
        print(f"   Classes remapped: {len(self.extraction_mapping)}")
        
        return total_files_updated
    
    def run(self, pilot_file: str = None):
        """
        Execute the agent-only extraction with surgical remapping.
        
        Args:
            pilot_file: Optional single file to process as pilot (e.g., "SignalRouterAgent.py")
        """
        print("="*80)
        print("SOVEREIGN EXTRACTOR: Agent Classes Only (SURGICAL)")
        print("="*80)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE EXTRACTION'}")
        print(f"Agent registry: {len(self.agent_registry)} agents")
        print(f"Multi-agent files: {len(self.multi_agent_files)}")
        print()
        
        # Filter to pilot file if specified
        if pilot_file:
            print(f"🎯 PILOT MODE: Processing only {pilot_file}")
            files_to_process = {
                path: agents 
                for path, agents in self.multi_agent_files.items()
                if pilot_file in path
            }
            if not files_to_process:
                print(f"❌ Pilot file not found: {pilot_file}")
                return 0
        else:
            files_to_process = self.multi_agent_files
        
        # Calculate totals
        total_extractions = sum(
            len(agents) - 1  # Keep first, extract rest
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
    extractor.run(pilot_file=args.pilot)


if __name__ == "__main__":
    main()
