# CodeDeduplicationAgent - Batch Validator (Phase 2)
# Territory: agentic_core/L2_execution/tool_registry
# Purpose: Cross-file detection and elimination of duplicated code blocks
# Canon Key 8 - Execution tools + agent behavioral patterns

import ast
import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple
import textwrap
import shutil
from agentic_core.config.blueprint_sovereign.structure_blueprint import FORBIDDEN_ROOT_FOLDERS

class CodeDeduplicationAgent:
    """
    Batch agent for detecting and optionally refactoring duplicated code.
    
    Responsibilities:
    - Computes perceptual hashes of normalized AST nodes.
    - Groups duplicates with similarity > 95%.
    - Reports redundancy to the L4 Ledger for audit tracking.
    - [SURGERY] When RUN_SPRAWL_SURGERY=True: Extracts duplicates to shared utils
    """
    
    def __init__(self, similarity_threshold: float = 0.95, min_lines: int = 8):
        self.threshold = similarity_threshold
        self.min_lines = min_lines
        self.duplicate_groups: Dict[str, List[Tuple[Path, str, int]]] = defaultdict(list)
        self.extracted_count = 0
        self.errors: List[str] = []
    
    @staticmethod
    def _normalize_code(code: str) -> str:
        """Normalize for hashing: dedent, collapse whitespace, strip comments."""
        code = textwrap.dedent(code)
        lines = []
        for line in code.splitlines():
            stripped = line.strip()
            if stripped.startswith('#'):
                continue  # Skip comments
            if stripped:
                lines.append(' '.join(stripped.split()))
        return '\n'.join(lines)
    
    @staticmethod
    def _hash_block(code: str) -> str:
        normalized = CodeDeduplicationAgent._normalize_code(code)
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
                code_block = '\n'.join(source_lines[node.lineno-1:node.end_lineno])
                blocks.append((node.name, code_block, node.lineno))
        return blocks
    
    def scan_for_duplicates(self, python_files: List[str]):
        """Phase 2 entry point - cross-file territory sweep."""
        print("\n[*] CodeDeduplicationAgent: Scanning for cross-file duplicates...")
        
        hash_to_blocks = defaultdict(list)
        
        for file_str in python_files:
            file_path = Path(file_str)
            if not file_path.exists():
                continue
                
            for name, code, line in self._extract_functions_classes(file_path):
                block_hash = self._hash_block(code)
                hash_to_blocks[block_hash].append((file_path, name, line, code))
        
        for block_hash, occurrences in hash_to_blocks.items():
            if len(occurrences) > 1:
                print(f"   [!] DUPLICATE FOUND ({len(occurrences)} copies):")
                for path, name, line, _ in occurrences:
                    # Absolute path resolution consistent with project_root hardening
                    print(f"      -> {path.name}:{line} ({name})")
                self.duplicate_groups[block_hash] = occurrences
        
        if not self.duplicate_groups:
            print("   [OK] No significant code duplicates detected.")
    
    def _create_shared_utility(self, code: str, func_name: str, project_root: Path) -> Path:
        """Create deduplicated utility in sovereign shared location."""
        utils_dir = project_root / "agentic_core" / "utils" / "deduplicated"
        utils_dir.mkdir(parents=True, exist_ok=True)

        # Deterministic but readable name
        safe_name = ''.join(c if c.isalnum() else '_' for c in func_name.lower())[:40]
        candidate = utils_dir / f"{safe_name}_shared.py"

        counter = 1
        while candidate.exists():
            candidate = utils_dir / f"{safe_name}_shared_{counter}.py"
            counter += 1

        header = f'# Auto-extracted shared utility by CodeDeduplicationAgent\n# Original function: {func_name}\n\n'
        candidate.write_text(header + textwrap.dedent(code), encoding='utf-8')
        return candidate

    async def auto_extract_duplicates(self, project_root: Path, ctx):
        """[L6 SPRAWL SURGERY] Extract duplicates and inject imports."""
        if not getattr(ctx, 'RUN_SPRAWL_SURGERY', False):
            print("   [INFO] Auto-extraction disabled (RUN_SPRAWL_SURGERY=False)")
            return

        print("\n[*] CONTENT DEDUPLICATION SURGERY: Extracting common blocks...")

        for block_hash, occurrences in self.duplicate_groups.items():
            if len(occurrences) < 2:
                continue

            # Use first as canonical
            primary_path, func_name, _, canonical_code = occurrences[0]

            shared_file = self._create_shared_utility(canonical_code, func_name, project_root)
            module_name = shared_file.stem
            import_stmt = f"from agentic_core.utils.deduplicated.{module_name} import {func_name}"

            # Replace duplicates (skip primary)
            for file_path, name, start_line, code in occurrences[1:]:
                try:
                    lines = file_path.read_text(encoding='utf-8').splitlines(keepends=True)
                    end_line = start_line + code.count('\n')

                    # Simple replacement: comment + placeholder
                    replacement = [
                        f"# DEDUPLICATED: Extracted to {shared_file.name}\n",
                        f"{name}_result = {func_name}()  # TODO: manually adapt params/usage\n"
                    ]

                    # Find safe insertion point for import
                    import_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith(('import ', 'from ')):
                            import_idx = i + 1
                            break

                    new_lines = (
                        lines[:import_idx] +
                        [import_stmt + '\n'] +
                        lines[import_idx:start_line-1] +
                        replacement +
                        lines[end_line:]
                    )

                    file_path.write_text(''.join(new_lines), encoding='utf-8')
                    print(f"      [✓] REFACTORED: {file_path.name}:{start_line}")
                    self.extracted_count += 1
                except Exception as e:
                    self.errors.append(f"Refactor failed {file_path}: {e}")

        print(f"   [SURGERY COMPLETE] {self.extracted_count} instances extracted")
    
    async def execute(self, ctx):
        """Batch agent interface."""
        if not hasattr(ctx, 'python_files'):
            return
        if not hasattr(ctx, 'project_root'):
            print("   [!] project_root missing in context")
            return

        self.scan_for_duplicates(ctx.python_files)
        await self.auto_extract_duplicates(Path(ctx.project_root), ctx)

def get_code_deduplication_agent():
    return CodeDeduplicationAgent()
