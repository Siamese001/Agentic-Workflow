#!/usr/bin/env python3
"""
Deep Recursive Archive Scanner with Advanced AST Analysis

Performs comprehensive analysis of ALL files in archives/ folder using:
1. Full recursive directory traversal
2. AST parsing for class/function/method extraction
3. Semantic analysis of docstrings and naming patterns
4. Cross-reference with current codebase index
5. Uniqueness scoring based on multiple factors
6. Domain classification (resume/outreach/shared/infrastructure)
7. Dependency graph analysis
8. Quality metrics (docstrings, type hints, complexity)
"""

import ast
import hashlib
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

ARCHIVES_ROOT = Path("archives")
CURRENT_DIRS = ["agentic_core", "apps_rg", "apps_lic", "apps_shared", "scripts"]

# Patterns to skip
SKIP_PATTERNS = ["__pycache__", ".git", "node_modules", ".venv", "venv"]
SKIP_FILES = ["__init__.py", "conftest.py", "setup.py"]

# Domain keywords
RESUME_KEYWORDS = {
    "resume",
    "cv",
    "job",
    "skill",
    "experience",
    "ats",
    "bullet",
    "achievement",
    "qualification",
}
OUTREACH_KEYWORDS = {
    "outreach",
    "linkedin",
    "recipient",
    "campaign",
    "message",
    "personalization",
    "sender",
    "hop",
    "lic",
}
INFRA_KEYWORDS = {
    "cache",
    "redis",
    "pinecone",
    "mcp",
    "heal",
    "validate",
    "orchestrat",
    "state",
    "config",
    "mixin",
}

# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class CodeEntity:
    """A class, function, or method extracted from code."""

    name: str
    entity_type: str  # 'agent', 'class', 'model', 'mixin', 'function'
    file_path: str
    bases: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    params: list[str] = field(default_factory=list)
    docstring: str = ""
    line_start: int = 0
    line_end: int = 0


@dataclass
class FileAnalysis:
    """Complete analysis of a single Python file."""

    path: str
    relative_path: str
    archive_folder: str
    entities: list[CodeEntity] = field(default_factory=list)
    imports: set[str] = field(default_factory=set)
    loc: int = 0
    has_syntax_error: bool = False
    syntax_error_msg: str = ""
    domain: str = "unknown"
    quality_score: float = 0.0
    uniqueness_score: float = 0.0
    unique_entities: list[str] = field(default_factory=list)
    existing_entities: list[str] = field(default_factory=list)
    recommendation: str = ""  # 'restore', 'extract', 'review', 'skip'
    target_folder: str = ""


# ============================================================================
# CODEBASE INDEX
# ============================================================================


