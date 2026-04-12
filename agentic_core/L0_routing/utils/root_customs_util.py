"""Root Customs Utility - AST-based file routing without agent overhead.

This module provides deterministic file routing functionality previously
implemented in RootCustomsAgent. Converted from agent to utility script
as part of Phase 2 optimization (Wave 5).

Usage:
    from agentic_core.L0_routing.utils.root_customs_util import (
        scan_root_directory, analyze_content_signatures,
        determine_routing, run_inspection
    )

    # Run inspection
    results = run_inspection(project_root=Path("."), dry_run=True)
"""

from __future__ import annotations

import ast
import json
import re
import shutil
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    AST_PLACEMENT_SIGNALS,
    ROOT_ALLOWED_PATTERNS,
    ROOT_PROTECTED_FILES,
    get_validated_project_root,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)


@dataclass
class RoutingDecision:
    """Represents a routing decision for a file."""

    file_path: Path
    destination: str | None = None
    reason: str = ""
    confidence: float = 0.0
    content_matches: dict[str, Any] = field(default_factory=dict)
    ast_matches: dict[str, Any] = field(default_factory=dict)
    is_protected: bool = False
    is_allowed_pattern: bool = False


class ASTAnalyzer:
    """Analyzes Python files for AST-based routing signals."""

    def __init__(self):
        self.imports: list[str] = []
        self.decorators: list[str] = []
        self.class_names: list[str] = []
        self.function_calls: list[str] = []
        self.docstring_markers: list[str] = []

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """Analyze Python file for AST signals."""
        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"root_customs_util.analyze_file:{file_path.name}",
        )
        if not file_path.suffix == ".py":
            return {}

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            self._extract_signals(tree)

            return {
                "imports": self.imports,
                "decorators": self.decorators,
                "class_names": self.class_names,
                "function_calls": self.function_calls,
                "docstring_markers": self.docstring_markers,
            }

        except (ValueError, TypeError, RuntimeError) as e:
            return {"error": str(e)}

    def _extract_signals(self, tree: ast.AST):
        """Extract AST signals from parsed tree."""
        self.imports = []
        self.decorators = []
        self.class_names = []
        self.function_calls = []
        self.docstring_markers = []

        for node in ast.walk(tree):
            # Extract imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imports.append(node.module)

            # Extract decorators
            elif isinstance(node, ast.ClassDef):
                self.class_names.append(node.name)
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        self.decorators.append(f"@{decorator.id}")
                    elif isinstance(decorator, ast.Attribute):
                        self.decorators.append(f"@{decorator.attr}")

                # Check docstring for markers
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                ):
                    docstring = node.body[0].value.value
                    if isinstance(docstring, str):
                        for marker in ["DEPRECATED", "LEGACY", "DO NOT USE", "MOVED TO"]:
                            if marker in docstring.upper():
                                self.docstring_markers.append(marker)

            # Extract function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "warn":
                        self.function_calls.append("warnings.warn")
                elif isinstance(node.func, ast.Name):
                    if node.func.id == "warn":
                        self.function_calls.append("warnings.warn")


def scan_root_directory(project_root: Path) -> list[Path]:
    """Scan the project root for files to analyze."""
    root_files = []

    for item in project_root.iterdir():
        if item.is_file():
            # Skip hidden files and protected files
            if not item.name.startswith(".") and item.name not in ROOT_PROTECTED_FILES:
                root_files.append(item)

    print(f"📋 Found {len(root_files)} files in root to analyze")
    return root_files


def check_allowed_patterns(file_path: Path) -> bool:
    """Check if file matches any allowed root patterns."""
    for pattern in ROOT_ALLOWED_PATTERNS:
        if pattern.match(file_path.name):
            return True
    return False


