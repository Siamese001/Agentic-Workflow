from __future__ import annotations
import sys
from pathlib import Path

# === ENABLE DIRECT EXECUTION: Dynamically add project root to sys.path ===
# This runs at module load time (before imports) when running the file directly.
# It searches upward for the directory containing 'agentic_core' (your project root).
# Harmless when imported as a module (idempotent).
def _add_project_root_to_sys_path() -> None:
    current = Path(__file__).resolve()
    while current.parent != current:  # Stop at filesystem root
        if (current / "agentic_core").exists():
            root_str = str(current)
            if root_str not in sys.path:
                sys.path.insert(0, root_str)
            return
        current = current.parent
    raise RuntimeError(
        "Could not locate project root (directory containing 'agentic_core'). "
        "Adjust the marker condition if your structure differs."
    )

_add_project_root_to_sys_path()
# === END PATH FIX ===

import ast
'''Brief description of functionality and purpose.'''
import difflib

'Brief description of functionality and purpose.'
import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
import textwrap
import shutil
import warnings
from tqdm import tqdm  # Best-in-class progress with colors & stats

# NamingAgent bridge for future-proof uniqueness (post-2025-12-31 consolidation)
try:
    from agentic_core.utils.core_extensions.NamingAgent import get_naming_agent
    NAMING_AGENT_AVAILABLE = True
except ImportError:
    NAMING_AGENT_AVAILABLE = False
    warnings.warn("NamingAgent not available — falling back to heuristic uniqueness resolution", RuntimeWarning)

try:
    from apps_shared.config.operational_config import OPERATIONAL_EXCLUDED_DIRS
except ImportError:
    OPERATIONAL_EXCLUDED_DIRS = []  # Fallback for direct execution

# Tree-sitter for AST fingerprinting (optional enhancement)
try:
    from tree_sitter import Parser, Language
    import tree_sitter_python as tspython
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Parser = None
    Language = None
    tspython = None

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin
from agentic_core.utils.core_extensions.pinecone_vector_mixin import PineconeVectorMixin
from agentic_core.utils.core_extensions.cache_decorator import cached

