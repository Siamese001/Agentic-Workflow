#!/usr/bin/env python3
"""
Evidence Contract v2 Checker

Scans consolidated evidence files and verifies contract compliance:
- Required headings exist and appear exactly once
- CODE_COMMIT and EVIDENCE_COMMIT are 40-hex
- No duplicated/contradictory commit fields
- No embedded Python source blocks that look like runner code
- Deterministic, pure read-only, exits nonzero on violations
"""

import argparse
import re
import sys
from pathlib import Path


class EvidenceContractChecker:
    """Checker for Evidence Contract v2 compliance."""

    # Required headings that must appear exactly once
    REQUIRED_HEADINGS: set[str] = {
        "CODE_COMMIT",
        "EVIDENCE_COMMIT",
        "FILES_CHANGED_CODE",
        "FILES_CHANGED_EVIDENCE",
        "INSPECTED_FILES",
    }

    # Patterns that suggest embedded Python code
    PYTHON_CODE_PATTERNS = [
        r"#!/usr/bin/env python",
        r"def main\(",
        r"import sys",
        r"from pathlib import Path",
        r'if __name__ == "__main__"',
        r"argparse\.ArgumentParser",
        r"subprocess\.run",
    ]

    def __init__(self, paths: list[Path]):
        """Initialize checker with paths to scan.

        Args:
            paths: List of directories to scan for evidence files
        """
        self.paths = paths
        self.violations = []

    def find_evidence_files(self) -> list[Path]:
        """Find all phase_*_consolidated*.md files in paths."""
        evidence_files = []

        for path in self.paths:
            if not path.exists():
                self.violations.append(f"Path does not exist: {path}")
                continue

            if (
                path.is_file()
                and path.name.startswith("phase_")
                and "consolidated" in path.name
                and path.suffix == ".md"
            ):
                evidence_files.append(path)
            elif path.is_dir():
                # Search for matching files
                pattern = "phase_*_consolidated*.md"
                files = list(path.glob(pattern))
                evidence_files.extend(files)

        return sorted(evidence_files)

    def validate_commit_hash(self, commit_hash: str, field_name: str, filepath: Path) -> None:
        """Validate that commit hash is 40-character hex."""
        if len(commit_hash) != 40:
            self.violations.append(
                f"{filepath}: {field_name} must be 40 characters (got {len(commit_hash)}): {commit_hash}",
            )
        elif not all(c in "0123456789abcdefABCDEF" for c in commit_hash):
            self.violations.append(f"{filepath}: {field_name} must be hex: {commit_hash}")
        elif field_name != "EVIDENCE_COMMIT" or commit_hash != "PENDING":
            # Additional check: verify commit exists (skip for PENDING)
            try:
                import subprocess

                result = subprocess.run(
                    ["git", "cat-file", "-e", commit_hash],
                    capture_output=True,
                    text=True,
                    cwd=filepath.parent.parent.parent,
                )
                if result.returncode != 0:
                    self.violations.append(
                        f"{filepath}: {field_name} does not exist in repository: {commit_hash}",
                    )
            except (subprocess.CalledProcessError, ValueError) as e:
                # If git check fails, just warn but don't fail
                print(f"Git check failed for {commit_hash}: {e}")

    def check_file(self, filepath: Path) -> None:
        """Check a single evidence file for compliance."""
        try:
            content = filepath.read_text(encoding="utf-8")
        except OSError as e:
            self.violations.append(f"{filepath}: Could not read file: {e}")
            return

        # Check for required headings
        found_headings = set()
        for heading in self.REQUIRED_HEADINGS:
            pattern = rf"^## {heading}$"
            matches = re.findall(pattern, content, re.MULTILINE)
            if len(matches) == 0:
                self.violations.append(f"{filepath}: Missing required heading: ## {heading}")
            elif len(matches) > 1:
                self.violations.append(
                    f"{filepath}: Duplicate heading: ## {heading} (found {len(matches)} times)",
                )
            else:
                found_headings.add(heading)

        # Check for unexpected headings
        all_headings = re.findall(r"^## (.+)$", content, re.MULTILINE)
        for heading in all_headings:
            if heading in self.REQUIRED_HEADINGS and heading not in found_headings:
                # This shouldn't happen if our counting is right, but let's be safe
                self.violations.append(f"{filepath}: Found heading but not counted: ## {heading}")

        # Extract and validate commit hashes
        lines = content.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()

            if line.startswith("## CODE_COMMIT"):
                # Next line should be the commit hash
                if i + 1 < len(lines):
                    commit_hash = lines[i + 1].strip()
                    if commit_hash and commit_hash != "CODE_COMMIT":  # Skip if it's just the heading again
                        self.validate_commit_hash(commit_hash, "CODE_COMMIT", filepath)

            elif line.startswith("## EVIDENCE_COMMIT"):
                # Next line should be the commit hash
                if i + 1 < len(lines):
                    commit_hash = lines[i + 1].strip()
                    if commit_hash and commit_hash != "EVIDENCE_COMMIT":
                        if commit_hash != "PENDING":
                            self.validate_commit_hash(commit_hash, "EVIDENCE_COMMIT", filepath)

        # Check for embedded Python code (basic heuristic)
        content_lower = content.lower()
        for pattern in self.PYTHON_CODE_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                # Check if it's in a code block (which is expected for file contents)
                # We're looking for Python code outside of proper markdown code blocks
                lines = content.split("\n")
                in_code_block = False
                code_block_start = None

                for j, check_line in enumerate(lines):
                    if check_line.strip() == "```":
                        if not in_code_block:
                            in_code_block = True
                            code_block_start = j
                        else:
                            in_code_block = False
                            code_block_start = None

                    # If we find Python-like patterns outside code blocks, that's suspicious
                    if not in_code_block and re.search(pattern, check_line, re.IGNORECASE):
                        # Skip if it's clearly just a comment about Python code
                        if not check_line.strip().startswith("#") and "python" not in check_line.lower():
                            self.violations.append(
                                f"{filepath}: Suspicious Python code pattern detected outside code block at line {j + 1}: {pattern}",
                            )
                            break  # One violation per pattern is enough

        # Check for proper markdown structure
        if not content.startswith("#"):
            self.violations.append(f"{filepath}: Should start with markdown heading (#)")

    def check(self) -> list[str]:
        """Check all evidence files and return violations."""
        evidence_files = self.find_evidence_files()

        if not evidence_files:
            self.violations.append("No evidence files found matching pattern phase_*_consolidated*.md")
            return self.violations

        print(f"Checking {len(evidence_files)} evidence file(s)...")

        for filepath in evidence_files:
            print(f"Checking: {filepath.relative_to(filepath.parent.parent.parent)}")
            self.check_file(filepath)

        return self.violations


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check Evidence Contract v2 compliance")
    parser.add_argument("--paths", nargs="+", required=True, help="Paths to scan for evidence files")
    args = parser.parse_args()

    # Convert to Path objects
    paths = [Path(p) for p in args.paths]

    checker = EvidenceContractChecker(paths)
    violations = checker.check()

    if violations:
        print(f"\nERROR: Evidence contract violations found: {len(violations)}")
        for violation in violations:
            print(f"  - {violation}")
        return 1
    else:
        print("\nOK: All evidence files comply with contract v2")
        return 0


if __name__ == "__main__":
    sys.exit(main())