def analyze_content_signatures(file_path: Path) -> dict[str, Any]:
    """Analyze file content for routing signatures."""
    content_matches: dict[str, Any] = {}

    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Check file extension
        ext = file_path.suffix.lower()

        # Analyze based on file type
        if ext == ".md":
            content_matches.update(_analyze_markdown(content))
        elif ext == ".json":
            content_matches.update(_analyze_json(content))
        else:
            content_matches.update(_analyze_text(content))

    except (ValueError, TypeError, RuntimeError) as e:
        content_matches["error"] = str(e)

    return content_matches


def _analyze_markdown(content: str) -> dict[str, Any]:
    """Analyze markdown content for headers and keywords."""
    matches = {"headers": [], "keywords": []}

    # Extract headers
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            matches["headers"].append(line)

    # Check keywords
    content_lower = content.lower()
    for keyword in ["critical", "assessment", "findings", "report", "analysis"]:
        if keyword in content_lower:
            matches["keywords"].append(keyword)

    return matches


def _analyze_json(content: str) -> dict[str, Any]:
    """Analyze JSON content for key signatures."""
    matches: dict[str, Any] = {"json_keys": []}

    try:
        data = json.loads(content)

        def extract_keys(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    matches["json_keys"].append(key)
                    if isinstance(value, dict | list):
                        extract_keys(value, full_key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, dict | list):
                        extract_keys(item, f"{prefix}[{i}]")

        extract_keys(data)

    except json.JSONDecodeError:
        matches["error"] = "Invalid JSON"

    return matches


def _analyze_text(content: str) -> dict[str, Any]:
    """Analyze plain text content for keywords."""
    matches = {"keywords": []}

    # Common log/error keywords
    error_keywords = ["debug", "error", "exception", "traceback", "mission", "trace"]
    content_lower = content.lower()

    for keyword in error_keywords:
        if keyword in content_lower:
            matches["keywords"].append(keyword)

    return matches


def determine_routing(
    file_path: Path,
    content_matches: dict[str, Any],
    ast_matches: dict[str, Any],
) -> RoutingDecision:
    """Determine where a file should be routed using enhanced analysis."""

    # Check if protected
    if file_path.name in ROOT_PROTECTED_FILES:
        return RoutingDecision(
            file_path=file_path,
            destination=None,
            reason="Protected file - cannot be moved",
            confidence=1.0,
            content_matches=content_matches,
            ast_matches=ast_matches,
            is_protected=True,
        )

    # Check if matches allowed patterns
    if check_allowed_patterns(file_path):
        return RoutingDecision(
            file_path=file_path,
            destination=None,
            reason="Matches allowed root pattern",
            confidence=1.0,
            content_matches=content_matches,
            ast_matches=ast_matches,
            is_allowed_pattern=True,
        )

    # Check Test Taxonomy Signals
    if file_path.suffix == ".py" and "test" in file_path.name.lower():
        test_routing = _determine_test_routing(file_path, ast_matches)
        if test_routing:
            return test_routing

    # Check Legacy/Zombie Signals
    if file_path.suffix == ".py":
        legacy_routing = _determine_legacy_routing(file_path, ast_matches)
        if legacy_routing:
            return legacy_routing

    # Check AST Placement Signals
    if file_path.suffix == ".py":
        ast_routing = _determine_ast_placement_routing(file_path, ast_matches)
        if ast_routing:
            return ast_routing

    # Check against ARTIFACT_ROUTING_MAP (original logic)
    from agentic_core.L0_routing.reasoning.RootCustomsAgent import ARTIFACT_ROUTING_MAP

    best_match = None
    best_score = 0

    for destination, config in ARTIFACT_ROUTING_MAP.items():
        score = _calculate_routing_score(file_path, content_matches, config)
        if score > best_score:
            best_score = score
            best_match = (destination, config)

    if best_match and best_score > 0:
        destination, config = best_match
        return RoutingDecision(
            file_path=file_path,
            destination=destination,
            reason=f"Content matches {destination} routing rules (score: {best_score:.2f})",
            confidence=best_score,
            content_matches=content_matches,
            ast_matches=ast_matches,
        )

    return RoutingDecision(
        file_path=file_path,
        destination=None,
        reason="No matching routing rule found",
        confidence=0.0,
        content_matches=content_matches,
        ast_matches=ast_matches,
    )


def _determine_test_routing(file_path: Path, ast_matches: dict[str, Any]) -> RoutingDecision | None:
    """Determine test routing based on AST signals."""
    imports = ast_matches.get("imports", [])
    decorators = ast_matches.get("decorators", [])
    class_names = ast_matches.get("class_names", [])

    best_match = None
    best_score = 0

    from agentic_core.L0_routing.reasoning.RootCustomsAgent import TEST_TYPE_SIGNALS

    for destination, config in TEST_TYPE_SIGNALS.items():
        score = 0

        # Check required imports
        for imp in config.get("imports", []):
            if any(imp in import_name for import_name in imports):
                score += 0.4

        # Check forbidden imports (penalty)
        for forbidden in config.get("forbidden_imports", []):
            if any(forbidden in import_name for import_name in imports):
                score -= 0.5

        # Check decorators
        for decorator in config.get("decorators", []):
            if decorator in decorators:
                score += 0.3

        # Check class patterns
        for pattern in config.get("class_patterns", []):
            for class_name in class_names:
                if re.match(pattern, class_name):
                    score += 0.3
                    break

        if score > best_score:
            best_score = score
            best_match = (destination, config)

    if best_match and best_score > 0:
        destination, config = best_match
        return RoutingDecision(
            file_path=file_path,
            destination=destination,
            reason=f"AST test taxonomy: {config['description']} (score: {best_score:.2f})",
            confidence=best_score,
            ast_matches=ast_matches,
        )

    return None


def _determine_legacy_routing(
    file_path: Path,
    ast_matches: dict[str, Any],
) -> RoutingDecision | None:
    """Determine legacy routing based on AST signals."""
    decorators = ast_matches.get("decorators", [])
    docstring_markers = ast_matches.get("docstring_markers", [])
    class_names = ast_matches.get("class_names", [])
    function_calls = ast_matches.get("function_calls", [])

    from agentic_core.L0_routing.reasoning.RootCustomsAgent import LEGACY_AST_SIGNALS

    config = LEGACY_AST_SIGNALS["archives/legacy_code"]
    score = 0

    # Check decorators
    for decorator in config.get("decorators", []):
        if decorator in decorators:
            score += 0.4

    # Check docstring markers
    for marker in config.get("docstring_markers", []):
        if marker in docstring_markers:
            score += 0.3

    # Check class patterns
    for pattern in config.get("class_patterns", []):
        for class_name in class_names:
            if re.match(pattern, class_name):
                score += 0.3
                break

    # Check function calls
    for call in config.get("function_calls", []):
        if call in function_calls:
            score += 0.2

    if score > 0.3:  # Threshold for legacy detection
        return RoutingDecision(
            file_path=file_path,
            destination="archives/legacy_code",
            reason=f"AST legacy detection: {config['description']} (score: {score:.2f})",
            confidence=score,
            ast_matches=ast_matches,
        )

    return None


def _determine_ast_placement_routing(
    file_path: Path,
    ast_matches: dict[str, Any],
) -> RoutingDecision | None:
    """Determine AST placement routing."""
    imports = ast_matches.get("imports", [])
    class_names = ast_matches.get("class_names", [])

    best_match = None
    best_score = 0

    for destination, config in AST_PLACEMENT_SIGNALS.items():
        score = 0

        # Check import signals
        for imp in config.get("import_signals", []):
            if any(imp in import_name for import_name in imports):
                score += 0.3

        # Check class patterns
        for pattern in config.get("class_patterns", []):
            for class_name in class_names:
                if re.match(pattern, class_name):
                    score += 0.3
                    break

        # Apply weight
        weight = config.get("weight", 1)
        score = score * (weight / 100)

        if score > best_score:
            best_score = score
            best_match = (destination, config)

    if best_match and best_score > 0.2:  # Threshold for AST placement
        destination, config = best_match
        return RoutingDecision(
            file_path=file_path,
            destination=destination,
            reason=f"AST placement: {destination} (score: {best_score:.2f})",
            confidence=best_score,
            ast_matches=ast_matches,
        )

    return None


def _calculate_routing_score(
    file_path: Path,
    content_matches: dict[str, Any],
    config: dict[str, Any],
) -> float:
    """Calculate routing score for a destination configuration."""
    score = 0.0

    # Check forbidden extensions (exclude if matches)
    ext = file_path.suffix.lower()
    if "forbidden_extensions" in config:
        if ext in config.get("forbidden_extensions", []):
            return 0.0  # Explicit exclusion

    # Check file extension
    if ext in config.get("file_extensions", []):
        score += 0.3

    # Check naming patterns
    for pattern in config.get("naming_patterns", []):
        if pattern.match(file_path.name):
            score += 0.3
            break

    # Check content signals
    content_signals = config.get("content_signals", {})

    # Headers
    if "headers" in content_matches:
        file_headers = [h.lower() for h in content_matches["headers"]]
        for header in content_signals.get("headers", []):
            if any(header.lower() in fh for fh in file_headers):
                score += 0.2
                break

    # JSON keys
    if "json_keys" in content_matches:
        file_keys = [k.lower() for k in content_matches["json_keys"]]
        for key in content_signals.get("json_keys", []):
            if any(key.lower() in fk for fk in file_keys):
                score += 0.2
                break

    # Keywords
    if "keywords" in content_matches:
        file_keywords = [k.lower() for k in content_matches["keywords"]]
        for keyword in content_signals.get("keywords", []):
            if any(keyword.lower() in fk for fk in file_keywords):
                score += 0.1
                break

    # Check forbidden keywords (penalty)
    if "forbidden_keywords" in config and "keywords" in content_matches:
        file_keywords = [k.lower() for k in content_matches["keywords"]]
        for forbidden in config.get("forbidden_keywords", []):
            if any(forbidden.lower() in fk for fk in file_keywords):
                score -= 0.5  # Penalty for forbidden content
                break

    return max(0.0, min(score, 1.0))  # Cap at 1.0, floor at 0.0


def execute_routing(
    decision: RoutingDecision,
    project_root: Path,
    dry_run: bool = True,
) -> bool:
    """Execute a routing decision."""
    if not decision.destination or dry_run:
        return False

    source = decision.file_path
    target_dir = project_root / decision.destination
    target_file = target_dir / source.name

    try:
        # Create target directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)

        # Move the file
        assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
        shutil.move(str(source), str(target_file))
        print(f"✅ Moved: {source.name} → {decision.destination}/")
        return True

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ Failed to move {source.name}: {e}")
        return False


def run_inspection(
    project_root: Path | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Run complete enhanced root inspection and routing.

    Args:
        project_root: Project root path (defaults to validated project root)
        dry_run: If True, only analyze without moving files

    Returns:
        Dictionary with inspection results
    """
    print("🔍 Starting Enhanced Root Inspection...")
    print("=" * 70)

    project_root = project_root or get_validated_project_root()
    root_files = scan_root_directory(project_root)
    routing_decisions: list[RoutingDecision] = []
    ast_analyzer = ASTAnalyzer()

    for file_path in root_files:
        print(f"\n📄 Analyzing: {file_path.name}")

        # Analyze content
        content_matches = analyze_content_signatures(file_path)

        # Analyze AST for Python files
        ast_matches: dict[str, Any] = {}
        if file_path.suffix == ".py":
            ast_matches = ast_analyzer.analyze_file(file_path)

        # Determine routing
        decision = determine_routing(file_path, content_matches, ast_matches)
        routing_decisions.append(decision)

        # Display decision
        if decision.is_protected:
            status_icon = "🛡️"
        elif decision.is_allowed_pattern:
            status_icon = "✅"
        elif decision.destination:
            if "AST" in decision.reason:
                status_icon = "🧠"
            else:
                status_icon = "📦"
        else:
            status_icon = "❓"

        print(f"   {status_icon} {decision.reason}")

        if decision.destination:
            print(f"   🎯 Destination: {decision.destination}/")

        # Show content matches
        if decision.content_matches:
            for match_type, matches in decision.content_matches.items():
                if matches and match_type != "error":
                    print(f"   🔍 {match_type.title()}: {matches[:3]}{'...' if len(matches) > 3 else ''}")

        # Show AST matches for Python files
        if decision.ast_matches:
            for match_type, matches in decision.ast_matches.items():
                if matches and match_type != "error":
                    print(
                        f"   🧠 AST {match_type.title()}: {matches[:3]}{'...' if len(matches) > 3 else ''}",
                    )

    # Summary
    _print_summary(routing_decisions, dry_run)

    # Execute routing if not dry run
    if not dry_run:
        print("\n🚀 Executing routing decisions...")
        moved_count = 0
        for decision in routing_decisions:
            if execute_routing(decision, project_root, dry_run):
                moved_count += 1
        print(f"✅ Moved {moved_count} files")

    return {
        "total_files": len(root_files),
        "routing_decisions": len(routing_decisions),
        "protected_files": sum(1 for d in routing_decisions if d.is_protected),
        "allowed_patterns": sum(1 for d in routing_decisions if d.is_allowed_pattern),
        "routed_files": sum(1 for d in routing_decisions if d.destination),
        "ast_routed_files": sum(1 for d in routing_decisions if d.destination and "AST" in d.reason),
        "unmatched_files": sum(
            1
            for d in routing_decisions
            if not d.destination and not d.is_protected and not d.is_allowed_pattern
        ),
    }


def _print_summary(routing_decisions: list[RoutingDecision], dry_run: bool) -> None:
    """Print enhanced inspection summary."""
    print("\n" + "=" * 70)
    print("📊 ENHANCED ROOT INSPECTION SUMMARY")
    print("=" * 70)

    total = len(routing_decisions)
    protected = sum(1 for d in routing_decisions if d.is_protected)
    allowed = sum(1 for d in routing_decisions if d.is_allowed_pattern)
    routed = sum(1 for d in routing_decisions if d.destination)
    ast_routed = sum(1 for d in routing_decisions if d.destination and "AST" in d.reason)
    unmatched = sum(
        1 for d in routing_decisions if not d.destination and not d.is_protected and not d.is_allowed_pattern
    )

    print(f"📁 Total Files Analyzed: {total}")
    print(f"🛡️ Protected Files: {protected}")
    print(f"✅ Allowed Patterns: {allowed}")
    print(f"📦 Files to Route: {routed}")
    print(f"🧠 AST-Routed Files: {ast_routed}")
    print(f"❓ Unmatched Files: {unmatched}")

    if routed > 0:
        print("\n🎯 ROUTING DECISIONS:")
        for decision in routing_decisions:
            if decision.destination:
                icon = "🧠" if "AST" in decision.reason else "📦"
                print(f"   {icon} {decision.file_path.name} → {decision.destination}/")

    print(f"\n🔍 Mode: {'DRY RUN (no files moved)' if dry_run else 'EXECUTE (files will be moved)'}")


def main():
    """Main entry point for the Root Customs Utility."""
    import argparse

    parser = argparse.ArgumentParser(description="Root Customs Utility - AST-Powered Routing")
    parser.add_argument("--execute", action="store_true", help="Execute routing (default: dry-run)")
    parser.add_argument("--project-root", type=str, help="Project root path")

    args = parser.parse_args()

    # Run inspection
    results = run_inspection(
        project_root=Path(args.project_root) if args.project_root else None,
        dry_run=not args.execute,
    )

    print("\n🎉 Root Customs Utility Complete!")
    return results


if __name__ == "__main__":
    main()