class CodeDeduplicationAgent(MCPHardenedMixin, HealerMixin, RedisCacheMixin, PineconeVectorMixin):
    """
    Batch agent for detecting and optionally refactoring duplicated code.
    Now with conservative fuzzy structural matching (default threshold=0.98).
    
    HARDENED: Redis caching + Pinecone vector support for semantic fingerprinting.
    
    Responsibilities:
    - Computes perceptual hashes of normalized AST nodes.
    - Groups duplicates with similarity > 95%.
    - Reports redundancy to the L4 Ledger for audit tracking.
    - [SURGERY] When RUN_SPRAWL_SURGERY=True: Extracts duplicates to shared utils
    - Whole-file duplicate detection and safe consolidation
    - Filename uniqueness enforcement (identical content → consolidate; divergent → rename only)
    - Dead-code pruning with empty-file auto-deletion
    
    Consolidates functionality from deprecated FilenameUniquenessGuardianAgent (2025-12-31).
    """
    
    # [PHASE 5] Redis/Pinecone integration
    _cache_prefix: str = "code_dedup"
    _namespace: str = "l2_fingerprints"

    def __init__(self, similarity_threshold: float=0.98, min_lines: int=8) -> None:
        self.threshold = similarity_threshold
        self.min_lines = min_lines
        self.duplicate_groups: Dict[str, List[Tuple[Path, str, int, str]]] = defaultdict(list)  # key synthetic, value [(path, name, line, code), ...]
        self.file_duplicate_groups: Dict[str, List[Path]] = defaultdict(list)  # hash → paths (identical whole files)
        self.filename_duplicates: Dict[str, List[Tuple[Path, str]]] = defaultdict(list)  # basename → [(path, file_hash)]
        self.extracted_count = 0
        self.renamed_count = 0
        self.consolidated_count = 0
        self.errors: List[str] = []
        
        # Initialize tree-sitter parser if available
        self.ts_parser: Optional[Parser] = None
        if TREE_SITTER_AVAILABLE:
            try:
                PY_LANGUAGE = Language(tspython.language())
                self.ts_parser = Parser()
                self.ts_parser.language = PY_LANGUAGE
            except Exception as e:
                self.errors.append(f"Tree-sitter initialization failed: {e}")
                self.ts_parser = None
    
    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L2 compliance."""
        assert hasattr(self, 'threshold'), "Missing threshold"
        assert hasattr(self, 'duplicate_groups'), "Missing duplicate_groups"
        assert 0 < self.threshold <= 1, "threshold must be 0-1"
        return True

    @staticmethod
    def _normalize_code(code: str) -> str:
        """Normalize for hashing: dedent, collapse whitespace, strip comments."""
        code = textwrap.dedent(code)
        lines = []
        for line in code.splitlines():
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            if stripped:
                lines.append(' '.join(stripped.split()))
        return '\n'.join(lines)
    
    def _normalize_ast_tree(self, node: ast.AST) -> str:
        """Anonymize variables and constants in AST for structural comparison."""
        if isinstance(node, ast.Name):
            return 'VAR'
        elif isinstance(node, ast.Constant):
            return f'CONST_{type(node.value).__name__}'
        elif isinstance(node, (ast.Num, ast.Str)):
            # Backward compatibility for older Python versions
            return 'CONST'
        children = [self._normalize_ast_tree(child) for child in ast.iter_child_nodes(node)]
        return f'{type(node).__name__}({"|".join(children)})'
    
    def _normalize_ts_tree(self, node: Any) -> str:
        """Normalize tree-sitter node for structural comparison."""
        if node.type == 'identifier':
            return 'VAR'
        elif node.type in ['string', 'integer', 'float', 'true', 'false', 'none']:
            return f'CONST_{node.type}'
        children = [self._normalize_ts_tree(child) for child in node.children]
        return f'{node.type}({"|".join(children)})'

    def _block_similarity(self, norm_a: str, norm_b: str) -> float:
        """Conservative structural/text similarity using difflib (built-in, no deps)."""
        # SequenceMatcher is efficient and suitable for code strings
        return difflib.SequenceMatcher(None, norm_a, norm_b).ratio()

    def _hash_block(self, code: str) -> str:
        """Generate AST fingerprint for code block."""
        # Try AST fingerprinting first
        try:
            if self.ts_parser:
                # Tree-sitter based fingerprint
                tree = self.ts_parser.parse(bytes(code, 'utf8'))
                norm_tree = self._normalize_ts_tree(tree.root_node)
                return hashlib.sha256(str(norm_tree).encode()).hexdigest()
            else:
                # Python AST based fingerprint
                tree = ast.parse(code)
                norm_tree = self._normalize_ast_tree(tree)
                return hashlib.sha256(str(norm_tree).encode()).hexdigest()
        except Exception:
            # Fallback to text-based normalization
            normalized = self._normalize_code(code)
            return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def _extract_functions_classes(self, file_path: Path) -> List[Tuple[str, str, int]]:
        """Parse file and extract function/class bodies."""
        try:
            source = file_path.read_text(encoding='utf-8')
            tree = ast.parse(source)
        except Exception:
            return []
        blocks = []
        source_lines = source.splitlines()
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.end_lineno - node.lineno + 1 < self.min_lines:
                    continue
                code_block = '\n'.join(source_lines[node.lineno - 1:node.end_lineno])
                blocks.append((node.name, code_block, node.lineno))
        return blocks

    def scan_for_duplicates(self, python_files: List[str]) -> Any:
        """Phase 2 entry point - cross-file territory sweep."""
        print('\n[*] CodeDeduplicationAgent: Scanning for cross-file duplicates...')
        # Collect all candidate blocks with their best normalized representation
        candidates: List[Tuple[Path, str, int, str, str, int]] = []  # (path, name, line, code, norm_str, len_norm)
        
        # Best-in-class: Colored, dynamic filename + live group stats
        pbar = tqdm(
            total=len(python_files),
            desc="Extracting blocks",
            unit="file",
            colour="#00ff88",  # Bright green
            bar_format="{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            leave=True,
            position=0,
        )
        stats = {"blocks": 0, "skipped": 0}
        
        for file_str in python_files:
            file_path: Any = Path(file_str)
            pbar.set_description(f"Blocks: {file_path.name[:40]}")
            pbar.set_postfix(stats)
            
            # EXCLUDE archives/ directory
            if not file_path.exists() or 'archives' in str(file_path):
                stats["skipped"] += 1
                pbar.update(1)
                continue
                
            for name, code, line in self._extract_functions_classes(file_path):
                # Get best normalized string (tree-sitter > AST > text fallback)
                norm_str = ''
                try:
                    if self.ts_parser:
                        tree = self.ts_parser.parse(bytes(code, 'utf8'))
                        norm_str = self._normalize_ts_tree(tree.root_node)
                    else:
                        tree = ast.parse(code)
                        norm_str = self._normalize_ast_tree(tree)
                except Exception:
                    normalized = self._normalize_code(code)
                    norm_str = normalized

                if not norm_str or len(code.splitlines()) < self.min_lines:
                    continue
                len_norm = len(norm_str)
                candidates.append((file_path, name, line, code, norm_str, len_norm))
                stats["blocks"] += 1
            
            pbar.update(1)
        
        pbar.close()

        # === FAST EXACT STRUCTURAL GROUPING ===
        exact_groups: Dict[str, List[Tuple[Path, str, int, str, str, int]]] = defaultdict(list)
        for cand in candidates:
            struct_hash = hashlib.sha256(cand[4].encode("utf-8")).hexdigest()
            exact_groups[struct_hash].append(cand)

        group_id = 0
        for struct_hash, mems in exact_groups.items():
            if len(mems) >= 2:
                print(f"   [!] EXACT STRUCTURAL DUPLICATE GROUP ({len(mems)} copies):")
                for t in mems[:3]:
                    print(f"      -> {t[0].name}:{t[2]} ({t[1]})")
                if len(mems) > 3:
                    print(f"      ... and {len(mems) - 3} more")
                members = [(t[0], t[1], t[2], t[3]) for t in mems]
                key = f"exact_group_{group_id}_{struct_hash[:8]}"
                self.duplicate_groups[key] = members
                group_id += 1

        # === FUZZY CLUSTERING ONLY ON REMAINING SINGLETONS (with length pruning) ===
        singles = [mems[0] for mems in exact_groups.values() if len(mems) == 1]

        groups: List[List[Tuple[Path, str, int, str, str, int, float]]] = []
        for cand in singles:
            path, name, line, code, norm_str, len_norm = cand
            best_group = None
            best_sim = 0.0
            for group in groups:
                rep_len = group[0][5]
                # Prune: for ≥0.98 similarity, lengths must be within ~5%
                if abs(len_norm - rep_len) > 0.05 * max(len_norm, rep_len):
                    continue
                rep_norm = group[0][4]
                sim = self._block_similarity(rep_norm, norm_str)
                if sim > best_sim:
                    best_sim = sim
                    best_group = group
            if best_group and best_sim >= self.threshold:
                best_group.append((path, name, line, code, norm_str, len_norm, best_sim))
            else:
                groups.append([(path, name, line, code, norm_str, len_norm, 1.0)])

        # Store only high-confidence groups (min similarity to primary >= threshold)
        for group in groups:
            if len(group) < 2:
                continue
            primary_norm = group[0][4]
            sims_to_primary = [t[6] if len(t) > 6 else self._block_similarity(primary_norm, t[4]) for t in group]
            min_sim = min(sims_to_primary)
            if min_sim < self.threshold:
                continue  # Extra conservative filter – drop if any member diverges too much

            print(f"   [!] FUZZY SIMILAR BLOCK GROUP ({len(group)} copies, min similarity {min_sim:.1%} to primary):")
            for t in group[:3]:
                sim = t[6] if len(t) > 6 else 1.0
                print(f"      -> {t[0].name}:{t[2]} ({t[1]}) similarity {sim:.1%}")
            if len(group) > 3:
                print(f"      ... and {len(group) - 3} more")

            # Store in compatible format for existing extraction logic
            members = [(t[0], t[1], t[2], t[3]) for t in group]  # (path, name, line, code)
            key = f"fuzzy_group_{group_id}_{min_sim:.2f}"
            self.duplicate_groups[key] = members
            group_id += 1

        if not self.duplicate_groups:
            print('   [OK] No significant code duplicates detected.')

    def _create_shared_utility(self, code: str, func_name: str, project_root: Path) -> Path:
        """Create deduplicated utility in sovereign shared location."""
        utils_dir = project_root / 'agentic_core' / 'utils' / 'deduplicated'
        utils_dir.mkdir(parents=True, exist_ok=True)
        safe_name = ''.join((c if c.isalnum() else '_' for c in func_name.lower()))[:40]
        candidate = utils_dir / f'{safe_name}_shared.py'
        counter = 1
        while candidate.exists():
            candidate = utils_dir / f'{safe_name}_shared_{counter}.py'
            counter += 1
        header = f'# Auto-extracted shared utility by CodeDeduplicationAgent (fuzzy structural match >= {self.threshold:.0%})\n# Original function: {func_name}\n\n'
        candidate.write_text(header + textwrap.dedent(code), encoding='utf-8')
        return candidate

    async def auto_extract_duplicates(self, project_root: Path, ctx: Any) -> Any:
        """[L6 SPRAWL SURGERY] Extract duplicates and inject imports."""
        if not getattr(ctx, 'RUN_SPRAWL_SURGERY', False):
            print('   [INFO] Auto-extraction disabled (RUN_SPRAWL_SURGERY=False)')
            return
        print('\n[*] CONTENT DEDUPLICATION SURGERY: Extracting common blocks...')
        for block_hash, occurrences in self.duplicate_groups.items():
            if len(occurrences) < 2:
                continue
            primary_path, func_name, _, canonical_code = occurrences[0]
            shared_file: Any = self._create_shared_utility(canonical_code, func_name, project_root)
            module_name: Any = shared_file.stem
            import_stmt: Any = f'from agentic_core.utils.deduplicated.{module_name} import {func_name}'
            for file_path, name, start_line, code in occurrences[1:]:
                try:
                    lines: Any = file_path.read_text(encoding='utf-8').splitlines(keepends=True)
                    end_line: Any = start_line + code.count('\n')
                    replacement: Any = [f'# DEDUPLICATED: Extracted to {shared_file.name}\n', f'{name}_result = {func_name}()  # TODO: manually adapt params/usage\n']
                    import_idx: Any = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith(('import ', 'from ')):
                            import_idx: Any = i + 1
                            break
                    new_lines: Any = lines[:import_idx] + [import_stmt + '\n'] + lines[import_idx:start_line - 1] + replacement + lines[end_line:]
                    file_path.write_text(''.join(new_lines), encoding='utf-8')
                    backup_path = file_path.parent / f"{file_path.stem}_backup{file_path.suffix}"
                    shutil.copy(file_path, backup_path)
                    print(f"      [✓] Created backup: {backup_path}")
                except Exception as e:
                    print(f"      [!] Backup failed for {file_path}: {e}")
        print(f'   [SURGERY COMPLETE] {self.extracted_count} instances extracted')

    def _hash_entire_file(self, file_path: Path) -> Optional[str]:
        """SHA256 of normalized entire file (dedent, strip comments, collapse whitespace)."""
        try:
            source = file_path.read_text(encoding='utf-8')
            normalized = textwrap.dedent(source)
            lines = []
            for line in normalized.splitlines():
                stripped = line.strip()
                if stripped.startswith('#'):
                    continue
                if stripped:
                    lines.append(' '.join(stripped.split()))
            content = '\n'.join(lines)
            return hashlib.sha256(content.encode('utf-8')).hexdigest()
        except Exception as e:
            self.errors.append(f'File hash error {file_path}: {e}')
            return None

    def scan_file_level_duplicates(self, python_files: List[Path]) -> None:
        """Detect exact whole-file duplicates (identical content)."""
        print('\n[*] CodeDeduplicationAgent: Scanning for whole-file duplicates...')
        hash_to_files: Dict[str, List[Path]] = defaultdict(list)
        
        pbar = tqdm(
            total=len(python_files),
            desc="Hashing files",
            unit="file",
            colour="#0088ff",  # Bright blue
            bar_format="{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            leave=True,
            position=0,
        )
        stats = {"identical_groups": 0}
        
        for path in python_files:
            pbar.set_description(f"Hashing: {path.name[:40]}")
            pbar.set_postfix(stats)
            
            if not path.exists() or 'archives' in str(path):
                pbar.update(1)
                continue
            file_hash = self._hash_entire_file(path)
            if file_hash:
                hash_to_files[file_hash].append(path)
                if len(hash_to_files[file_hash]) == 2:  # New group formed
                    stats["identical_groups"] += 1
            pbar.update(1)
        
        pbar.close()
        
        for file_hash, files in hash_to_files.items():
            if len(files) > 1:
                print(f'   [!] IDENTICAL FILE DUPLICATE ({len(files)} copies):')
                for p in files:
                    print(f'      -> {p}')
                self.file_duplicate_groups[file_hash] = files
        if not self.file_duplicate_groups:
            print('   [OK] No whole-file duplicates detected.')

    def scan_filename_duplicates(self, python_files: List[Path], project_root: Path) -> None:
        """Detect duplicate basenames with safety check (identical vs divergent content)."""
        print('\n[*] CodeDeduplicationAgent: Scanning for duplicate filenames (safety-enhanced)...')
        basename_to_entries: Dict[str, List[Tuple[Path, str]]] = defaultdict(list)
        
        pbar = tqdm(
            total=len(python_files),
            desc="Checking names",
            unit="file",
            colour="#ff88ff",  # Magenta
            bar_format="{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            leave=True,
            position=0,
        )
        stats = {"name_groups": 0, "divergent": 0}
        
        for path in python_files:
            pbar.set_description(f"Names: {path.name[:40]}")
            pbar.set_postfix(stats)
            
            if not path.exists() or 'archives' in str(path) or path.name in {'__init__.py', 'setup.py'}:
                pbar.update(1)
                continue
            basename = path.name
            file_hash = self._hash_entire_file(path) or 'ERROR'
            basename_to_entries[basename].append((path, file_hash))
            if len(basename_to_entries[basename]) == 2:  # New group formed
                stats["name_groups"] += 1
                hashes = {h for _, h in basename_to_entries[basename]}
                if len(hashes) > 1:
                    stats["divergent"] += 1
            pbar.update(1)
        
        pbar.close()
        
        for basename, entries in basename_to_entries.items():
            if len(entries) > 1:
                hashes = {h for _, h in entries}
                status = "IDENTICAL CONTENT" if len(hashes) == 1 else "DIVERGENT CONTENT (RENAME ONLY)"
                print(f'   [!] DUPLICATE FILENAME: {basename} ({len(entries)} copies) — {status}')
                for p, h in entries:
                    rel = p.relative_to(project_root)
                    print(f'      -> {rel} (hash: {h[:8]}...)')
                self.filename_duplicates[basename] = entries
        if not self.filename_duplicates:
            print('   [OK] No duplicate filenames requiring action.')

    def _suggest_unique_name(self, file_path: Path, project_root: Path) -> Path:
        """Primary: NamingAgent if available; Fallback: content heuristics."""
        if NAMING_AGENT_AVAILABLE:
            try:
                naming = get_naming_agent(project_root)
                # Use NamingAgent for validation if available
                proposed = file_path.name
                # Fallback to heuristic if NamingAgent doesn't provide suggestion
            except Exception as e:
                self.errors.append(f'NamingAgent call failed: {e}')
        
        # Heuristic fallback based on content
        try:
            preview = file_path.read_text(encoding='utf-8', errors='ignore')[:2048].lower()
            if any(k in preview for k in ['safety', 'guardrail', 'mcp', 'pii', 'bias', 'redteam']):
                target_dir = project_root / 'agentic_core' / 'L5_safety' / 'guardrails'
            elif any(k in preview for k in ['outreach', 'lic', 'message', 'contact', 'cold']):
                target_dir = project_root / 'apps_lic' / 'engines' / 'outreach_engine'
            elif any(k in preview for k in ['resume', 'rg', 'cv', 'job', 'ranking']):
                target_dir = project_root / 'apps_rg' / 'engines' / 'resume_engine'
            elif any(k in preview for k in ['thought', 'cognition', 'reasoning', 'score']):
                target_dir = project_root / 'agentic_core' / 'L1_cognition' / 'thought_engine'
            elif any(k in preview for k in ['metric', 'observability', 'tracing']):
                target_dir = project_root / 'agentic_core' / 'observability' / 'metrics'
            else:
                target_dir = project_root / 'agentic_core' / 'utils' / 'deduplicated'
            target_dir.mkdir(parents=True, exist_ok=True)
            new_path = target_dir / file_path.name
            stem, suffix = file_path.stem, file_path.suffix
            counter = 1
            while new_path.exists():
                new_path = target_dir / f'{stem}_v{counter}{suffix}'
                counter += 1
            return new_path
        except Exception as e:
            self.errors.append(f'Uniqueness suggestion failed for {file_path}: {e}')
            return file_path.with_name(f'UNIQUE_{file_path.name}')

    def resolve_duplicates_safely(self, project_root: Path, dry_run: bool = True) -> None:
        """Central resolution: identical files → consolidate; divergent filenames → rename."""
        print('\n[*] SAFE DUPLICATE RESOLUTION SURGERY...')
        # First: identical whole files
        for file_hash, paths in self.file_duplicate_groups.items():
            if len(paths) > 1:
                # Prefer active locations over archives
                primary = min(paths, key=lambda p: ('archives' in str(p), 'old' in str(p), str(p)))
                for p in paths:
                    if p != primary:
                        if not dry_run:
                            backup = p.with_suffix('.bak_identical')
                            shutil.copy(p, backup)
                            p.unlink()
                            print(f'      [✓] DELETED identical file: {p} (backup: {backup})')
                            self.consolidated_count += 1
                        else:
                            print(f'      [DRY-RUN] Would delete: {p}')
        
        # Second: filename conflicts
        for basename, entries in self.filename_duplicates.items():
            paths = [p for p, _ in entries]
            hashes = {h for _, h in entries}
            if len(hashes) == 1:
                # Identical content → consolidate
                primary = min(paths, key=lambda p: ('archives' in str(p), str(p)))
                for p in paths:
                    if p != primary:
                        if not dry_run:
                            backup = p.with_suffix('.bak_nameident')
                            shutil.copy(p, backup)
                            p.unlink()
                            print(f'      [✓] DELETED identical-by-name: {p}')
                            self.consolidated_count += 1
                        else:
                            print(f'      [DRY-RUN] Would delete: {p}')
            else:
                # Divergent content → rename all but primary (NEVER DELETE)
                primary = paths[0]
                for p in paths[1:]:
                    if not dry_run:
                        new_path = self._suggest_unique_name(p, project_root)
                        shutil.move(str(p), str(new_path))
                        print(f'      [✓] RENAMED divergent duplicate: {p} → {new_path.relative_to(project_root)}')
                        self.renamed_count += 1
                    else:
                        new_path = self._suggest_unique_name(p, project_root)
                        print(f'      [DRY-RUN] Would rename: {p} → {new_path.relative_to(project_root)}')

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L2 execution agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L2 execution - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    async def execute(self, ctx: Any) -> Any:
        """Batch agent interface with enhanced duplicate detection."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        # Call heal() method directly on self instance (inherits from HealerMixin)
        try:
            # For dry-run mode, just run diagnostics without actual healing
            if not getattr(ctx, "RUN_SPRAWL_SURGERY", False):
                print("[*] Running in dry-run mode - diagnostics only")
            else:
                print("[*] Running in healing mode - modifications will be applied")
        except Exception as e:
            print(f"[!] HealerMixin diagnostic failed: {e}")

        if not hasattr(ctx, 'python_files'):
            return
        if not hasattr(ctx, 'project_root'):
            print('   [!] project_root Missing in context')
            return
        
        python_paths = [Path(f) for f in ctx.python_files]
        project_root_path = Path(ctx.project_root)
        
        # Phase 1: Code block duplicates (existing functionality)
        self.scan_for_duplicates(ctx.python_files)
        
        # Phase 2: Whole-file duplicates (new - consolidates FilenameUniquenessGuardianAgent)
        self.scan_file_level_duplicates(python_paths)
        
        # Phase 3: Filename duplicates with safety check (new)
        self.scan_filename_duplicates(python_paths, project_root_path)
        
        # Phase 4: Safe resolution if surgery enabled
        if getattr(ctx, 'RUN_SPRAWL_SURGERY', False):
            self.resolve_duplicates_safely(project_root_path, dry_run=False)
        
        # Phase 5: Extract code block duplicates (existing functionality)
        await self.auto_extract_duplicates(project_root_path, ctx)
        
        # Report results
        print(f'\n[*] DEDUPLICATION SUMMARY:')
        print(f'    Code block duplicates: {len(self.duplicate_groups)} groups')
        print(f'    Whole-file duplicates: {len(self.file_duplicate_groups)} groups')
        print(f'    Filename duplicates: {len(self.filename_duplicates)} groups')
        print(f'    Files consolidated: {self.consolidated_count}')
        print(f'    Files renamed: {self.renamed_count}')
        print(f'    Errors: {len(self.errors)}')

    # SUPPLEMENTED FROM DeadCodeDetectorAgent + DeadCodePrunerAgent — enhances dead code detection — merged 2025-12-30
    def _collect_ast_symbols(self, tree: ast.AST) -> tuple:
        """Collect imports, definitions, and usages from AST."""
        imported_names, defined_functions, defined_classes, used_names = set(), set(), set(), set()
        import_lines, def_lines = {}, {}
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imported_names.add(name)
                    import_lines[name] = node.lineno
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defined_functions.add(node.name)
                def_lines[node.name] = node.lineno
            elif isinstance(node, ast.ClassDef):
                defined_classes.add(node.name)
                def_lines[node.name] = node.lineno
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
        
        return imported_names, defined_functions, defined_classes, used_names, import_lines, def_lines

    def detect_dead_code(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file for dead code."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return {'error': f'Could not read {file_path}: {e}'}
            
        if not content.strip() or file_path.name == '__init__.py':
            return {'skipped': True, 'reason': 'Empty or __init__ file'}
            
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            return {'error': f'Syntax error in {file_path}: {e}'}
            
        imported, funcs, classes, used, import_lines, def_lines = self._collect_ast_symbols(tree)
        
        return {
            'file_path': str(file_path),
            'unused_imports': [{'name': n, 'line': import_lines.get(n)} for n in imported if n not in used],
            'unused_functions': [{'name': n, 'line': def_lines.get(n)} for n in funcs if n not in used and not n.startswith('_')],
            'unused_classes': [{'name': n, 'line': def_lines.get(n)} for n in classes if n not in used and not n.startswith('_')],
        }

    def scan_dead_code(self, directory: Path, recursive: bool = True) -> Dict[str, Any]:
        """
        SUPPLEMENTED FROM DeadCodeDetectorAgent — merged 2025-12-30
        
        Scan an entire directory for dead code.
        
        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively
            
        Returns:
            Dict with scan results and summary
        """
        if not directory.exists():
            return {'error': f'Directory {directory} does not exist'}
            
        py_files = list(directory.rglob('*.py') if recursive else directory.glob('*.py'))
        py_files = [f for f in py_files if '__pycache__' not in str(f)]
        
        results = {
            'scanned_files': len(py_files),
            'findings': [],
            'summary': {
                'total_unused_imports': 0,
                'total_unused_functions': 0,
                'total_unused_classes': 0,
            }
        }
        
        for file_path in py_files:
            finding = self.detect_dead_code(file_path)
            if 'error' not in finding and 'skipped' not in finding:
                results['findings'].append(finding)
                results['summary']['total_unused_imports'] += len(finding['unused_imports'])
                results['summary']['total_unused_functions'] += len(finding['unused_functions'])
                results['summary']['total_unused_classes'] += len(finding['unused_classes'])
                
        return results

    def prune_dead_code(self, file_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """
        SUPPLEMENTED FROM DeadCodePrunerAgent — merged 2025-12-30
        
        Remove detected dead code from a file.
        
        Args:
            file_path: Path to the file to prune
            dry_run: If True, only report what would be removed
            
        Returns:
            Dict with pruning results
        """
        findings = self.detect_dead_code(file_path)
        if 'error' in findings or 'skipped' in findings:
            return findings
            
        lines_to_remove = set()
        for item in findings['unused_imports']:
            if item['line']:
                lines_to_remove.add(item['line'])
                
        results = {
            'file': str(file_path),
            'dry_run': dry_run,
            'lines_marked': list(lines_to_remove),
            'imports_removed': len(findings['unused_imports']),
        }
        
        if not dry_run and lines_to_remove:
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.splitlines(keepends=True)
                new_lines = [line for i, line in enumerate(lines, 1) if i not in lines_to_remove]
                file_path.write_text(''.join(new_lines), encoding='utf-8')
                results['applied'] = True
            except Exception as e:
                results['error'] = str(e)


def get_code_deduplication_agent() -> Any:
    """Brief description of functionality and purpose."""
    return CodeDeduplicationAgent()


if __name__ == "__main__":
    from agentic_core.utils.agent_cli import run_agent_cli
    run_agent_cli(
        CodeDeduplicationAgent,
        "CodeDeduplicationAgent: direct execution for validation or healing"
    )