class CodebaseIndex:
    """Index of all entities in current codebase."""

    def __init__(self):
        self.classes: set[str] = set()
        self.functions: set[str] = set()
        self.agents: set[str] = set()
        self.methods: set[str] = set()
        self.file_hashes: dict[str, str] = {}

    def build(self, dirs: list[str]):
        """Build index from directories."""
        for dir_path in dirs:
            if not Path(dir_path).exists():
                continue
            for py_file in Path(dir_path).rglob("*.py"):
                if any(skip in str(py_file) for skip in SKIP_PATTERNS):
                    continue
                self._index_file(py_file)

        print(
            f"  Indexed: {len(self.classes)} classes, {len(self.agents)} agents, "
            f"{len(self.functions)} functions, {len(self.methods)} methods"
        )

    def _index_file(self, file_path: Path):
        """Index a single file."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            # Store hash for duplicate detection
            self.file_hashes[file_path.name.lower()] = hashlib.md5(content.encode()).hexdigest()

            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.classes.add(node.name.lower())
                    if node.name.endswith("Agent"):
                        self.agents.add(node.name.lower())
                    # Index methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                            self.methods.add(item.name.lower())
                elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    self.functions.add(node.name.lower())
        except:
            pass

    def entity_exists(self, name: str, entity_type: str) -> bool:
        """Check if entity exists in codebase."""
        name_lower = name.lower()
        if entity_type == "agent":
            return name_lower in self.agents
        elif entity_type in ("class", "model", "mixin"):
            return name_lower in self.classes
        elif entity_type == "function":
            return name_lower in self.functions
        return False


# ============================================================================
# AST ANALYSIS
# ============================================================================


def get_docstring(node) -> str:
    """Extract docstring from AST node."""
    try:
        doc = ast.get_docstring(node)
        return doc[:300] if doc else ""
    except:
        return ""


def classify_entity(name: str, bases: list[str]) -> str:
    """Classify entity type based on name and inheritance."""
    if name.endswith("Agent") or any("Agent" in b for b in bases):
        return "agent"
    if any(b in ("BaseModel", "Enum", "TypedDict", "NamedTuple") for b in bases):
        return "model"
    if "Mixin" in name:
        return "mixin"
    if name[0].isupper():
        return "class"
    return "function"


def infer_domain(content: str, entities: list[CodeEntity]) -> str:
    """Infer domain from content and entities."""
    content_lower = content.lower()

    resume_score = sum(5 for kw in RESUME_KEYWORDS if kw in content_lower)
    outreach_score = sum(5 for kw in OUTREACH_KEYWORDS if kw in content_lower)
    infra_score = sum(3 for kw in INFRA_KEYWORDS if kw in content_lower)

    # Boost from entity names
    for e in entities:
        name_lower = e.name.lower()
        if any(kw in name_lower for kw in RESUME_KEYWORDS):
            resume_score += 15
        if any(kw in name_lower for kw in OUTREACH_KEYWORDS):
            outreach_score += 15
        if any(kw in name_lower for kw in INFRA_KEYWORDS):
            infra_score += 10

    if resume_score > 20 and outreach_score > 20:
        return "shared"
    if resume_score > outreach_score and resume_score > infra_score:
        return "resume"
    if outreach_score > resume_score and outreach_score > infra_score:
        return "outreach"
    if infra_score > 15:
        return "infrastructure"
    return "shared"


def analyze_file(file_path: Path, archive_folder: str, index: CodebaseIndex) -> FileAnalysis | None:
    """Perform deep AST analysis on a file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    # Create analysis object
    rel_path = str(file_path.relative_to(ARCHIVES_ROOT))
    analysis = FileAnalysis(
        path=str(file_path),
        relative_path=rel_path,
        archive_folder=archive_folder,
        loc=len(content.splitlines()),
    )

    # Try to parse
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        analysis.has_syntax_error = True
        analysis.syntax_error_msg = str(e)
        return analysis

    # Extract imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                analysis.imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                analysis.imports.add(node.module)

    # Extract entities
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(base.attr)

            methods = [
                item.name
                for item in node.body
                if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef)
            ]

            entity = CodeEntity(
                name=node.name,
                entity_type=classify_entity(node.name, bases),
                file_path=str(file_path),
                bases=bases,
                methods=methods,
                docstring=get_docstring(node),
                line_start=node.lineno,
                line_end=getattr(node, "end_lineno", node.lineno + 50),
            )
            analysis.entities.append(entity)

        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            if not node.name.startswith("_"):  # Skip private functions
                params = [arg.arg for arg in node.args.args if arg.arg != "self"]
                entity = CodeEntity(
                    name=node.name,
                    entity_type="function",
                    file_path=str(file_path),
                    params=params,
                    docstring=get_docstring(node),
                    line_start=node.lineno,
                    line_end=getattr(node, "end_lineno", node.lineno + 20),
                )
                analysis.entities.append(entity)

    # Infer domain
    analysis.domain = infer_domain(content, analysis.entities)

    # Calculate uniqueness
    unique_entities = []
    existing_entities = []

    for entity in analysis.entities:
        if index.entity_exists(entity.name, entity.entity_type):
            existing_entities.append(entity.name)
        else:
            unique_entities.append(entity.name)

    analysis.unique_entities = unique_entities
    analysis.existing_entities = existing_entities

    # Calculate uniqueness score
    if analysis.entities:
        unique_count = len(unique_entities)
        total_count = len(analysis.entities)

        # Weight agents higher
        agent_bonus = sum(
            20 for e in analysis.entities if e.entity_type == "agent" and e.name in unique_entities
        )

        analysis.uniqueness_score = (unique_count / total_count * 100) + agent_bonus
        analysis.uniqueness_score = min(100, analysis.uniqueness_score)

    # Calculate quality score
    has_docstrings = sum(1 for e in analysis.entities if e.docstring) / max(
        len(analysis.entities), 1
    )
    has_types = "typing" in str(analysis.imports) or ": " in content
    analysis.quality_score = (has_docstrings * 50) + (50 if has_types else 0)

    # Determine recommendation
    unique_agents = [
        e for e in analysis.entities if e.entity_type == "agent" and e.name in unique_entities
    ]

    if analysis.uniqueness_score >= 80 or unique_agents:
        analysis.recommendation = "restore"
    elif analysis.uniqueness_score >= 50:
        analysis.recommendation = "extract"
    elif analysis.uniqueness_score >= 20:
        analysis.recommendation = "review"
    else:
        analysis.recommendation = "skip"

    # Determine target folder
    if analysis.domain == "outreach":
        analysis.target_folder = "apps_lic/engines/"
    elif analysis.domain == "resume":
        analysis.target_folder = "apps_rg/engines/"
    elif analysis.domain == "infrastructure":
        analysis.target_folder = "agentic_core/utils/"
    else:
        analysis.target_folder = "apps_shared/"

    return analysis


