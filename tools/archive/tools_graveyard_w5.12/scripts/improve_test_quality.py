#!/usr/bin/env python3
"""Test Quality Improvement Script - Phase 3 Implementation.

This script analyzes and improves test quality by:
1. Identifying weak assertions and suggesting improvements
2. Adding behavioral validation to existing tests
3. Improving test coverage with edge cases and error handling
4. Creating enhanced test files with comprehensive validation

Usage:
    python tools/improve_test_quality.py --analyze tests/unit/
    python tools/improve_test_quality.py --enhance tests/unit/specific_test.py
    python tools/improve_test_quality.py --coverage source/module.py tests/test_module.py
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from agentic_core.core.test_quality_framework import (
    TestCoverageAnalyzer,
    TestQualityAnalyzer,
    create_behavioral_test_template,
    strengthen_existing_assertions,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def analyze_test_quality(test_paths: list[Path]) -> bool:
    """Analyze test quality issues in specified test files."""
    analyzer = TestQualityAnalyzer()
    total_issues = 0

    for test_path in test_paths:
        if not test_path.exists():
            logger.warning(f"Test file not found: {test_path}")
            continue

        logger.info(f"Analyzing test quality: {test_path}")
        issues = analyzer.analyze_test_file(str(test_path))

        if issues:
            logger.warning(f"Found {len(issues)} issues in {test_path.name}")
            for issue in issues:
                logger.warning(f"  {issue.issue_type}: {issue.description}")
                if issue.suggested_improvement:
                    logger.info(f"    Suggestion: {issue.suggested_improvement}")
            total_issues += len(issues)
        else:
            logger.info(f"✅ No quality issues found in {test_path.name}")

    logger.info(f"Analysis complete. Total issues found: {total_issues}")
    return total_issues == 0


def enhance_test_assertions(test_path: Path) -> bool:
    """Enhance assertions in a specific test file."""
    if not test_path.exists():
        logger.error(f"Test file not found: {test_path}")
        return False

    logger.info(f"Enhancing assertions in: {test_path}")

    try:
        # Read original content
        with open(test_path, encoding="utf-8") as f:
            original_content = f.read()

        # Enhance assertions
        enhanced_content = strengthen_existing_assertions(str(test_path))

        # Write enhanced content
        enhanced_path = test_path.parent / f"{test_path.stem}_enhanced.py"
        with open(enhanced_path, "w", encoding="utf-8") as f:
            f.write(enhanced_content)

        logger.info(f"Enhanced test saved to: {enhanced_path}")
        return True

    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        logger.error(f"Failed to enhance test {test_path}: {e}")
        return False


def analyze_coverage_gaps(source_path: Path, test_path: Path) -> bool:
    """Analyze coverage gaps between source and test files."""
    if not source_path.exists():
        logger.error(f"Source file not found: {source_path}")
        return False

    if not test_path.exists():
        logger.error(f"Test file not found: {test_path}")
        return False

    logger.info(f"Analyzing coverage gaps: {source_path} <-> {test_path}")

    analyzer = TestCoverageAnalyzer()
    gaps = analyzer.analyze_coverage_gaps(str(source_path), str(test_path))

    if gaps:
        logger.warning(f"Found {len(gaps)} coverage gaps:")
        for gap in gaps:
            logger.warning(f"  - {gap}")
        return False
    else:
        logger.info("✅ No significant coverage gaps found")
        return True


def create_enhanced_test_template(source_path: Path, output_path: Path | None = None) -> bool:
    """Create an enhanced test template for a source file."""
    if not source_path.exists():
        logger.error(f"Source file not found: {source_path}")
        return False

    logger.info(f"Creating enhanced test template for: {source_path}")

    try:
        # Extract class and method information from source
        with open(source_path, encoding="utf-8") as f:
            source_content = f.read()

        # Simple parsing to extract class and method names
        # In a real implementation, this would use AST parsing
        import re

        class_pattern = r"class\s+(\w+)"
        method_pattern = r"def\s+(\w+)\s*\("

        classes = re.findall(class_pattern, source_content)
        methods = re.findall(method_pattern, source_content)

        if not classes:
            logger.warning("No classes found in source file")
            return False

        # Create enhanced test template
        main_class = classes[0]  # Use first class found
        template = create_behavioral_test_template(main_class, methods[:5])  # Limit to 5 methods

        # Save template
        if output_path is None:
            output_path = source_path.parent / "tests" / f"test_{source_path.stem}_enhanced.py"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f'"""Enhanced test for {source_path.name} with comprehensive validation.\n\n')
            f.write(f"Generated automatically from: {source_path.name}\n")
            f.write(f"Classes found: {classes}\n")
            f.write(f"Methods found: {methods[:10]}...\n")
            f.write('"""\n\n')
            f.write(template)

        logger.info(f"Enhanced test template created: {output_path}")
        return True

    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        logger.error(f"Failed to create test template: {e}")
        return False


