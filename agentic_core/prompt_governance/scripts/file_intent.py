#!/usr/bin/env python3
"""
HARDENED Naming Convention Audit (Phase 6)
ENFORCES: Sovereign Naming Law with AST-based Content Analysis

CRITICAL IMPROVEMENTS:
1. AST parsing for accurate class/function detection
2. Content-first analysis (not filename heuristics)
3. Bidirectional validation (name↔content cross-reference)
4. Semantic intent classification
5. Confidence scoring with manual review triggers
"""

import ast
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class FileIntent(Enum):
    """Semantic classification of file purpose."""

    CLASS_EXPORT = "Primary Class/Agent Export"
    UTILITY_MODULE = "Utility/Configuration Module"
    MIXED_CONTENT = "Mixed Content (Multiple Classes)"
    DATA_MODULE = "Data/Constants Module"
    SCRIPT_MODULE = "Executable Script"
    UNCLEAR = "Unclassified/Edge Case"


class NamingConvention(Enum):
    """Naming convention types."""

    PASCAL_CASE = "PascalCase"
    SNAKE_CASE = "snake_case"
    INVALID = "Invalid"


@dataclass
class ViolationReport:
    """Detailed violation analysis."""

    file_path: str
    current_name: str
    detected_intent: FileIntent
    current_naming: NamingConvention
    proposed_name: str
    rationale: str
    confidence: float
    requires_manual_review: bool
    ast_analysis: dict