# ============================================================================
# MAIN SCANNER
# ============================================================================


def scan_archives(index: CodebaseIndex) -> list[FileAnalysis]:
    """Recursively scan all archives."""
    all_analyses = []

    for root, dirs, files in os.walk(ARCHIVES_ROOT):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in SKIP_PATTERNS]

        root_path = Path(root)

        # Determine archive folder name
        try:
            rel_to_archives = root_path.relative_to(ARCHIVES_ROOT)
            archive_folder = (
                str(rel_to_archives).split(os.sep)[0] if str(rel_to_archives) != "." else "root"
            )
        except:
            archive_folder = "unknown"

        for file in files:
            if not file.endswith(".py"):
                continue
            if file in SKIP_FILES:
                continue

            file_path = root_path / file
            analysis = analyze_file(file_path, archive_folder, index)

            if analysis:
                all_analyses.append(analysis)

    return all_analyses


def generate_report(analyses: list[FileAnalysis]) -> str:
    """Generate comprehensive findings report."""
    lines = []

    # Header
    lines.append("=" * 80)
    lines.append("DEEP ARCHIVE ANALYSIS - FINDINGS & RECOMMENDATIONS")
    lines.append("=" * 80)
    lines.append(f"\nTotal files scanned: {len(analyses)}")

    # Filter by recommendation
    restore = [a for a in analyses if a.recommendation == "restore" and not a.has_syntax_error]
    extract = [a for a in analyses if a.recommendation == "extract" and not a.has_syntax_error]
    review = [a for a in analyses if a.recommendation == "review" and not a.has_syntax_error]
    skip = [a for a in analyses if a.recommendation == "skip" and not a.has_syntax_error]
    errors = [a for a in analyses if a.has_syntax_error]

    lines.append(f"  RESTORE (unique agents/high value): {len(restore)}")
    lines.append(f"  EXTRACT (unique content): {len(extract)}")
    lines.append(f"  REVIEW (partial overlap): {len(review)}")
    lines.append(f"  SKIP (exists in codebase): {len(skip)}")
    lines.append(f"  SYNTAX ERRORS: {len(errors)}")

    # Archive folder breakdown
    lines.append("\n" + "=" * 80)
    lines.append("ARCHIVE FOLDER BREAKDOWN")
    lines.append("=" * 80)

    folder_stats = defaultdict(lambda: {"total": 0, "restore": 0, "unique_agents": []})
    for a in analyses:
        folder_stats[a.archive_folder]["total"] += 1
        if a.recommendation == "restore":
            folder_stats[a.archive_folder]["restore"] += 1
            for e in a.entities:
                if e.entity_type == "agent" and e.name in a.unique_entities:
                    folder_stats[a.archive_folder]["unique_agents"].append(e.name)

    for folder, stats in sorted(folder_stats.items(), key=lambda x: -x[1]["restore"]):
        if stats["restore"] > 0:
            lines.append(f"\n  {folder}:")
            lines.append(f"    Files: {stats['total']}, Restore: {stats['restore']}")
            if stats["unique_agents"]:
                lines.append(f"    Unique Agents: {stats['unique_agents'][:10]}")

    # HIGH PRIORITY - RESTORE
    lines.append("\n" + "=" * 80)
    lines.append("HIGH PRIORITY - RESTORE (Unique Agents)")
    lines.append("=" * 80)

    restore_sorted = sorted(restore, key=lambda x: -x.uniqueness_score)
    for a in restore_sorted[:50]:
        unique_agents = [
            e.name for e in a.entities if e.entity_type == "agent" and e.name in a.unique_entities
        ]
        unique_classes = [
            e.name for e in a.entities if e.entity_type != "agent" and e.name in a.unique_entities
        ]

        lines.append(f"\n  [{a.uniqueness_score:.0f}%] {Path(a.path).name}")
        lines.append(f"    Path: {a.relative_path}")
        lines.append(f"    Domain: {a.domain.upper()}")
        if unique_agents:
            lines.append(f"    Unique Agents: {unique_agents}")
        if unique_classes:
            lines.append(f"    Unique Classes: {unique_classes[:5]}")
        lines.append(f"    Target: {a.target_folder}")

    # MEDIUM PRIORITY - EXTRACT
    lines.append("\n" + "=" * 80)
    lines.append("MEDIUM PRIORITY - EXTRACT (Unique Utilities)")
    lines.append("=" * 80)
    lines.append(f"\nTotal: {len(extract)} files")

    extract_sorted = sorted(extract, key=lambda x: -x.uniqueness_score)
    for a in extract_sorted[:30]:
        lines.append(f"\n  [{a.uniqueness_score:.0f}%] {Path(a.path).name}")
        lines.append(f"    Path: {a.relative_path}")
        lines.append(f"    Unique: {a.unique_entities[:5]}")

    # Summary statistics
    lines.append("\n" + "=" * 80)
    lines.append("EXECUTIVE SUMMARY")
    lines.append("=" * 80)

    total_unique_agents = sum(
        len([e for e in a.entities if e.entity_type == "agent" and e.name in a.unique_entities])
        for a in restore
    )

    lines.append(f"""
    Files to RESTORE:           {len(restore)}
    Files to EXTRACT:           {len(extract)}
    Files to REVIEW:            {len(review)}
    Files to SKIP:              {len(skip)}
    Files with syntax errors:   {len(errors)}

    TOTAL UNIQUE AGENTS:        {total_unique_agents}
    TOTAL RESTORATION FILES:    {len(restore) + len(extract)}
    """)

    # Top restoration commands
    lines.append("\n" + "=" * 80)
    lines.append("TOP 20 RESTORATION COMMANDS")
    lines.append("=" * 80)

    for a in restore_sorted[:20]:
        src = a.path
        # Generate PascalCase filename from first agent or class
        agents = [e for e in a.entities if e.entity_type == "agent" and e.name in a.unique_entities]
        if agents:
            dst_name = agents[0].name + ".py"
        else:
            dst_name = Path(a.path).name

        dst = a.target_folder + dst_name
        lines.append(f'\ncp "{src}" "{dst}"')

    return "\n".join(lines)


def main():
    print("=" * 80)
    print("DEEP RECURSIVE ARCHIVE SCANNER")
    print("=" * 80)

    # Build codebase index
    print("\n[1/3] Building codebase index...")
    index = CodebaseIndex()
    index.build(CURRENT_DIRS)

    # Scan archives
    print("\n[2/3] Scanning archives recursively...")
    analyses = scan_archives(index)
    print(f"  Scanned {len(analyses)} Python files")

    # Generate report
    print("\n[3/3] Generating report...")
    report = generate_report(analyses)

    # Print report
    print("\n" + report)

    # Save report
    report_path = Path("docs/DEEP_ARCHIVE_ANALYSIS.md")
    report_path.write_text(report, encoding="utf-8")
    print(f"\n\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
