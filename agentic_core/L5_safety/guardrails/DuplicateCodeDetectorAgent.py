from __future__ import annotations
#!/usr/bin/env python3
"""
Duplicate Code Detector Agent
Batch agent: Detects exact duplicate code blocks across the entire territory.
Uses AST fingerprinting for structural comparison (Type-2/3 clone detection).
"""
import hashlib
import tokenize
import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Any
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

# Tree-sitter for AST fingerprinting
try:
    from tree_sitter import Language, Parser
    from tree_sitter_python import language
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Parser = None
    Language = None

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

class DuplicateCodeDetectorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Batch agent: Detects exact duplicate code blocks across the entire territory.
    Uses token-based hashing for speed and accuracy (ignores whitespace/comments).
    """

    def __init__(self, project_root: Path, ctx) -> None:
        self.project_root = Path(project_root)
        self.ctx = ctx
        self.min_lines = 10  # Minimum block size to flag
        self.max_report = 20  # Limit detailed reporting
        self.auto_deduplicate = False
        
        # Initialize tree-sitter parser if available
        self.ts_parser: Optional[Parser] = None
        if TREE_SITTER_AVAILABLE:
            try:
                self.ts_parser = Parser()
                self.ts_parser.language = language()
            except Exception:
                self.ts_parser = None

    async def execute(self) -> Dict:
        """Scan all Python files for duplicate code blocks."""
        if not hasattr(self.ctx, "python_files") or not self.ctx.python_files:
            return {}

        print(
            f"   [DUPE SCAN] Analyzing {len(self.ctx.python_files)} files for duplicates >={self.min_lines} lines..."
        )
        code_blocks = defaultdict(list)  # hash -> [(path, start_line)]

        for file_path_str in self.ctx.python_files:
            file_path = Path(file_path_str)
            # EXCLUDE archives/ directory
            if not file_path.exists() or 'archives' in str(file_path):
                continue

            try:
                # Read file content
                lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()

                # Sliding window hash
                for i in range(len(lines) - self.min_lines + 1):
                    # Extract block
                    block_content = "\nfrom agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n".join(lines[i : i + self.min_lines])
                    if not block_content.strip():
                        continue

                    # AST fingerprint for structural comparison
                    block_hash = self._hash_block_ast(block_content)
                    try:
                        rel_path = file_path.relative_to(self.project_root)
                    except ValueError:
                        rel_path = file_path
                    code_blocks[block_hash].append((str(rel_path), i + 1))

            except Exception as e:
                # Skip unreadable files
                continue

        # Find duplicates (blocks that appear in multiple locations)
        duplicates = [locations for locations in code_blocks.values() if len(locations) > 1]
        total_dupes = sum(len(locs) - 1 for locs in duplicates)

        return {
            "duplicates_found": len(duplicates),
            "instances_eliminated_potential": total_dupes,
            "details": duplicates[: self.max_report],
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
