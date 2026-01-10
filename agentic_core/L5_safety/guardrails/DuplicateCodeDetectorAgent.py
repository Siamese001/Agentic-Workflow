from __future__ import annotations
#!/usr/bin/env python3
"""
Duplicate Code Detector Agent
Batch agent: Detects exact duplicate files and code blocks across the entire territory.
Supports Python, HTML, CSS, JS, JSON, YAML, Markdown, and other text files.
Uses content hashing for exact duplicates and AST fingerprinting for structural comparison.
"""
import hashlib
import tokenize
import ast
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.mixins import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
import logging

Logger = logging.getLogger(__name__)

# Tree-sitter for AST fingerprinting
try:
    from tree_sitter import Language, Parser
    from tree_sitter_python import language
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Parser = None
    Language = None


@dataclass
class DuplicateFile:
    """Represents a duplicate file with metadata."""
    hash: str
    size: int
    paths: List[Path]
    file_type: str
    keep_path: Optional[Path] = None
    delete_paths: List[Path] = None
    rationale: str = ""


class DuplicateCodeDetectorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Batch agent: Detects exact duplicate files and code blocks across the entire territory.
    Supports multiple file types with appropriate hashing strategies.
    """
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.py', '.html', '.htm', '.css', '.js', '.json', '.yaml', '.yml', 
        '.md', '.txt', '.xml', '.svg', '.toml', '.ini', '.cfg', '.conf'
    }
    
    # Extensions that should use whole-file hashing (not block-based)
    WHOLE_FILE_TYPES = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'}
    
    # Canonical locations (prefer these over others)
    CANONICAL_PREFIXES = [
        'agentic_core/L5_safety',
        'agentic_core/L4_state',
        'agentic_core/L3_orchestration',
        'agentic_core/L2_execution',
        'agentic_core/L1_cognition',
        'agentic_core/L0_maintenance',
        'agentic_core/observability',
        'agentic_core/utils',
    ]
    
    # Directories to exclude from scanning
    EXCLUDE_DIRS = {'archives', '__pycache__', '.git', 'node_modules', 'venv', '.venv', 'dist', 'build'}

    def __init__(self, project_root: Path = None, ctx = None) -> None:
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.ctx = ctx
        self.min_lines = 10  # Minimum block size to flag
        self.max_report = 100  # Limit detailed reporting
        self.auto_deduplicate = False
        
        # Initialize tree-sitter parser if available
        self.ts_parser: Optional[Parser] = None
        if TREE_SITTER_AVAILABLE:
            try:
                self.ts_parser = Parser()
                self.ts_parser.language = language()
            except Exception:
                self.ts_parser = None

    async def execute(self, file_types: Set[str] = None, scan_whole_files: bool = True) -> Dict:
        """Scan files for duplicates.
        
        Args:
            file_types: Set of file extensions to scan (e.g., {'.py', '.html'})
            scan_whole_files: If True, detect exact file duplicates first
            
        Returns:
            Dict with duplicate findings and deletion recommendations
        """
        file_types = file_types or self.SUPPORTED_EXTENSIONS
        
        Logger.info(f"[DUPE SCAN] Scanning for duplicates in {len(file_types)} file types...")
        
        results = {
            "whole_file_duplicates": [],
            "code_block_duplicates": [],
            "deletion_recommendations": []
        }
        
        # Phase 1: Detect exact file duplicates
        if scan_whole_files:
            whole_file_dupes = self._scan_whole_files(file_types)
            results["whole_file_duplicates"] = whole_file_dupes
            results["deletion_recommendations"].extend(self._generate_deletion_plan(whole_file_dupes))
        
        # Phase 2: Detect code block duplicates (Python only for now)
        if '.py' in file_types:
            block_dupes = await self._scan_code_blocks()
            results["code_block_duplicates"] = block_dupes
        
        return results
    
    def _scan_whole_files(self, file_types: Set[str]) -> List[DuplicateFile]:
        """Scan for exact duplicate files by content hash."""
        file_hashes = defaultdict(list)  # hash -> [paths]
        
        for file_path in self._iter_files(file_types):
            try:
                content = file_path.read_bytes()
                file_hash = hashlib.sha256(content).hexdigest()
                file_size = len(content)
                
                file_hashes[file_hash].append((file_path, file_size))
            except Exception as e:
                Logger.warning(f"Failed to read {file_path}: {e}")
                continue
        
        # Find duplicates
        duplicates = []
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                paths = [f[0] for f in files]
                size = files[0][1]
                file_type = paths[0].suffix
                
                duplicate = DuplicateFile(
                    hash=file_hash,
                    size=size,
                    paths=paths,
                    file_type=file_type
                )
                duplicates.append(duplicate)
        
        Logger.info(f"[DUPE SCAN] Found {len(duplicates)} sets of duplicate files")
        return duplicates
    
    async def _scan_code_blocks(self) -> List[Dict]:
        """Scan Python files for duplicate code blocks."""
        code_blocks = defaultdict(list)  # hash -> [(path, start_line)]
        
        for file_path in self._iter_files({'.py'}):
            try:
                lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                
                # Sliding window hash
                for i in range(len(lines) - self.min_lines + 1):
                    block_content = "\n".join(lines[i : i + self.min_lines])
                    if not block_content.strip():
                        continue
                    
                    block_hash = self._hash_block_ast(block_content)
                    try:
                        rel_path = file_path.relative_to(self.project_root)
                    except ValueError:
                        rel_path = file_path
                    code_blocks[block_hash].append((str(rel_path), i + 1))
            
            except Exception as e:
                Logger.warning(f"Failed to scan {file_path}: {e}")
                continue
        
        # Find duplicates
        duplicates = [
            {"hash": h, "locations": locs} 
            for h, locs in code_blocks.items() 
            if len(locs) > 1
        ]
        
        Logger.info(f"[DUPE SCAN] Found {len(duplicates)} duplicate code blocks")
        return duplicates[:self.max_report]
    
    def _iter_files(self, file_types: Set[str]):
        """Iterate over files matching the given extensions."""
        for file_path in self.project_root.rglob('*'):
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in self.EXCLUDE_DIRS):
                continue
            
            # Check extension
            if file_path.suffix in file_types and file_path.is_file():
                yield file_path
    
    def _generate_deletion_plan(self, duplicates: List[DuplicateFile]) -> List[Dict]:
        """Generate deletion recommendations with rationale."""
        recommendations = []
        
        for dup in duplicates:
            # Determine which file to keep
            keep_path = self._choose_canonical_path(dup.paths)
            delete_paths = [p for p in dup.paths if p != keep_path]
            
            # Generate rationale
            rationale = self._generate_rationale(keep_path, delete_paths, dup)
            
            dup.keep_path = keep_path
            dup.delete_paths = delete_paths
            dup.rationale = rationale
            
            recommendations.append({
                "keep": str(keep_path.relative_to(self.project_root)),
                "delete": [str(p.relative_to(self.project_root)) for p in delete_paths],
                "rationale": rationale,
                "size": dup.size,
                "file_type": dup.file_type,
                "hash": dup.hash[:16]
            })
        
        return recommendations
    
    def _choose_canonical_path(self, paths: List[Path]) -> Path:
        """Choose the canonical path to keep based on location priority."""
        # Prefer canonical layer locations
        for prefix in self.CANONICAL_PREFIXES:
            for path in paths:
                if prefix in str(path):
                    return path
        
        # Prefer shorter paths (less nested)
        paths_sorted = sorted(paths, key=lambda p: len(p.parts))
        return paths_sorted[0]
    
    def _generate_rationale(self, keep_path: Path, delete_paths: List[Path], dup: DuplicateFile) -> str:
        """Generate human-readable rationale for deletion."""
        keep_str = str(keep_path.relative_to(self.project_root))
        
        # Check if keep_path is in canonical location
        is_canonical = any(prefix in keep_str for prefix in self.CANONICAL_PREFIXES)
        
        if is_canonical:
            return f"Keep canonical location in {keep_str.split('/')[0]}/{keep_str.split('/')[1]}"
        else:
            return f"Keep shortest path: {len(keep_path.parts)} levels deep"
    
    def archive_duplicates(self, recommendations: List[Dict], dry_run: bool = True) -> Dict:
        """Archive duplicate files to archives/ directory (Phase 2.2).
        
        Args:
            recommendations: List of deletion recommendations from execute()
            dry_run: If True, only simulate archiving
            
        Returns:
            Dict with archiving results
        """
        import shutil
        from datetime import datetime
        
        archived = []
        errors = []
        
        # Create archive directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = self.project_root / "archives" / f"duplicates_{timestamp}"
        
        if not dry_run:
            archive_dir.mkdir(parents=True, exist_ok=True)
            Logger.info(f"Created archive directory: {archive_dir}")
        
        for rec in recommendations:
            for delete_path_str in rec["delete"]:
                full_path = self.project_root / delete_path_str
                
                try:
                    # Preserve directory structure in archive
                    relative_path = Path(delete_path_str)
                    archive_target = archive_dir / relative_path
                    
                    if dry_run:
                        Logger.info(f"[DRY RUN] Would archive: {delete_path_str} -> archives/duplicates_{timestamp}/{delete_path_str}")
                        archived.append(delete_path_str)
                    else:
                        # Create parent directories in archive
                        archive_target.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Move file to archive
                        shutil.move(str(full_path), str(archive_target))
                        Logger.info(f"[ARCHIVED] {delete_path_str} -> {archive_target.relative_to(self.project_root)}")
                        archived.append(delete_path_str)
                except Exception as e:
                    Logger.error(f"Failed to archive {delete_path_str}: {e}")
                    errors.append({"path": delete_path_str, "error": str(e)})
        
        return {
            "archived_count": len(archived),
            "archived_files": archived,
            "archive_location": str(archive_dir.relative_to(self.project_root)) if not dry_run else f"archives/duplicates_{timestamp}",
            "errors": errors,
            "dry_run": dry_run
        }
    
    def delete_duplicates(self, recommendations: List[Dict], dry_run: bool = True) -> Dict:
        """Delete duplicate files based on recommendations.
        
        Args:
            recommendations: List of deletion recommendations from execute()
            dry_run: If True, only simulate deletion
            
        Returns:
            Dict with deletion results
        """
        deleted = []
        errors = []
        
        for rec in recommendations:
            for delete_path_str in rec["delete"]:
                full_path = self.project_root / delete_path_str
                
                try:
                    if dry_run:
                        Logger.info(f"[DRY RUN] Would delete: {delete_path_str}")
                        deleted.append(delete_path_str)
                    else:
                        full_path.unlink()
                        Logger.info(f"[DELETED] {delete_path_str}")
                        deleted.append(delete_path_str)
                except Exception as e:
                    Logger.error(f"Failed to delete {delete_path_str}: {e}")
                    errors.append({"path": delete_path_str, "error": str(e)})
        
        return {
            "deleted_count": len(deleted),
            "deleted_files": deleted,
            "errors": errors,
            "dry_run": dry_run
        }
    
    def _hash_block_ast(self, code: str) -> str:
        """Generate AST fingerprint for code block."""
        try:
            if self.ts_parser:
                # Tree-sitter based fingerprint
                tree = self.ts_parser.parse(bytes(code, 'utf8'))
                norm_tree = self._normalize_ts_tree(tree.root_node)
                return hashlib.md5(str(norm_tree).encode()).hexdigest()
            else:
                # Python AST based fingerprint
                tree = ast.parse(code)
                norm_tree = self._normalize_ast_tree(tree)
                return hashlib.sha256(code.encode()).hexdigest()
        except Exception:
            # Fallback to token-based hash if AST parsing fails
            return hashlib.sha256(code.encode()).hexdigest()
    
    def _normalize_ast_tree(self, node: ast.AST) -> str:
        """Anonymize variables and constants in AST for structural comparison."""
        if isinstance(node, ast.Name):
            return 'VAR'
        elif isinstance(node, ast.Constant):
            return f'CONST_{type(node.value).__name__}'
        elif isinstance(node, (ast.Num, ast.Str)):
            return 'CONST'
        children = [self._normalize_ast_tree(child) for child in ast.iter_child_nodes(node)]
        return f'{type(node).__name__}({"|" .join(children)})' if children else type(node).__name__
    
    def _normalize_ts_tree(self, node: Any) -> str:
        """Normalize tree-sitter node for structural comparison."""
        if node.type == 'identifier':
            return 'VAR'
        elif node.type in ['string', 'integer', 'float', 'true', 'false', 'none']:
            return f'CONST_{node.type}'
        children = [self._normalize_ts_tree(child) for child in node.children]
        return f'{node.type}({"|" .join(children)})' if children else node.type

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L5 safety agent - operational only."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()
        
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
