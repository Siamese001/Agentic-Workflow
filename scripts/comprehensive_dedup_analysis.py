#!/usr/bin/env python3
"""
Comprehensive Zero-Loss Deduplication Analysis Engine

Performs AST-level structural analysis and semantic equivalence checks
to identify and reconcile duplicate code artifacts.

Analysis Methods:
1. SHA256 content hash (exact duplicates)
2. AST structural hash (structure-only duplicates)
3. Normalized text hash (formatting-independent)
4. Semantic role hash (imports, functions, classes)
"""

import ast
import hashlib
import json
import scripts.check_canonical_structure
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional, object
from dataclasses import dataclass, field
from collections import defaultdict
import tokenize
import io

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "06_data" / "dedup_analysis"

# Folders to analyze (excluding data and tests)
SCAN_FOLDERS = [
    "agentic_core",
    "schemas",
    "runtime",
    "prompt_governance",
    "config",
    "observability",
    "scripts",
    "09_apps",
]

# Exclusion patterns
EXCLUDE_PATTERNS = [
    "06_data",
    "tests",
    "__pycache__",
    ".venv",
    ".git",
    "dedup_archive",
    "phase3_snapshots",
    "unassigned_archive",
    "review_pending",
    "stray_root_archive",
]


@dataclass
class FileFingerprint:
    """Complete fingerprint for a Python file."""
    path: Path
    content_hash: str  # SHA256 of raw content
    ast_hash: str  # Hash of AST structure
    normalized_hash: str  # Hash of normalized (no comments/whitespace) content
    semantic_hash: str  # Hash of semantic elements (imports, functions, classes)
    size: int
    line_count: int
    imports: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    is_stub: bool = False
    parse_error: Optional[str] = None


@dataclass
class DuplicateCluster:
    """A cluster of duplicate files."""
    cluster_id: str
    match_type: str  # "exact", "ast", "normalized", "semantic"
    canonical_path: Optional[Path] = None
    duplicates: List[Path] = field(default_factory=list)
    fingerprints: List[FileFingerprint] = field(default_factory=list)
    merge_plan: Dict = field(default_factory=dict)


@dataclass
class DedupReport:
    """Complete deduplication analysis report."""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_files_scanned: int = 0
    total_duplicates: int = 0
    exact_duplicates: int = 0
    ast_duplicates: int = 0
    normalized_duplicates: int = 0
    semantic_duplicates: int = 0
    clusters: List[DuplicateCluster] = field(default_factory=list)
    bytes_recoverable: int = 0


def compute_content_hash(content: str) -> str:
    """Compute SHA256 hash of content."""
    return hashlib.sha256(content.encode('utf-8', errors='replace')).hexdigest()


def compute_ast_hash(content: str) -> Tuple[str, Optional[str]]:
    """
    Compute hash of AST structure (ignoring formatting/comments).
    Returns (hash, error_message).
    """
    try:
        tree = ast.parse(content)
                for node in ast.walk(tree):
            # Clear line/column info
            for attr in ('lineno', 'col_offset', 'end_lineno', 'end_col_offset'):
                if hasattr(node, attr):
                    setattr(node, attr, 0)

        ast_dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(ast_dump.encode()).hexdigest(), None
    except SyntaxError as e:
        return "", f"SyntaxError: {e}"
    except (ValueError, TypeError, KeyError) as e:
        return "", str(e)


def normalize_content(content: str) -> str:
    """
    Normalize content by removing comments, docstrings, and normalizing whitespace.
    """
    try:
                result = []
        tokens = tokenize.generate_tokens(io.StringIO(content).readline)
        prev_toktype = tokenize.INDENT

        for toktype, tokval, _, _, _ in tokens:
            if toktype == tokenize.COMMENT:
                continue
            elif toktype == tokenize.STRING:
                if prev_toktype in (tokenize.INDENT, tokenize.NEWLINE, tokenize.NL):
                    # This is likely a docstring, skip it
                    continue
            result.append(tokval)
            prev_toktype = toktype

        normalized = ''.join(result)
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    except (ValueError, TypeError, KeyError):
        # Fallback: basic whitespace normalization
        return re.sub(r'\s+', ' ', content).strip()


def compute_normalized_hash(content: str) -> str:
    """Compute hash of normalized content."""
    normalized = normalize_content(content)
    return hashlib.sha256(normalized.encode()).hexdigest()


def extract_semantic_elements(content: str) -> Tuple[List[str], List[str], List[str]]:
    """Extract imports, function names, and class names from content."""
    imports = []
    functions = []
    classes = []

    try:
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                functions.append(f"async_{node.name}")
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
    except (ValueError, TypeError, KeyError):
        ...

    return sorted(imports), sorted(functions), sorted(classes)


