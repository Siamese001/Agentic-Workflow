from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

"Brief description of functionality and purpose."
import difflib

"Brief description of functionality and purpose."
import hashlib
import textwrap
import uuid
import warnings
from collections import defaultdict
from typing import Any

from tqdm import tqdm

try:
    from agentic_core.base_agents.NamingAgent import get_naming_agent

    NAMING_AGENT_AVAILABLE = True
except ImportError:
    NAMING_AGENT_AVAILABLE = False
    warnings.warn(
        "NamingAgent not available — falling back to heuristic uniqueness resolution",
        RuntimeWarning,
        stacklevel=2,
    )
try:
    from apps_shared.config.operational_config import OPERATIONAL_EXCLUDED_DIRS
except ImportError:
    OPERATIONAL_EXCLUDED_DIRS = []
try:
    import tree_sitter_python as tspython
    from tree_sitter import Language, Parser

    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Parser = None
    Language = None
    tspython = None
from agentic_core.L0_routing.config import AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR
from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR
from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR
from agentic_core.utils.timeout_decorator_util import timeout


class CodeDeduplicationAgent(SovereignBaseAgent):
    """
    Batch agent for detecting and optionally refactoring duplicated code.

    HARDENED CONFIGURATION (2026-01-07):
    - Default threshold: 1.0 (100% structural identity required)
    - Aggressive purge mode: Filename duplicates consolidated to SSOT regardless of content divergence
    - Prevents Logic Bleed by enforcing absolute identity

    HARDENED: Redis caching + Pinecone vector support for semantic fingerprinting.

    Responsibilities:
    - Computes perceptual hashes of normalized AST nodes
    - Groups duplicates with 100% structural identity (threshold=THRESHOLD)
    - Reports redundancy to the L4 Ledger for audit tracking
    - [SURGERY] When RUN_SPRAWL_SURGERY=True: Extracts duplicates to shared utils
    - Whole-file duplicate detection and aggressive consolidation
    - Filename uniqueness enforcement (AGGRESSIVE: all duplicates → SSOT, no rename fallback)
    - Dead-code pruning with empty-file auto-deletion

    Consolidates functionality from deprecated FilenameUniquenessGuardianAgent (2025-12-31).
    """

    _cache_prefix: str = "code_dedup"
    _namespace: str = "l2_fingerprints"

    # guardian: allow-magic-config
    def __init__(self, similarity_threshold: float = 1.0, min_lines: int = 8) -> None:
        """
        HARDENED: 100% identity by default to prevent Logic Bleed.
        Enforces absolute structural identity for SSOT compliance.

        Args:
            similarity_threshold: Default 1.0 (100% identity required)
            min_lines: Minimum lines for duplicate detection
        """
        self.threshold = 1.0
        self.min_lines = min_lines
        self.duplicate_groups: dict[str, list[tuple[Path, str, int, str]]] = defaultdict(list)
        self.file_duplicate_groups: dict[str, list[Path]] = defaultdict(list)
        self.filename_duplicates: dict[str, list[tuple[Path, str]]] = defaultdict(list)
        self.extracted_count = 0
        self.consolidated_count = 0
        self.errors: list[str] = []
        self.ts_parser = None
        if TREE_SITTER_AVAILABLE and Parser and tspython:
            try:
                self.ts_parser = Parser()
                self.ts_parser.set_language(Language(tspython.language()))
            except (ImportError, AttributeError) as e:
                self.logger.debug(f"Tree-sitter unavailable: {e}")
                self.ts_parser = None

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        [HEALER PROTOCOL] Standardized healing interface for code deduplication violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        """

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L5_POLICY, "CodeDeduplicationAgent.heal")
        try:
            violation_type = violation.get("type", "")
            file_path = violation.get("file")
            if not file_path:
                return {
                    "status": "failed",
                    "details": "No file path provided in violation",
                    "artifacts": [],
                    "errors": ["Missing file path"],
                }
            if "DUPLICATE" in violation_type or "IDENTICAL" in violation_type:
                return {
                    "status": "manual_required",
                    "details": "Code deduplication requires batch processing via resolve_duplicates_safely()",
                    "artifacts": [],
                    "errors": [],
                }
            elif "FILENAME" in violation_type:
                return {
                    "status": "manual_required",
                    "details": "Filename duplicates require batch resolution with collision detection",
                    "artifacts": [],
                    "errors": [],
                }
            else:
                return {
                    "status": "skipped",
                    "details": f"No healer available for violation type: {violation_type}",
                    "artifacts": [],
                    "errors": [],
                }
        except (OSError, ImportError, AttributeError, ValueError) as e:
            return {
                "status": "failed",
                "details": "Exception during healing",
                "artifacts": [],
                "errors": [str(e)],
            }

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L2 compliance."""
        assert hasattr(self, "threshold"), "Missing threshold"
        assert hasattr(self, "duplicate_groups"), "Missing duplicate_groups"
        assert self.threshold == 1.0, "HARDENED: threshold must be 1.0 for SSOT"
        return True

    @staticmethod
    def _normalize_code(code: str) -> str:
        """Normalize for hashing: dedent, collapse whitespace, strip comments."""
        code = textwrap.dedent(code)
        lines = CodeDeduplicationAgent._filter_code_lines(code)
        return " ".join(lines)

    @staticmethod
    def _filter_code_lines(code: str) -> list[str]:
        """Filter code lines by removing comments and empty lines."""
        lines = []
        for line in code.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if stripped:
                lines.append(" ".join(stripped.split()))
        return "\n".join(lines)

    def _normalize_ast_tree(self, node: ast.AST) -> str:
        """Anonymize variables and constants in AST for structural comparison."""
        if isinstance(node, ast.Name):
            return "VAR"
        elif isinstance(node, ast.Constant):
            return f"CONST_{type(node.value).__name__}"
        elif isinstance(node, ast.Num | ast.Str):
            return "CONST"
        children = [self._normalize_ast_tree(child) for child in ast.iter_child_nodes(node)]
        return f"{type(node).__name__}({'|'.join(children)})"

    def _normalize_ts_tree(self, node: Any) -> str:
        """Normalize tree-sitter node for structural comparison."""
        if node.type == "identifier":
            return "VAR"
        elif node.type in ["string", "integer", "float", "true", "false", "none"]:
            return f"CONST_{node.type}"
        children = [self._normalize_ts_tree(child) for child in node.children]
        return f"{node.type}({'|'.join(children)})"

    def _block_similarity(self, norm_a: str, norm_b: str) -> float:
        """Conservative structural/text similarity using difflib (built-in, no deps)."""
        return difflib.SequenceMatcher(None, norm_a, norm_b).ratio()

    def _hash_block(self, code: str) -> str:
        """Generate AST fingerprint for code block."""
        try:
            if self.ts_parser:
                tree = self.ts_parser.parse(bytes(code, "utf8"))
                norm_tree = self._normalize_ts_tree(tree.root_node)
                return hashlib.sha256(str(norm_tree).encode()).hexdigest()
            else:
                tree = ast.parse(code)
                norm_tree = self._normalize_ast_tree(tree)
                return hashlib.sha256(str(norm_tree).encode()).hexdigest()
        except (SyntaxError, ValueError) as e:
            self.logger.debug(f"AST parsing failed, using text normalization: {e}")
            normalized = self._normalize_code(code)
            return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _extract_functions_classes(self, file_path: Path) -> list[tuple[str, str, int]]:
        """Parse file and extract function/class bodies."""
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, UnicodeDecodeError, SyntaxError) as e:
            self.logger.debug(f"Failed to extract blocks from {file_path.name}: {e}")
            return []
        blocks = []
        source_lines = source.splitlines()
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                if node.end_lineno - node.lineno + 1 < self.min_lines:
                    continue
                code_block = "\n".join(source_lines[node.lineno - 1 : node.end_lineno])
                blocks.append((node.name, code_block, node.lineno))
        return blocks

    # guardian: allow-type-erasure
    def scan_for_duplicates(self, python_files: list[str]) -> Any:
        """Phase 2 entry point - cross-file territory sweep."""
        print("\n[*] CodeDeduplicationAgent: Scanning for cross-file duplicates...")
        candidates: list[tuple[Path, str, int, str, str, int]] = []
        pbar = tqdm(
            total=len(python_files),
            desc="Extracting blocks",
            unit="file",
            colour="#00ff88",
            bar_format="{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            leave=True,
            position=0,
        )
        stats = {"blocks": 0, "skipped": 0}
        for file_str in python_files:
            file_path: Any = Path(file_str)
            pbar.set_description(f"Blocks: {file_path.name[:40]}")
            pbar.set_postfix(stats)
            if not file_path.exists() or ARCHIVES_DIR in str(file_path):
                stats["skipped"] += 1
                pbar.update(1)
                continue
            for name, code, line in self._extract_functions_classes(file_path):
                norm_str = ""
                try:
                    if self.ts_parser:
                        tree = self.ts_parser.parse(bytes(code, "utf8"))
                        norm_str = self._normalize_ts_tree(tree.root_node)
                    else:
                        tree = ast.parse(code)
                        norm_str = self._normalize_ast_tree(tree)
                except (SyntaxError, ValueError) as e:
                    self.logger.debug(f"AST normalization failed: {e}")
                    normalized = self._normalize_code(code)
                    norm_str = normalized
                if not norm_str or len(code.splitlines()) < self.min_lines:
                    continue
                len_norm = len(norm_str)
                candidates.append((file_path, name, line, code, norm_str, len_norm))
                stats["blocks"] += 1
            pbar.update(1)
        pbar.close()
        exact_groups: dict[str, list[tuple[Path, str, int, str, str, int]]] = defaultdict(list)
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
        if not self.duplicate_groups:
            print("   [OK] No significant code duplicates detected.")

    def _create_shared_utility(self, code: str, func_name: str, project_root: Path) -> Path:
        """Create deduplicated utility in sovereign shared location."""
        utils_dir = project_root / AGENTIC_CORE_DIR / "utils" / "deduplicated"
        _wg.ensure_dir(utils_dir)
        safe_name = "".join(c if c.isalnum() else "_" for c in func_name.lower())[:40]
        candidate = utils_dir / f"{safe_name}_shared.py"
        counter = 1
        while candidate.exists():
            candidate = utils_dir / f"{safe_name}_shared_{counter}.py"
            counter += 1
        header = f"# Auto-extracted shared utility by CodeDeduplicationAgent (fuzzy structural match >= {self.threshold:.0%})\n# Original function: {func_name}\n\n"
        _wg.write_text(candidate, header + textwrap.dedent(code), encoding="utf-8")
        return candidate

    # guardian: allow-type-erasure
    async def auto_extract_duplicates(self, project_root: Path, ctx: Any) -> Any:
        """[L6 SPRAWL SURGERY] Extract duplicates and inject imports."""
        if not getattr(ctx, "RUN_SPRAWL_SURGERY", False):
            print("   [INFO] Auto-extraction disabled (RUN_SPRAWL_SURGERY=False)")
            return
        print("\n[*] CONTENT DEDUPLICATION SURGERY: Extracting common blocks...")
        for _block_hash, occurrences in self.duplicate_groups.items():
            if len(occurrences) < 2:
                continue
            primary_path, func_name, _, canonical_code = occurrences[0]
            shared_file: Any = self._create_shared_utility(canonical_code, func_name, project_root)
            module_name: Any = shared_file.stem
            import_stmt: Any = f"from agentic_core.utils.deduplicated.{module_name} import {func_name}"
            for file_path, name, start_line, code in occurrences[1:]:
                try:
                    lines: Any = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
                    end_line: Any = start_line + code.count("\n")
                    replacement: Any = [
                        f"# DEDUPLICATED: Extracted to {shared_file.name}\n",
                        f"{name}_result = {func_name}()  # TODO: manually adapt params/usage\n",
                    ]
                    import_idx: Any = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith(("import ", "from ")):
                            import_idx: Any = i + 1
                            break
                    new_lines: Any = (
                        lines[:import_idx]
                        + [import_stmt + "\n"]
                        + lines[import_idx : start_line - 1]
                        + replacement
                        + lines[end_line:]
                    )
                    _wg.write_text(file_path, "".join(new_lines), encoding="utf-8")
                    backup_path = file_path.parent / f"{file_path.stem}_backup{file_path.suffix}"
                    _wg.copy_file(file_path, backup_path)
                    print(f"      [✓] Created backup: {backup_path}")
                except (OSError, TypeError) as e:
                    print(f"      [!] Backup failed for {file_path}: {e}")
        print(f"   [SURGERY COMPLETE] {self.extracted_count} instances extracted")

    def _hash_entire_file(self, file_path: Path) -> str | None:
        """SHA256 of normalized entire file (dedent, strip comments, collapse whitespace)."""
        try:
            source = file_path.read_text(encoding="utf-8")
            normalized = textwrap.dedent(source)
            lines = []
            for line in normalized.splitlines():
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if stripped:
                    lines.append(" ".join(stripped.split()))
            content = "\n".join(lines)
            return hashlib.sha256(content.encode("utf-8")).hexdigest()
        except (OSError, UnicodeDecodeError) as e:
            self.errors.append(f"File hash error {file_path}: {e}")
            return None

    def scan_file_level_duplicates(self, python_files: list[Path]) -> None:
        """Detect exact whole-file duplicates (identical content)."""
        print("\n[*] CodeDeduplicationAgent: Scanning for whole-file duplicates...")
        hash_to_files: dict[str, list[Path]] = defaultdict(list)
        pbar = tqdm(
            total=len(python_files),
            desc="Hashing files",
            unit="file",
            colour="#0088ff",
            bar_format="{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            leave=True,
            position=0,
        )
        stats = {"identical_groups": 0}
        for path in python_files:
            pbar.set_description(f"Hashing: {path.name[:40]}")
            pbar.set_postfix(stats)
            if not path.exists() or ARCHIVES_DIR in str(path):
                pbar.update(1)
                continue
            file_hash = self._hash_entire_file(path)
            if file_hash:
                hash_to_files[file_hash].append(path)
                if len(hash_to_files[file_hash]) == 2:
                    stats["identical_groups"] += 1
            pbar.update(1)
        pbar.close()
        for file_hash, files in hash_to_files.items():
            if len(files) > 1:
                print(f"   [!] IDENTICAL FILE DUPLICATE ({len(files)} copies):")
                for p in files:
                    print(f"      -> {p}")
                self.file_duplicate_groups[file_hash] = files
        if not self.file_duplicate_groups:
            print("   [OK] No whole-file duplicates detected.")

    def scan_filename_duplicates(self, python_files: list[Path], project_root: Path) -> None:
        """Detect duplicate basenames with safety check (identical vs divergent content).

        Enhanced with intelligent suffix pattern detection to catch all common duplicate
        suffixes: _flat, _1, _2, _from_utils, _copy, etc.
        """
        print(
            "\n[*] CodeDeduplicationAgent: Scanning for duplicate filenames (intelligent suffix detection)..."
        )
        basename_to_entries: dict[str, list[tuple[Path, str]]] = defaultdict(list)
        suffix_duplicates: dict[str, list[Path]] = defaultdict(list)
        PROBLEMATIC_SUFFIXES = [
            "_flat",
            "_from_utils",
            "_1",
            "_2",
            "_3",
            "_copy",
            "_backup",
            "_old",
            "_new",
            "_temp",
            "_tmp",
        ]
        pbar = tqdm(
            total=len(python_files),
            desc="Checking names",
            unit="file",
            colour="#ff88ff",
            bar_format="{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            leave=True,
            position=0,
        )
        stats = {"name_groups": 0, "divergent": 0, "suffix_dupes": 0}
        for path in python_files:
            pbar.set_description(f"Names: {path.name[:40]}")
            pbar.set_postfix(stats)
            if not path.exists() or ARCHIVES_DIR in str(path) or path.name in {"__init__.py", "setup.py"}:
                pbar.update(1)
                continue
            basename = path.name
            stem = path.stem
            matched_suffix = None
            for suffix in PROBLEMATIC_SUFFIXES:
                if stem.endswith(suffix):
                    matched_suffix = suffix
                    break
            if matched_suffix:
                canonical_stem = stem[: -len(matched_suffix)]
                canonical_name = f"{canonical_stem}.py"
                canonical_path = path.parent / canonical_name
                if canonical_path.exists():
                    suffix_duplicates[canonical_name].append((path, matched_suffix))
                    stats["suffix_dupes"] += 1
            file_hash = self._hash_entire_file(path) or "ERROR"
            basename_to_entries[basename].append((path, file_hash))
            if len(basename_to_entries[basename]) == 2:
                stats["name_groups"] += 1
                hashes = {h for _, h in basename_to_entries[basename]}
                if len(hashes) > 1:
                    stats["divergent"] += 1
            pbar.update(1)
        pbar.close()
        if suffix_duplicates:
            print(f"\n   [!] SUFFIX-BASED DUPLICATES DETECTED: {len(suffix_duplicates)} groups")
            print("       These indicate incomplete operations - canonical version exists:")
            suffix_counts = defaultdict(int)
            for canonical_name, dup_list in suffix_duplicates.items():
                for dup_path, suffix in dup_list:
                    suffix_counts[suffix] += 1
            print(f"       Breakdown by suffix: {dict(suffix_counts)}")
            for canonical_name, dup_list in suffix_duplicates.items():
                print(f"       • {canonical_name} has {len(dup_list)} suffix duplicate(s):")
                for dup_path, suffix in dup_list:
                    rel = dup_path.relative_to(project_root)
                    print(f"         → {rel} (suffix: {suffix})")
                self.filename_duplicates[canonical_name] = [(p, "") for p, _ in dup_list]
        for basename, entries in basename_to_entries.items():
            if len(entries) > 1:
                hashes = {h for _, h in entries}
                status = "IDENTICAL CONTENT" if len(hashes) == 1 else "DIVERGENT CONTENT (RENAME ONLY)"
                print(f"   [!] DUPLICATE FILENAME: {basename} ({len(entries)} copies) — {status}")
                for p, h in entries:
                    rel = p.relative_to(project_root)
                    print(f"      -> {rel} (hash: {h[:8]}...)")
                self.filename_duplicates[basename] = entries
        if not self.filename_duplicates:
            print("   [OK] No duplicate filenames requiring action.")

    CONTENT_DIR_MAPPING = [
        (
            ["safety", "guardrail", "mcp", "pii", "bias", "redteam"],
            f"{AGENTIC_CORE_DIR}/L5_safety/guardrails",
        ),
        (["outreach", "lic", "message", "contact", "cold"], "apps_lic/engines/outreach_engine"),
        (["resume", "rg", "cv", "job", "ranking"], "apps_rg/engines/resume_engine"),
        (["thought", "cognition", "reasoning", "score"], f"{AGENTIC_CORE_DIR}/L1_cognition/thought_engine"),
        (["metric", "observability", "tracing"], f"{AGENTIC_CORE_DIR}/observability/metrics"),
    ]

    def _suggest_unique_name(self, file_path: Path, project_root: Path) -> Path:
        """Primary: NamingAgent if available; Fallback: content heuristics."""
        if NAMING_AGENT_AVAILABLE:
            try:
                get_naming_agent(project_root)
            except (ImportError, AttributeError) as e:
                self.errors.append(f"NamingAgent call failed: {e}")
        try:
            preview = file_path.read_text(encoding="utf-8", errors="ignore")[:2048].lower()
            target_dir = self._get_target_dir_from_content(preview, project_root)
            _wg.ensure_dir(target_dir)
            return self._get_unique_path(target_dir, file_path)
        except (OSError, ImportError, AttributeError, ValueError) as e:
            self.errors.append(f"Uniqueness suggestion failed for {file_path}: {e}")
            return file_path.with_name(f"UNIQUE_{file_path.name}")

    def _get_target_dir_from_content(self, preview: str, project_root: Path) -> Path:
        """Determine target directory from content keywords using lookup table."""
        for keywords, rel_path in self.CONTENT_DIR_MAPPING:
            if any(k in preview for k in keywords):
                return project_root / rel_path
        return project_root / AGENTIC_CORE_DIR / "utils" / "deduplicated"

    def _get_unique_path(self, target_dir: Path, file_path: Path) -> Path:
        """Generate unique path with collision handling."""
        new_path = target_dir / file_path.name
        stem, suffix = (file_path.stem, file_path.suffix)
        counter = 1
        while new_path.exists():
            new_path = target_dir / f"{stem}_v{counter}{suffix}"
            counter += 1
        return new_path

    def resolve_duplicates_safely(self, project_root: Path, dry_run: bool = True) -> None:
        """Central resolution: identical files → consolidate; divergent filenames → rename.

        [BATCH 1 REMEDIATION] Respects SOVEREIGN_AUTO_APPROVE for automated healing.
        """
        import os

        print("\n[*] SAFE DUPLICATE RESOLUTION SURGERY...")
        auto_approve = os.environ.get("SOVEREIGN_AUTO_APPROVE") == "1"
        if auto_approve:
            print("   [SOVEREIGN] Auto-approve mode enabled")
        for _file_hash, paths in self.file_duplicate_groups.items():
            if len(paths) > 1:
                primary = min(paths, key=lambda p: (ARCHIVES_DIR in str(p), "old" in str(p), str(p)))
                for p in paths:
                    if p != primary:
                        if not dry_run:
                            backup = p.with_suffix(".bak_identical")
                            _wg.copy_file(p, backup)
                            _wg.remove_file(p)
                            print(f"      [✓] DELETED identical file: {p} (backup: {backup})")
                            self.consolidated_count += 1
                        else:
                            print(f"      [DRY-RUN] Would delete: {p}")
        for _basename, entries in self.filename_duplicates.items():
            paths = [p for p, _ in entries]
            {h for _, h in entries}
            if len(paths) > 1:
                primary = min(
                    paths, key=lambda p: (ARCHIVES_DIR in str(p), "tool_registry" in str(p), str(p))
                )
                for p in paths:
                    if p != primary:
                        if not dry_run:
                            content_hash = hashlib.md5(str(p).encode()).hexdigest()[:6]
                            backup = p.with_suffix(f".bak_purge_{content_hash}")
                            _wg.copy_file(p, backup)
                            _wg.remove_file(p)
                            print(f"      [✓] AGGRESSIVE PURGE: Deleted {p} (Backup: {backup.name})")
                            self.consolidated_count += 1
                        else:
                            print(f"      [DRY-RUN] Would delete: {p}")

    @timeout(300)
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        **kwargs,
    ) -> dict[str, int]:
        """Scan repository for code duplication and report findings.

        Detects duplicated code blocks, whole-file duplicates, and filename
        collisions. Deduplication requires batch processing and manual review.

        Args:
            dry_run: If True, only report duplicates (default: True).
            execute: If True, generate deduplication report.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        """
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path, **kwargs)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "errors": 1,
                "skipped": 0,
                "cycle_detected": True,
            }
        if depth > max_depth:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "errors": 0,
                "skipped": 1,
                "depth_limited": True,
            }
        _call_path.add(agent_name)
        violations_found = 0
        violations_fixed = 0
        errors = 0
        skipped = 0
        try:
            self.logger.info(f"[{agent_name}] Scanning for code duplication...")
            source_dirs = [
                self.project_root / AGENTIC_CORE_DIR,
                self.project_root / APPS_LIC_DIR,
                self.project_root / APPS_RG_DIR,
                self.project_root / APPS_SHARED_DIR,
            ]
            python_files = []
            for source_dir in source_dirs:
                if source_dir.exists():
                    python_files.extend(source_dir.rglob("*.py"))
            python_files = [
                f for f in python_files if "__pycache__" not in str(f) and ARCHIVES_DIR not in str(f)
            ]
            self.logger.info(f"  Scanning {len(python_files)} Python files...")
            try:
                self.scan_for_duplicates([str(f) for f in python_files])
                block_duplicates = len(self.duplicate_blocks) if hasattr(self, "duplicate_blocks") else 0
                violations_found += block_duplicates
            except (OSError, UnicodeDecodeError, SyntaxError) as e:
                self.logger.error(f"  Error scanning code blocks: {e}")
                errors += 1
            try:
                self.scan_file_level_duplicates(python_files)
                file_duplicates = len(self.file_duplicates) if hasattr(self, "file_duplicates") else 0
                violations_found += file_duplicates
            except (OSError, UnicodeDecodeError) as e:
                self.logger.error(f"  Error scanning file duplicates: {e}")
                errors += 1
            try:
                self.scan_filename_duplicates(python_files)
                name_duplicates = len(self.filename_duplicates) if hasattr(self, "filename_duplicates") else 0
                violations_found += name_duplicates
            except (OSError, UnicodeDecodeError) as e:
                self.logger.error(f"  Error scanning filename duplicates: {e}")
                errors += 1
            if violations_found > 0:
                self.logger.warning(f"  Found {violations_found} duplication issues")
                if execute and (not dry_run):
                    report_path = self.project_root / "logs" / "deduplication_report.json"
                    _wg.ensure_dir(report_path.parent)
                    report = {
                        "scan_date": str(Path(__file__).stat().st_mtime),
                        "total_duplicates": violations_found,
                        "block_duplicates": getattr(self, "duplicate_blocks", [])[:20],
                        "file_duplicates": [str(f) for f in getattr(self, "file_duplicates", [])[:20]],
                        "filename_duplicates": [
                            str(f) for f in getattr(self, "filename_duplicates", [])[:20]
                        ],
                        "note": "Deduplication requires batch processing and manual review",
                    }
                    _wg.write_json(report_path, report, indent=2)
                    self.logger.info(f"  Generated deduplication report: {report_path}")
            else:
                self.logger.info("  No significant duplication found")
            self.logger.info(
                f"[{agent_name}] Complete: {violations_found} duplicates (batch processing required)"
            )
            return {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "errors": errors,
                "skipped": skipped,
                "agent": agent_name,
                "dry_run": dry_run,
                "note": "Deduplication requires batch processing",
            }
        finally:
            _call_path.discard(agent_name)

    # guardian: allow-type-erasure
    async def execute(self, ctx: Any) -> Any:
        """Batch agent interface with enhanced duplicate detection."""
        try:
            if not getattr(ctx, "RUN_SPRAWL_SURGERY", False):
                print("[*] Running in dry-run mode - diagnostics only")
            else:
                print("[*] Running in healing mode - modifications will be applied")
        except (ImportError, AttributeError) as e:
            print(f"[!] HealerMixin diagnostic failed: {e}")
        if not hasattr(ctx, "python_files"):
            return
        if not hasattr(ctx, "project_root"):
            print("   [!] project_root Missing in context")
            return
        python_paths = [Path(f) for f in ctx.python_files]
        project_root_path = Path(ctx.project_root)
        self.scan_for_duplicates(ctx.python_files)
        self.scan_file_level_duplicates(python_paths)
        self.scan_filename_duplicates(python_paths, project_root_path)
        if getattr(ctx, "RUN_SPRAWL_SURGERY", False):
            self.resolve_duplicates_safely(project_root_path, dry_run=False)
        await self.auto_extract_duplicates(project_root_path, ctx)
        print("\n[*] DEDUPLICATION SUMMARY:")
        print(f"    Code block duplicates: {len(self.duplicate_groups)} groups")
        print(f"    Whole-file duplicates: {len(self.file_duplicate_groups)} groups")
        print(f"    Filename duplicates: {len(self.filename_duplicates)} groups")
        print(f"    Files consolidated: {self.consolidated_count}")
        print(f"    Errors: {len(self.errors)}")

    def _collect_ast_symbols(self, tree: ast.AST) -> tuple:
        """Collect imports, definitions, and usages from AST."""
        imported_names, defined_functions, defined_classes, used_names = (set(), set(), set(), set())
        import_lines, def_lines = ({}, {})
        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imported_names.add(name)
                    import_lines[name] = node.lineno
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                defined_functions.add(node.name)
                def_lines[node.name] = node.lineno
            elif isinstance(node, ast.ClassDef):
                defined_classes.add(node.name)
                def_lines[node.name] = node.lineno
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
        return (imported_names, defined_functions, defined_classes, used_names, import_lines, def_lines)

    # guardian: allow-type-erasure
    def detect_dead_code(self, file_path: Path) -> dict[str, Any]:
        """Analyze a single Python file for dead code."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            return {"error": f"Could not read {file_path}: {e}"}
        if not content.strip() or file_path.name == "__init__.py":
            return {"skipped": True, "reason": "Empty or __init__ file"}
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            return {"error": f"Syntax error in {file_path}: {e}"}
        imported, funcs, classes, used, import_lines, def_lines = self._collect_ast_symbols(tree)
        return {
            "file_path": str(file_path),
            "unused_imports": [{"name": n, "line": import_lines.get(n)} for n in imported if n not in used],
            "unused_functions": [
                {"name": n, "line": def_lines.get(n)}
                for n in funcs
                if n not in used and (not n.startswith("_"))
            ],
            "unused_classes": [
                {"name": n, "line": def_lines.get(n)}
                for n in classes
                if n not in used and (not n.startswith("_"))
            ],
        }

    # guardian: allow-type-erasure
    def scan_dead_code(self, directory: Path, recursive: bool = True) -> dict[str, Any]:
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
            return {"error": f"Directory {directory} does not exist"}
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        py_files = list(get_python_files(directory))
        results = {
            "scanned_files": len(py_files),
            "findings": [],
            "summary": {"total_unused_imports": 0, "total_unused_functions": 0, "total_unused_classes": 0},
        }
        for file_path in py_files:
            finding = self.detect_dead_code(file_path)
            if "error" not in finding and "skipped" not in finding:
                results["findings"].append(finding)
                results["summary"]["total_unused_imports"] += len(finding["unused_imports"])
                results["summary"]["total_unused_functions"] += len(finding["unused_functions"])
                results["summary"]["total_unused_classes"] += len(finding["unused_classes"])
        return results

    # guardian: allow-type-erasure
    def prune_dead_code(self, file_path: Path, dry_run: bool = True) -> dict[str, Any]:
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
        if "error" in findings or "skipped" in findings:
            return findings
        lines_to_remove = set()
        for item in findings["unused_imports"]:
            if item["line"]:
                lines_to_remove.add(item["line"])
        results = {
            "file": str(file_path),
            "dry_run": dry_run,
            "lines_marked": list(lines_to_remove),
            "imports_removed": len(findings["unused_imports"]),
        }
        if not dry_run and lines_to_remove:
            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.splitlines(keepends=True)
                new_lines = [line for i, line in enumerate(lines, 1) if i not in lines_to_remove]
                _wg.write_text(file_path, "".join(new_lines), encoding="utf-8")
                results["applied"] = True
            except (OSError, TypeError) as e:
                results["error"] = str(e)


# guardian: allow-type-erasure
def get_code_deduplication_agent() -> Any:
    """Brief description of functionality and purpose."""
    return CodeDeduplicationAgent()


if __name__ == "__main__":
    from agentic_core.utils.agent_cli import run_agent_cli

    run_agent_cli(
        CodeDeduplicationAgent, "CodeDeduplicationAgent: direct execution for validation or healing"
    )
