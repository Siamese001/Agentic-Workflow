from collections import defaultdict
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from pathlib import Path
from typing import Dict, List, Tuple
import shutil
from agentic_core.config.blueprint_sovereign.structure_blueprint import FORBIDDEN_ROOT_FOLDERS, CORE_SUBFOLDER_MAP
# [PHASE 20] DEPRECATION: void_compliance.py removed
def get_placement_guidance(content_preview):
    """Bridge function for placement heuristics."""
    if any(x in content_preview for x in ['planner', 'strategy', 'reasoning', 'mission']):
        return 'agentic_core/L1_cognition'
    if 'node' in content_preview.lower() or 'execute' in content_preview:
        return 'agentic_core/L1_cognition/thought_engine'
    if any(x in content_preview for x in ['router', 'orchestrator', 'fission', 'hop']):
        return 'agentic_core/L3_orchestration'
    if any(x in content_preview for x in ['pinecone', 'redis', 'storage', 'cache']):
        return 'agentic_core/L4_state'
    return 'agentic_core/L1_cognition'

class filename_uniqueness_guardian:
    """
    Batch agent that enforces unique filenames across the entire repository.
    
    Rule: No two Python files may share the same basename (e.g., sovereign_agent.py)
    
    [SURGERY] When RUN_HIERARCHY_HEALING=True: Auto-rename duplicates to sovereign locations
    Activation: Runs in Phase 2 batch sweep via auto-discovery.
    """

    def __init__(self, allow_same_dir_duplicates: bool=False):
        self.allow_same_dir = allow_same_dir_duplicates
        self.duplicates: Dict[str, List[Path]] = defaultdict(list)
        self.renamed_count = 0
        self.errors = []

    def scan_repository(self, python_files: List[str], project_root: Path) -> Any:
        """Core scan logic — identifies non-unique filenames across territories"""
        print('\n[*] FilenameUniquenessGuardian: Enforcing atomic filename sovereignty...')
        basename_to_paths: Any = defaultdict(list)
        for file_str in python_files:
            file_path: Any = Path(file_str)
            if not file_path.exists():
                continue
            basename: Any = file_path.name
            basename_to_paths[basename].append(file_path)
        for basename, paths in basename_to_paths.items():
            if len(paths) > 1:
                if self.allow_same_dir:
                    parents: Any = {p.parent for p in paths}
                    if len(parents) == 1:
                        continue
                self.duplicates[basename] = paths
                print(f'   [!] DUPLICATE FILENAME: {basename} ({len(paths)} occurrences)')
                for p in paths:
                    rel: Any = p.relative_to(project_root)
                    print(f'      -> {rel}')
        if not self.duplicates:
            print('   [OK] All filenames are uniquely sovereign.')
        else:
            print(f'   [VIOLATION] {len(self.duplicates)} filename(s) lack atomic ownership.')

    def _suggest_sovereign_name(self, file_path: Path, project_root: Path) -> Path:
        """Use void_compliance heuristics to suggest correct L1/L2 home and unique name."""
        try:
            preview = file_path.read_text(encoding='utf-8', errors='ignore')[:2048]
            suggested = get_placement_guidance(preview)
            if not suggested or suggested == 'unknown':
                suggested = 'agentic_core/utils/general_helpers'
            parts = suggested.split('/')
            l1, l2 = (parts[-2], parts[-1])
            target_dir = project_root / 'agentic_core' / l1 / l2
            new_path = target_dir / file_path.name
            stem, suffix = (file_path.stem, file_path.suffix)
            counter = 1
            while new_path.exists():
                new_path = target_dir / f'{stem}_dup{counter}{suffix}'
                counter += 1
            return new_path
        except Exception as e:
            self.errors.append(f'Guidance failed for {file_path}: {e}')
            return file_path.with_name(f'RECOVERY_{file_path.name}')

    async def auto_rename_duplicates(self, project_root: Path, ctx: Any) -> Any:
        """[L6 SURGERY] Physically rename/move duplicates to sovereign homes."""
        if not getattr(ctx, 'RUN_HIERARCHY_HEALING', False):
            print('   [INFO] Auto-rename disabled (RUN_HIERARCHY_HEALING=False)')
            return
        print('\n[*] AUTO-RENAME SURGERY: Resolving duplicate filenames...')
        for basename, paths in self.duplicates.items():
            primary: Any = paths[0]
            duplicates: Any = paths[1:]
            for dup_path in duplicates:
                try:
                    new_path: Any = self._suggest_sovereign_name(dup_path, project_root)
                    rel_new: Any = new_path.relative_to(project_root)
                    if rel_new.parts[0] in FORBIDDEN_ROOT_FOLDERS:
                        print(f'      [!] Blocked forbidden move: {rel_new}')
                        continue
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(dup_path), str(new_path))
                    print(f'      [✓] RENAMED: {dup_path.name} → {rel_new}')
                    self.renamed_count += 1
                    if hasattr(ctx, 'audit_log'):
                        ctx.audit_log.record(file_name=basename, action='RENAMED_DUPLICATE', source=str(dup_path.relative_to(project_root)), destination=str(rel_new), reason='Filename uniqueness surgery')
                except Exception as e:
                    self.errors.append(str(e))

    async def execute(self, ctx: Any) -> Any:
        """Batch agent interface — receives ctx with python_files and project_root"""
        if not hasattr(ctx, 'python_files') or not hasattr(ctx, 'project_root'):
            print('   [!] Missing context for uniqueness scan')
            return
        project_root: Any = Path(ctx.project_root)
        self.scan_repository(ctx.python_files, project_root)
        await self.auto_rename_duplicates(project_root, ctx)