def compute_semantic_hash(imports: List[str], functions: List[str], classes: List[str]) -> str:
    """Compute hash of semantic elements."""
    semantic_str = f"imports:{','.join(imports)}|functions:{','.join(functions)}|classes:{','.join(classes)}"
    return hashlib.sha256(semantic_str.encode()).hexdigest()


def is_stub_file(content: str, functions: List[str], classes: List[str]) -> bool:
    """Detect if file is a stub/placeholder."""
        stub_indicators = [
        "# AUTO-POPULATED",
        "        "# PLACEHOLDER",
        "pass  # Implementation pending
        "raise NotImplementedError",
        '"""Auto-generated',
        "LEVEL_3_placeholder",
    ]

    for indicator in stub_indicators:
        if indicator in content:
            return True

    # Check if file has no real implementation
    if not functions and not classes and len(content) < 500:
        return True

    return False


def fingerprint_file(filepath: Path) -> FileFingerprint:
    """Generate complete fingerprint for a file."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except (ValueError, TypeError, KeyError) as e:
        return FileFingerprint(
            path=filepath,
            content_hash="",
            ast_hash="",
            normalized_hash="",
            semantic_hash="",
            size=0,
            line_count=0,
            parse_error=str(e)
        )

    content_hash = compute_content_hash(content)
    ast_hash, ast_error = compute_ast_hash(content)
    normalized_hash = compute_normalized_hash(content)
    imports, functions, classes = extract_semantic_elements(content)
    semantic_hash = compute_semantic_hash(imports, functions, classes)

    return FileFingerprint(
        path=filepath,
        content_hash=content_hash,
        ast_hash=ast_hash,
        normalized_hash=normalized_hash,
        semantic_hash=semantic_hash,
        size=filepath.stat().st_size,
        line_count=content.count('\n') + 1,
        imports=imports,
        functions=functions,
        classes=classes,
        is_stub=is_stub_file(content, functions, classes),
        parse_error=ast_error
    )


def collect_fingerprints() -> List[FileFingerprint]:
    """Collect fingerprints for all Python files."""
    fingerprints = []

    for folder in SCAN_FOLDERS:
        folder_path = REPO_ROOT / folder
        if not folder_path.exists():
            continue

        for filepath in folder_path.rglob("*.py"):
            path_str = str(filepath)
            if any(excl in path_str for excl in EXCLUDE_PATTERNS):
                continue

            if filepath.is_file():
                fp = fingerprint_file(filepath)
                fingerprints.append(fp)

    return fingerprints


def find_duplicate_clusters(fingerprints: List[FileFingerprint]) -> List[DuplicateCluster]:
    """Find all duplicate clusters using multiple hash types."""
    clusters = []
    processed_paths: Set[Path] = set()

    # Group by different hash types
    by_content = defaultdict(list)
    by_ast = defaultdict(list)
    by_normalized = defaultdict(list)
    by_semantic = defaultdict(list)

    for fp in fingerprints:
        if fp.content_hash:
            by_content[fp.content_hash].append(fp)
        if fp.ast_hash:
            by_ast[fp.ast_hash].append(fp)
        if fp.normalized_hash:
            by_normalized[fp.normalized_hash].append(fp)
        if fp.semantic_hash and not fp.is_stub:  # Skip stubs for semantic matching
            by_semantic[fp.semantic_hash].append(fp)

    cluster_id = 0

    # Exact content duplicates (highest priority)
    for hash_val, fps in by_content.items():
        if len(fps) > 1:
            paths = [fp.path for fp in fps]
            if not any(p in processed_paths for p in paths):
                cluster = DuplicateCluster(
                    cluster_id=f"exact_{cluster_id}",
                    match_type="exact",
                    fingerprints=fps,
                    duplicates=[fp.path for fp in fps]
                )
                clusters.append(cluster)
                processed_paths.update(paths)
                cluster_id += 1

    # AST duplicates (same structure, different formatting)
    for hash_val, fps in by_ast.items():
        if len(fps) > 1:
            paths = [fp.path for fp in fps]
            unprocessed = [fp for fp in fps if fp.path not in processed_paths]
            if len(unprocessed) > 1:
                cluster = DuplicateCluster(
                    cluster_id=f"ast_{cluster_id}",
                    match_type="ast",
                    fingerprints=unprocessed,
                    duplicates=[fp.path for fp in unprocessed]
                )
                clusters.append(cluster)
                processed_paths.update([fp.path for fp in unprocessed])
                cluster_id += 1

    # Normalized duplicates (same content ignoring comments/whitespace)
    for hash_val, fps in by_normalized.items():
        if len(fps) > 1:
            paths = [fp.path for fp in fps]
            unprocessed = [fp for fp in fps if fp.path not in processed_paths]
            if len(unprocessed) > 1:
                cluster = DuplicateCluster(
                    cluster_id=f"normalized_{cluster_id}",
                    match_type="normalized",
                    fingerprints=unprocessed,
                    duplicates=[fp.path for fp in unprocessed]
                )
                clusters.append(cluster)
                processed_paths.update([fp.path for fp in unprocessed])
                cluster_id += 1

    # Semantic duplicates (same imports/functions/classes)
    for hash_val, fps in by_semantic.items():
        if len(fps) > 1:
            # Additional filter: must have significant content
            significant = [fp for fp in fps if fp.size > 200 and len(fp.functions) + len(fp.classes) > 0]
            unprocessed = [fp for fp in significant if fp.path not in processed_paths]
            if len(unprocessed) > 1:
                cluster = DuplicateCluster(
                    cluster_id=f"semantic_{cluster_id}",
                    match_type="semantic",
                    fingerprints=unprocessed,
                    duplicates=[fp.path for fp in unprocessed]
                )
                clusters.append(cluster)
                processed_paths.update([fp.path for fp in unprocessed])
                cluster_id += 1

    return clusters


def select_canonical_path(cluster: DuplicateCluster) -> Path:
    """Select the canonical file from a cluster based on YAML-defined priorities."""
    # Priority order for canonical selection
    folder_priority = {
        "runtime": 0,  # Runtime is canonical for shared code
        "agentic_core": 1,
        "observability": 2,
        "schemas": 3,
        "prompt_governance": 4,
        "config": 5,
        "scripts": 6,
        "09_apps": 7,
    }

    def score_path(fp: FileFingerprint) -> Tuple[int, int, int, int]:
        path_str = str(fp.path)

        # Folder priority
        folder_score = 10
        for folder, priority in folder_priority.items():
            if folder in path_str:
                folder_score = priority
                break

        # Prefer non-stubs
        stub_score = 1 if fp.is_stub else 0

        # Prefer larger files (more complete)
        size_score = -fp.size

        # Prefer shorter paths (less nested)
        path_score = len(path_str)

        return (stub_score, folder_score, size_score, path_score)

    sorted_fps = sorted(cluster.fingerprints, key=score_path)
    return sorted_fps[0].path


def generate_merge_plan(cluster: DuplicateCluster) -> Dict:
    """Generate a merge plan for a duplicate cluster."""
    canonical = select_canonical_path(cluster)
    cluster.canonical_path = canonical

    non_canonical = [fp.path for fp in cluster.fingerprints if fp.path != canonical]

    # Get canonical fingerprint
    canonical_fp = next(fp for fp in cluster.fingerprints if fp.path == canonical)

    plan = {
        "canonical_path": str(canonical.relative_to(REPO_ROOT)),
        "canonical_hash": canonical_fp.content_hash[:16],
        "canonical_size": canonical_fp.size,
        "non_canonical": [str(p.relative_to(REPO_ROOT)) for p in non_canonical],
        "match_type": cluster.match_type,
        "functions_preserved": canonical_fp.functions,
        "classes_preserved": canonical_fp.classes,
        "imports_preserved": canonical_fp.imports,
        "bytes_recoverable": sum(fp.size for fp in cluster.fingerprints if fp.path != canonical),
    }

    cluster.merge_plan = plan
    return plan


def run_analysis() -> DedupReport:
    """Run complete deduplication analysis."""
    print("=" * 70)
    print("COMPREHENSIVE ZERO-LOSS DEDUPLICATION ANALYSIS")
    print("=" * 70)

    print("\nPhase 1: Collecting file fingerprints...")
    fingerprints = collect_fingerprints()
    print(f"  Scanned {len(fingerprints)} Python files")

    # Count stubs
    stubs = [fp for fp in fingerprints if fp.is_stub]
    print(f"  Identified {len(stubs)} stub/placeholder files")

    # Count parse errors
    errors = [fp for fp in fingerprints if fp.parse_error]
    print(f"  Parse errors: {len(errors)}")

    print("\nPhase 2: Finding duplicate clusters...")
    clusters = find_duplicate_clusters(fingerprints)
    print(f"  Found {len(clusters)} duplicate clusters")

    print("\nPhase 3: Generating merge plans...")
    for cluster in clusters:
        generate_merge_plan(cluster)

    # Build report
    report = DedupReport(
        total_files_scanned=len(fingerprints),
        total_duplicates=sum(len(c.duplicates) - 1 for c in clusters),
        exact_duplicates=sum(len(c.duplicates) - 1 for c in clusters if c.match_type == "exact"),
        ast_duplicates=sum(len(c.duplicates) - 1 for c in clusters if c.match_type == "ast"),
        normalized_duplicates=sum(len(c.duplicates) - 1 for c in clusters if c.match_type == "normalized"),
        semantic_duplicates=sum(len(c.duplicates) - 1 for c in clusters if c.match_type == "semantic"),
        clusters=clusters,
        bytes_recoverable=sum(c.merge_plan.get("bytes_recoverable", 0) for c in clusters),
    )

    return report


def print_section_a(report: DedupReport):
    """Print SECTION A - Duplicate Clusters."""
    print("\n" + "=" * 70)
    print("SECTION A — Duplicate Clusters (by structural hash)")
    print("=" * 70)

    for cluster in report.clusters:
        print(f"\n[{cluster.cluster_id}] Match Type: {cluster.match_type.upper()}")
        print(f"  Files in cluster: {len(cluster.duplicates)}")
        for fp in cluster.fingerprints:
            rel_path = fp.path.relative_to(REPO_ROOT)
            stub_marker = " [STUB]" if fp.is_stub else ""
            print(f"    - {rel_path} ({fp.size} bytes, {fp.line_count} lines){stub_marker}")


def print_section_b(report: DedupReport):
    """Print SECTION B - Merge Plans."""
    print("\n" + "=" * 70)
    print("SECTION B — Merge Plans (canonical + non-canonical + diff summary)")
    print("=" * 70)

    for cluster in report.clusters:
        plan = cluster.merge_plan
        print(f"\n[{cluster.cluster_id}] {cluster.match_type.upper()} MERGE PLAN")
        print(f"  Canonical: {plan['canonical_path']}")
        print(f"  Hash: {plan['canonical_hash']}")
        print(f"  Size: {plan['canonical_size']} bytes")
        print(f"  Functions: {', '.join(plan['functions_preserved'][:5]) or 'None'}")
        print(f"  Classes: {', '.join(plan['classes_preserved'][:5]) or 'None'}")
        print(f"  Non-canonical duplicates ({len(plan['non_canonical'])}):")
        for nc in plan['non_canonical']:
            print(f"    - {nc}")
        print(f"  Bytes recoverable: {plan['bytes_recoverable']:,}")


def print_section_e(report: DedupReport):
    """Print SECTION E - Final Summary."""
    print("\n" + "=" * 70)
    print("SECTION E — Final Repository Dedup Summary")
    print("=" * 70)

    print(f"\nTimestamp: {report.timestamp}")
    print(f"\nFiles Analyzed: {report.total_files_scanned}")
    print(f"\nDuplicate Statistics:")
    print(f"  Total duplicate files: {report.total_duplicates}")
    print(f"  - Exact content duplicates: {report.exact_duplicates}")
    print(f"  - AST structure duplicates: {report.ast_duplicates}")
    print(f"  - Normalized content duplicates: {report.normalized_duplicates}")
    print(f"  - Semantic role duplicates: {report.semantic_duplicates}")
    print(f"\nDuplicate Clusters: {len(report.clusters)}")
    print(f"Bytes Recoverable: {report.bytes_recoverable:,} ({report.bytes_recoverable / 1024 / 1024:.2f} MB)")

    # Group by folder
    by_folder = defaultdict(int)
    for cluster in report.clusters:
        for fp in cluster.fingerprints:
            folder = str(fp.path.relative_to(REPO_ROOT)).split('/')[0].split('\\')[0]
            by_folder[folder] += 1

    print(f"\nDuplicates by Folder:")
    for folder, count in sorted(by_folder.items(), key=lambda x: -x[1]):
        print(f"  {folder}: {count}")


def save_report(report: DedupReport):
    """Save report to JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report_data = {
        "timestamp": report.timestamp,
        "total_files_scanned": report.total_files_scanned,
        "total_duplicates": report.total_duplicates,
        "exact_duplicates": report.exact_duplicates,
        "ast_duplicates": report.ast_duplicates,
        "normalized_duplicates": report.normalized_duplicates,
        "semantic_duplicates": report.semantic_duplicates,
        "bytes_recoverable": report.bytes_recoverable,
        "clusters": [
            {
                "cluster_id": c.cluster_id,
                "match_type": c.match_type,
                "canonical_path": str(c.canonical_path.relative_to(REPO_ROOT)) if c.canonical_path else None,
                "duplicates": [str(p.relative_to(REPO_ROOT)) for p in c.duplicates],
                "merge_plan": c.merge_plan,
            }
            for c in report.clusters
        ]
    }

    output_path = OUTPUT_DIR / f"dedup_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"\nReport saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    report = run_analysis()

    print_section_a(report)
    print_section_b(report)
    print_section_e(report)

    save_report(report)