def improve_test_directory(test_dir: Path, recursive: bool = True) -> bool:
    """Improve test quality across a directory."""
    if not test_dir.exists():
        logger.error(f"Test directory not found: {test_dir}")
        return False

    # Find all test files
    if recursive:
        test_files = list(test_dir.rglob("test_*.py"))
    else:
        test_files = list(test_dir.glob("test_*.py"))

    if not test_files:
        logger.warning(f"No test files found in {test_dir}")
        return True

    logger.info(f"Found {len(test_files)} test files to analyze")

    # Analyze all files
    all_issues = []
    analyzer = TestQualityAnalyzer()

    for test_file in test_files:
        logger.info(f"Analyzing: {test_file.relative_to(test_dir.parent)}")
        issues = analyzer.analyze_test_file(str(test_file))
        all_issues.extend(issues)

    # Generate summary report
    total_files = len(test_files)
    files_with_issues = len(set(issue.file_path for issue in all_issues))

    print("\n" + "=" * 80)
    print("TEST QUALITY ANALYSIS REPORT")
    print("=" * 80)
    print(f"Total test files analyzed: {total_files}")
    print(f"Files with quality issues: {files_with_issues}")
    print(f"Total quality issues found: {len(all_issues)}")
    print(f"Quality score: {((total_files - files_with_issues) / total_files * 100):.1f}%")

    # Categorize issues
    issue_types = {}
    for issue in all_issues:
        issue_type = issue.issue_type
        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

    print("\nIssue Breakdown:")
    for issue_type, count in sorted(issue_types.items()):
        print(f"  {issue_type}: {count}")

    # Show worst files
    file_issue_counts = {}
    for issue in all_issues:
        file_issue_counts[issue.file_path] = file_issue_counts.get(issue.file_path, 0) + 1

    if file_issue_counts:
        print("\nFiles with most issues:")
        for file_path, count in sorted(file_issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {Path(file_path).name}: {count} issues")

    print("\n" + "=" * 80)

    return len(all_issues) == 0


def main():
    """Main entry point for test quality improvement."""
    parser = argparse.ArgumentParser(
        description="Test Quality Improvement Tool - Phase 3 Implementation",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze test quality")
    analyze_parser.add_argument("paths", nargs="+", help="Test files or directories to analyze")
    analyze_parser.add_argument("--recursive", action="store_true", help="Analyze directories recursively")

    # Enhance command
    enhance_parser = subparsers.add_parser("enhance", help="Enhance test assertions")
    enhance_parser.add_argument("test_file", help="Test file to enhance")

    # Coverage command
    coverage_parser = subparsers.add_parser("coverage", help="Analyze coverage gaps")
    coverage_parser.add_argument("source_file", help="Source file to analyze")
    coverage_parser.add_argument("test_file", help="Test file to analyze")

    # Template command
    template_parser = subparsers.add_parser("template", help="Create enhanced test template")
    template_parser.add_argument("source_file", help="Source file to create template for")
    template_parser.add_argument("--output", help="Output path for template")

    # Improve directory command
    improve_parser = subparsers.add_parser("improve", help="Improve test directory")
    improve_parser.add_argument("test_dir", help="Test directory to improve")
    improve_parser.add_argument("--recursive", action="store_true", default=True, help="Analyze recursively")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    success = True

    if args.command == "analyze":
        paths = [Path(p) for p in args.paths]
        for path in paths:
            if path.is_dir():
                test_files = list(path.rglob("test_*.py")) if args.recursive else list(path.glob("test_*.py"))
                success &= analyze_test_quality(test_files)
            else:
                success &= analyze_test_quality([path])

    elif args.command == "enhance":
        success = enhance_test_assertions(Path(args.test_file))

    elif args.command == "coverage":
        success = analyze_coverage_gaps(Path(args.source_file), Path(args.test_file))

    elif args.command == "template":
        output_path = Path(args.output) if args.output else None
        success = create_enhanced_test_template(Path(args.source_file), output_path)

    elif args.command == "improve":
        success = improve_test_directory(Path(args.test_dir), args.recursive)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
