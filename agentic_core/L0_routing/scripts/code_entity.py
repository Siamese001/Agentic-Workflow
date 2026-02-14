#!/usr/bin/env python3
"""
Comprehensive AST-based Archive Analyzer

Advanced analysis of all archived files to identify:
1. Unique agents not in current codebase
2. Unique utility functions/classes
3. Unique models/schemas
4. Code that fills gaps in current functionality
5. Dead code that should remain archived

Methods used:
- AST parsing for class/function extraction
- Semantic similarity based on naming patterns
- Dependency graph analysis
- Domain classification (resume/outreach/shared/infra)
- Complexity and quality metrics
"""

import ast
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.L5_safety.enforcement.mutation_prohibition import assert_no_persistent_write

# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class CodeEntity:
    """Represents a class or function extracted from code."""

    name: str
    entity_type: str  # 'class', 'function', 'agent', 'model', 'mixin'
    file_path: str
    bases: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    params: list[str] = field(default_factory=list)
    docstring: str = ""
    loc: int = 0
    domain: str = ""  # resume, outreach, shared, infrastructure


@dataclass
class FileAnalysis:
    """Complete analysis of a single file."""

    path: str
    archive_folder: str
    entities: list[CodeEntity] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    external_deps: list[str] = field(default_factory=list)
    internal_deps: list[str] = field(default_factory=list)
    loc: int = 0
    has_syntax_error: bool = False
    domain: str = ""
    quality_score: float = 0.0
    unique_score: float = 0.0  # How unique compared to current codebase


# ============================================================================
# AST ANALYSIS FUNCTIONS
# ============================================================================


def extract_docstring(node) -> str:
    """Extract docstring from AST node."""
    try:
        doc = ast.get_docstring(node)
        return doc[:200] if doc else ""
    # guardian: allow-silent-swallow
    except:
        return ""


def classify_entity_type(name: str, bases: list[str]) -> str:
    """Classify entity type based on name and inheritance."""
    name.lower()

    if name.endswith("Agent") or any("Agent" in b for b in bases):
        return "agent"
    if any(b in ("BaseModel", "Enum", "TypedDict") for b in bases):
        return "model"
    if "Mixin" in name:
        return "mixin"
    if name[0].isupper() and not name.isupper():
        return "class"
    return "function"


def infer_domain(content: str, entities: list[CodeEntity]) -> str:
    """Infer domain from content and entity names."""
    content_lower = content.lower()

    resume_signals = [
        "resume",
        "cv",
        "job description",
        "skill",
        "experience",
        "ats",
        "bullet",
        "achievement",
    ]
    outreach_signals = [
        "outreach",
        "linkedin",
        "recipient",
        "campaign",
        "message",
        "personalization",
        "sender",
        "hop",
    ]
    infra_signals = [
        "cache",
        "redis",
        "pinecone",
        "mcp",
        "heal",
        "validate",
        "orchestrat",
        "state",
        "config",
    ]

    resume_score = sum(3 if s in content_lower else 0 for s in resume_signals)
    outreach_score = sum(3 if s in content_lower else 0 for s in outreach_signals)
    infra_score = sum(2 if s in content_lower else 0 for s in infra_signals)

    # Boost from entity names
    for e in entities:
        name_lower = e.name.lower()
        if any(s in name_lower for s in ["resume", "skill", "job", "cv", "ats"]):
            resume_score += 10
        if any(s in name_lower for s in ["outreach", "message", "recipient", "campaign", "hop"]):
            outreach_score += 10
        if any(s in name_lower for s in ["state", "cache", "config", "validator"]):
            infra_score += 5

    if resume_score > 15 and outreach_score > 15:
        return "shared"
    if resume_score > outreach_score and resume_score > infra_score:
        return "resume"
    if outreach_score > resume_score and outreach_score > infra_score:
        return "outreach"
    if infra_score > 10:
        return "infrastructure"
    return "shared"