class HardenedNamingAuditor:
    """
    HARDENED auditor that would have caught pii.py violation.
    Uses AST parsing and semantic analysis instead of filename heuristics.
    """

    def __init__(self, target_directory: Path):
        self.target_directory = target_directory
        self.violations = []
        self.confident_files = []
        self.manual_review_required = []

    def analyze_file_content(self, file_path: Path) -> dict:
        """
        CRITICAL: Parse AST and extract semantic content.
        This is what was missing from the original audit.
        """
        try:
            content = file_path.read_text(encoding="utf-8")

            # Parse AST for accurate structure analysis
            tree = ast.parse(content)

            # Extract all classes and functions
            classes = []
            functions = []
            imports = []
            constants = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Get class details including decorators and inheritance
                    class_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "is_agent": self._is_agent_class(node, content),
                        "has_methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                        > 0,
                        "inherits_from_agent": self._inherits_from_agent(node),
                        "docstring": ast.get_docstring(node) or "",
                    }
                    classes.append(class_info)

                elif isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "is_private": node.name.startswith("_"),
                        "is_dunder": node.name.startswith("__") and node.name.endswith("__"),
                    }
                    functions.append(func_info)

                elif isinstance(node, ast.Import | ast.ImportFrom):
                    imports.append(ast.unparse(node))

                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            constants.append(target.id)

            return {
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "constants": constants,
                "line_count": len(content.splitlines()),
                "has_main": "__main__" in content,
                "content_preview": content[:200] + "..." if len(content) > 200 else content,
            }

        except Exception as e:
            return {"error": str(e)}

    def _is_agent_class(self, class_node: ast.ClassDef, content: str) -> bool:
        """Detect if class is an Agent (SovereignBaseAgent inheritance or naming)."""
        # Check inheritance
        for base in class_node.bases:
            if isinstance(base, ast.Name) and "Agent" in base.id:
                return True
            if isinstance(base, ast.Attribute) and "Agent" in str(base):
                return True

        # Check naming pattern
        if class_node.name.endswith("Agent"):
            return True

        # Check docstring for agent keywords
        docstring = ast.get_docstring(class_node) or ""
        agent_keywords = ["agent", "sovereign", "validator", "governor", "healer"]
        if any(keyword in docstring.lower() for keyword in agent_keywords):
            return True

        return False

    def _inherits_from_agent(self, class_node: ast.ClassDef) -> bool:
        """Check if class inherits from any Agent base class."""
        agent_bases = ["SovereignBaseAgent", "Agent", "ValidatorAgent"]
        for base in class_node.bases:
            if isinstance(base, ast.Name) and any(
                agent_base in base.id for agent_base in agent_bases
            ):
                return True
        return False

    def classify_file_intent(self, analysis: dict, file_path: Path) -> tuple[FileIntent, float]:
        """
        CRITICAL: Semantic classification based on content, not filename.
        This would have correctly classified pii.py as CLASS_EXPORT.
        """
        if "error" in analysis:
            return FileIntent.UNCLEAR, 0.0

        classes = analysis["classes"]
        functions = analysis["functions"]
        constants = analysis["constants"]

        # PRIMARY LOGIC: Class Export Detection
        primary_classes = [c for c in classes if c["is_agent"] or c["inherits_from_agent"]]

        if primary_classes and len(primary_classes) == 1:
            # Single primary class/agent - HIGH confidence
            return FileIntent.CLASS_EXPORT, 0.95

        elif len(classes) >= 1 and not functions:
            # Multiple classes, no functions - likely data models
            return FileIntent.DATA_MODULE, 0.85

        elif len(classes) == 1 and len(primary_classes) == 0:
            # Single non-agent class - check if it's primary export
            if classes[0]["has_methods"] and classes[0]["line"] < 20:
                return FileIntent.CLASS_EXPORT, 0.75
            else:
                return FileIntent.UTILITY_MODULE, 0.65

        elif functions and not classes:
            # Functions only - utility module
            if analysis["has_main"]:
                return FileIntent.SCRIPT_MODULE, 0.90
            else:
                return FileIntent.UTILITY_MODULE, 0.85

        elif constants and not classes and not functions:
            # Constants only - configuration/data
            return FileIntent.DATA_MODULE, 0.90

        elif classes and functions:
            # Mixed content - needs manual review
            return FileIntent.MIXED_CONTENT, 0.50

        else:
            return FileIntent.UNCLEAR, 0.30

    def detect_naming_convention(self, filename: str) -> NamingConvention:
        """Detect naming convention with strict validation."""
        if not filename.endswith(".py"):
            return NamingConvention.INVALID

        base_name = filename[:-3]  # Remove .py extension

        # PascalCase detection
        if re.match(r"^[A-Z][a-zA-Z0-9]*$", base_name):
            return NamingConvention.PASCAL_CASE

        # snake_case detection
        elif re.match(r"^[a-z][a-z0-9_]*$", base_name):
            return NamingConvention.SNAKE_CASE

        else:
            return NamingConvention.INVALID

    def validate_naming_compliance(self, file_path: Path) -> ViolationReport | None:
        """
        CRITICAL: Cross-reference naming with semantic intent.
        This is where pii.py would have been caught.
        """
        filename = file_path.name

        # Skip __init__.py and test files
        if filename == "__init__.py" or filename.startswith("test_"):
            return None

        analysis = self.analyze_file_content(file_path)
        if "error" in analysis:
            return None

        intent, confidence = self.classify_file_intent(analysis, file_path)
        naming = self.detect_naming_convention(filename)

        # CORE VALIDATION LOGIC
        violation = None

        # Rule 1: Class/Agent exports MUST be in PascalCase files
        if intent == FileIntent.CLASS_EXPORT and naming != NamingConvention.PASCAL_CASE:
            primary_class = analysis["classes"][0]["name"]
            violation = ViolationReport(
                file_path=str(file_path),
                current_name=filename,
                detected_intent=intent,
                current_naming=naming,
                proposed_name=f"{primary_class}.py",
                rationale=f"Primary class export '{primary_class}' found in snake_case file. Violates: 'PascalCase files should contain primary class/agent exports'",
                confidence=confidence,
                requires_manual_review=confidence < 0.8,
                ast_analysis=analysis,
            )

        # Rule 2: Utility modules MUST be in snake_case files
        elif (
            intent in [FileIntent.UTILITY_MODULE, FileIntent.SCRIPT_MODULE]
            and naming != NamingConvention.SNAKE_CASE
        ):
            violation = ViolationReport(
                file_path=str(file_path),
                current_name=filename,
                detected_intent=intent,
                current_naming=naming,
                proposed_name=self._to_snake_case(filename),
                rationale=f"Utility module with {len(analysis['functions'])} functions found in PascalCase file. Violates: 'snake_case files should contain utilities/scripts'",
                confidence=confidence,
                requires_manual_review=confidence < 0.8,
                ast_analysis=analysis,
            )

        # Rule 3: Mixed content requires manual review
        elif intent == FileIntent.MIXED_CONTENT:
            violation = ViolationReport(
                file_path=str(file_path),
                current_name=filename,
                detected_intent=intent,
                current_naming=naming,
                proposed_name="MANUAL_REVIEW_REQUIRED",
                rationale=f"Mixed content: {len(analysis['classes'])} classes and {len(analysis['functions'])} functions. Requires architectural decision",
                confidence=0.5,
                requires_manual_review=True,
                ast_analysis=analysis,
            )

        return violation

    def _to_snake_case(self, pascal_name: str) -> str:
        """Convert PascalCase to snake_case."""
        # Remove .py extension
        base_name = pascal_name[:-3] if pascal_name.endswith(".py") else pascal_name

        # Convert PascalCase to snake_case
        snake = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", base_name)
        snake = re.sub("([a-z0-9])([A-Z])", r"\1_\2", snake)
        snake = snake.lower()

        return f"{snake}.py"

    def scan_directory(self) -> list[ViolationReport]:
        """Scan directory and identify all naming violations."""
        print("🔍 HARDENED Naming Convention Audit")
        print("=" * 50)
        print(f"Scanning: {self.target_directory}")
        print()

        python_files = list(self.target_directory.rglob("*.py"))
        total_files = len(python_files)

        print(f"Found {total_files} Python files to analyze...")
        print()

        for i, file_path in enumerate(python_files, 1):
            print(f"Analyzing [{i:3d}/{total_files}]: {file_path.name}")

            violation = self.validate_naming_compliance(file_path)

            if violation:
                self.violations.append(violation)
                if violation.requires_manual_review:
                    self.manual_review_required.append(violation)
                else:
                    self.confident_files.append(violation)

                print(f"  ❌ VIOLATION: {violation.rationale}")
            else:
                print("  ✅ Compliant")

        return self.violations

    def generate_disposition_table(self) -> str:
        """Generate comprehensive disposition table."""
        table = []
        table.append("| Current Name | Detected Intent | Proposed Name | Rationale | Confidence |")
        table.append("|-------------|----------------|---------------|-----------|------------|")

        for violation in self.violations:
            confidence_icon = "🔺" if violation.confidence < 0.8 else "✅"
            manual_icon = "👁️" if violation.requires_manual_review else " "

            table.append(
                f"| {violation.current_name} | {violation.detected_intent.value} | {violation.proposed_name} | {violation.rationale} | {confidence_icon}{violation.confidence:.2f} {manual_icon} |"
            )

        return "\n".join(table)

    def print_summary(self):
        """Print comprehensive audit summary."""
        print("\n" + "=" * 80)
        print("🎯 HARDENED NAMING AUDIT RESULTS")
        print("=" * 80)

        print("\n📊 SUMMARY:")
        print(f"  Total violations found: {len(self.violations)}")
        print(f"  High confidence violations: {len(self.confident_files)}")
        print(f"  Manual review required: {len(self.manual_review_required)}")

        if self.violations:
            print("\n🚨 VIOLATIONS DETECTED:")
            print(self.generate_disposition_table())

            if self.manual_review_required:
                print("\n👁️ FILES REQUIRING MANUAL REVIEW:")
                for violation in self.manual_review_required:
                    print(f"  • {violation.current_name}: {violation.detected_intent.value}")

        else:
            print("\n✅ ZERO NAMING VIOLATIONS - Perfect compliance achieved!")


def main():
    """Execute hardened naming audit."""
    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1])
    else:
        target_dir = Path("agentic_core/prompt_governance")

    if not target_dir.exists():
        print(f"❌ Directory not found: {target_dir}")
        sys.exit(1)

    auditor = HardenedNamingAuditor(target_dir)
    violations = auditor.scan_directory()
    auditor.print_summary()

    # Exit code based on violations
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