def analyze_file(file_path: Path, archive_folder: str) -> FileAnalysis | None:
    """Perform deep AST analysis on a file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content)
    except SyntaxError:
        return FileAnalysis(path=str(file_path), archive_folder=archive_folder, has_syntax_error=True, loc=0)
    except Exception:
        return None

    analysis = FileAnalysis(path=str(file_path), archive_folder=archive_folder, loc=len(content.splitlines()))

    # Extract imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                analysis.imports.append(alias.name)
                if alias.name.startswith(("agentic_core", "apps_")):
                    analysis.internal_deps.append(alias.name)
                elif not alias.name.startswith(
                    ("typing", "pathlib", "os", "sys", "re", "json", "dataclasses"),
                ):
                    analysis.external_deps.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            analysis.imports.append(module)
            if module.startswith(("agentic_core", "apps_")):
                analysis.internal_deps.append(module)
            elif not module.startswith(
                ("typing", "pathlib", "os", "sys", "re", "json", "dataclasses", "enum"),
            ):
                analysis.external_deps.append(module)

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
                item.name for item in node.body if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef)
            ]

            entity = CodeEntity(
                name=node.name,
                entity_type=classify_entity_type(node.name, bases),
                file_path=str(file_path),
                bases=bases,
                methods=methods,
                docstring=extract_docstring(node),
                loc=node.end_lineno - node.lineno if hasattr(node, "end_lineno") else 0,
            )
            analysis.entities.append(entity)

        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            params = [arg.arg for arg in node.args.args if arg.arg != "self"]
            entity = CodeEntity(
                name=node.name,
                entity_type="function",
                file_path=str(file_path),
                params=params,
                docstring=extract_docstring(node),
                loc=node.end_lineno - node.lineno if hasattr(node, "end_lineno") else 0,
            )
            analysis.entities.append(entity)

    # Infer domain
    analysis.domain = infer_domain(content, analysis.entities)

    # Calculate quality score
    has_docstrings = sum(1 for e in analysis.entities if e.docstring) / max(len(analysis.entities), 1)
    has_type_hints = "typing" in str(analysis.imports) or ": " in content
    analysis.quality_score = (has_docstrings * 50) + (50 if has_type_hints else 0)

    return analysis


# ============================================================================
# CODEBASE INDEXING
# ============================================================================


def build_current_codebase_index(dirs: list[str]) -> dict[str, set[str]]:
    """Build index of all entities in current codebase."""
    index = {
        "classes": set(),
        "functions": set(),
        "agents": set(),
        "models": set(),
        "methods": set(),
    }

    for dir_path in dirs:
        for py_file in Path(dir_path).rglob("*.py"):
            if "__pycache__" in str(py_file) or "archives" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        index["classes"].add(node.name.lower())
                        if node.name.endswith("Agent"):
                            index["agents"].add(node.name.lower())
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                                index["methods"].add(item.name.lower())
                    elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                        index["functions"].add(node.name.lower())
            # guardian: allow-silent-swallow
            except:
                continue

    return index


def calculate_uniqueness(
    analysis: FileAnalysis,
    codebase_index: dict[str, set[str]],
) -> tuple[float, list[str]]:
    """Calculate how unique the file's entities are compared to codebase."""
    if not analysis.entities:
        return 0.0, []

    unique_entities = []
    total_score = 0

    for entity in analysis.entities:
        name_lower = entity.name.lower()

        # Check if entity exists in codebase
        exists = False
        if entity.entity_type == "agent":
            exists = name_lower in codebase_index["agents"]
        elif entity.entity_type in ("class", "model", "mixin"):
            exists = name_lower in codebase_index["classes"]
        elif entity.entity_type == "function":
            exists = name_lower in codebase_index["functions"]

        if not exists:
            unique_entities.append(entity.name)
            # Weight by entity type
            if entity.entity_type == "agent":
                total_score += 30
            elif entity.entity_type == "model":
                total_score += 20
            elif entity.entity_type == "class":
                total_score += 15
            elif entity.entity_type == "function":
                total_score += 10

    # Normalize to 0-100
    max_possible = len(analysis.entities) * 30
    uniqueness = (total_score / max_possible * 100) if max_possible > 0 else 0

    return uniqueness, unique_entities


# ============================================================================
# MAIN ANALYSIS
# ============================================================================


def main():
    print("=" * 80)
    print("COMPREHENSIVE ARCHIVE ANALYSIS")
    print("Advanced AST-based analysis of all archived files")
    print("=" * 80)

    # Build current codebase index
    print("\n[1/4] Building current codebase index...")
    current_dirs = ["agentic_core", "apps_rg", "apps_lic", "apps_shared", "scripts"]
    codebase_index = build_current_codebase_index(current_dirs)
    print(
        f"  Indexed: {len(codebase_index['classes'])} classes, {len(codebase_index['agents'])} agents, {len(codebase_index['functions'])} functions",
    )

    # Scan archives
    print("\n[2/4] Scanning archive folders...")
    archives_root = Path("archives")

    # Priority archives to analyze (most likely to have useful content)
    priority_archives = [
        "apps_lic",
        "apps_rg",
        "apps_shared",
        "Reachout Engine Archive",
        "legacy_agents",
        "legacy_orchestrators",
        "legacy_validators",
        "deprecated_agents",
        "consolidated_agents",
    ]

    all_analyses: list[FileAnalysis] = []
    archive_stats = defaultdict(lambda: {"files": 0, "agents": 0, "unique": 0})

    for archive_name in priority_archives:
        archive_path = archives_root / archive_name
        if not archive_path.exists():
            continue

        py_files = list(archive_path.rglob("*.py"))
        archive_stats[archive_name]["files"] = len(py_files)

        for py_file in py_files:
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue

            analysis = analyze_file(py_file, archive_name)
            if analysis and not analysis.has_syntax_error:
                # Calculate uniqueness
                uniqueness, unique_entities = calculate_uniqueness(analysis, codebase_index)
                analysis.unique_score = uniqueness

                # Count agents
                agents = [e for e in analysis.entities if e.entity_type == "agent"]
                archive_stats[archive_name]["agents"] += len(agents)

                if uniqueness > 50:
                    archive_stats[archive_name]["unique"] += 1

                all_analyses.append(analysis)

    print(f"  Analyzed {len(all_analyses)} files across {len(priority_archives)} archives")

    # Identify restoration candidates
    print("\n[3/4] Identifying restoration candidates...")

    # Categorize by recommendation
    restore_high = []  # Unique agents/critical functionality
    restore_medium = []  # Unique utilities/models
    review_needed = []  # Partial overlap, needs manual review
    skip_exists = []  # Already in codebase
    skip_low_quality = []  # Syntax errors or low quality

    for analysis in all_analyses:
        if analysis.has_syntax_error:
            skip_low_quality.append(analysis)
            continue

        agents = [e for e in analysis.entities if e.entity_type == "agent"]
        [e for e in analysis.entities if e.entity_type == "model"]

        if analysis.unique_score >= 80:
            if agents:
                restore_high.append(analysis)
            else:
                restore_medium.append(analysis)
        elif analysis.unique_score >= 50:
            restore_medium.append(analysis)
        elif analysis.unique_score >= 20:
            review_needed.append(analysis)
        else:
            skip_exists.append(analysis)

    # Generate report
    print("\n[4/4] Generating report...")

    report = []
    report.append("=" * 80)
    report.append("ARCHIVE RESTORATION FINDINGS & RECOMMENDATIONS")
    report.append("=" * 80)
    report.append("\nAnalysis Date: 2026-01-20")
    report.append(f"Total Files Analyzed: {len(all_analyses)}")
    report.append(
        f"Current Codebase: {len(codebase_index['agents'])} agents, {len(codebase_index['classes'])} classes",
    )

    # Archive summary
    report.append("\n" + "=" * 80)
    report.append("ARCHIVE SUMMARY")
    report.append("=" * 80)
    for archive_name, stats in sorted(archive_stats.items(), key=lambda x: -x[1]["unique"]):
        report.append(f"\n  {archive_name}:")
        report.append(
            f"    Files: {stats['files']}, Agents: {stats['agents']}, High-Unique: {stats['unique']}",
        )

    # HIGH PRIORITY RESTORATIONS
    report.append("\n" + "=" * 80)
    report.append("HIGH PRIORITY RESTORATIONS (Unique Agents)")
    report.append("=" * 80)
    report.append(f"\nTotal: {len(restore_high)} files")

    for analysis in sorted(restore_high, key=lambda x: -x.unique_score)[:20]:
        agents = [e for e in analysis.entities if e.entity_type == "agent"]
        report.append(f"\n  [{analysis.unique_score:.0f}%] {Path(analysis.path).name}")
        report.append(f"    Archive: {analysis.archive_folder}")
        report.append(f"    Domain: {analysis.domain.upper()}")
        report.append(f"    Agents: {[a.name for a in agents]}")
        if agents and agents[0].docstring:
            report.append(f"    Purpose: {agents[0].docstring[:80]}...")

        # Recommend target
        if analysis.domain == "outreach":
            target = "apps_lic/engines/"
        elif analysis.domain == "resume":
            target = "apps_rg/engines/"
        else:
            target = "apps_shared/base_agents/"
        report.append(f"    RESTORE TO: {target}")

    # MEDIUM PRIORITY
    report.append("\n" + "=" * 80)
    report.append("MEDIUM PRIORITY RESTORATIONS (Unique Utilities/models)")
    report.append("=" * 80)
    report.append(f"\nTotal: {len(restore_medium)} files")

    for analysis in sorted(restore_medium, key=lambda x: -x.unique_score)[:15]:
        entities = [e.name for e in analysis.entities if e.entity_type != "function"][:5]
        report.append(f"\n  [{analysis.unique_score:.0f}%] {Path(analysis.path).name}")
        report.append(f"    Archive: {analysis.archive_folder}")
        report.append(f"    Domain: {analysis.domain.upper()}")
        report.append(f"    Entities: {entities}")

        if analysis.domain == "outreach":
            target = "apps_lic/engines/utils/"
        elif analysis.domain == "resume":
            target = "apps_rg/engines/utils/"
        else:
            target = "apps_shared/common_utils/"
        report.append(f"    RESTORE TO: {target}")

    # REVIEW NEEDED
    report.append("\n" + "=" * 80)
    report.append("REVIEW NEEDED (Partial Overlap)")
    report.append("=" * 80)
    report.append(f"\nTotal: {len(review_needed)} files")
    report.append("These files have some unique content but significant overlap with current codebase.")

    for analysis in sorted(review_needed, key=lambda x: -x.unique_score)[:10]:
        report.append(f"\n  [{analysis.unique_score:.0f}%] {Path(analysis.path).name}")
        report.append(f"    Archive: {analysis.archive_folder}")
        report.append(f"    Entities: {[e.name for e in analysis.entities][:5]}")

    # SKIP
    report.append("\n" + "=" * 80)
    report.append("SKIP (Already Exists or Low Quality)")
    report.append("=" * 80)
    report.append(f"\nAlready in codebase: {len(skip_exists)} files")
    report.append(f"Syntax errors/low quality: {len(skip_low_quality)} files")

    # SUMMARY
    report.append("\n" + "=" * 80)
    report.append("EXECUTIVE SUMMARY")
    report.append("=" * 80)
    report.append(f"""
    HIGH PRIORITY (restore immediately):     {len(restore_high)} files
    MEDIUM PRIORITY (restore as needed):     {len(restore_medium)} files
    REVIEW NEEDED (manual inspection):       {len(review_needed)} files
    SKIP (exists or low quality):            {len(skip_exists) + len(skip_low_quality)} files

    TOTAL RESTORATION CANDIDATES:            {len(restore_high) + len(restore_medium)} files
    """)

    # Top 10 restoration commands
    report.append("\n" + "=" * 80)
    report.append("TOP 10 RESTORATION COMMANDS")
    report.append("=" * 80)

    top_restores = sorted(restore_high + restore_medium, key=lambda x: -x.unique_score)[:10]
    for analysis in top_restores:
        src = analysis.path
        if analysis.domain == "outreach":
            dst = "apps_lic/engines/"
        elif analysis.domain == "resume":
            dst = "apps_rg/engines/"
        else:
            dst = "apps_shared/"

        filename = Path(analysis.path).name
        report.append(f'\ncp "{src}" "{dst}{filename}"')

    # Print and save report
    report_text = "\n".join(report)
    print(report_text)

    # Save to file
    report_path = Path("docs/ARCHIVE_ANALYSIS_REPORT.md")
    assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
    report_path.write_text(report_text, encoding="utf-8")
    print(f"\n\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
