#!/usr/bin/env python3
"""
HITL Format Compliance Validator

Validates that HITL ask_user_question calls in plan files comply with
the confidence-gated §HITL-10 format: packet header, confidence score
in option labels, and decision_thesis field in option descriptions.

DEPRECATED CHECKS REMOVED: **Pros**/**Cons** and bare ⭐ star markers
are no longer the required format (see §HITL-10 in hitl-enforcement.md).

Usage:
    python ops_scripts/ci/validate_hitl_format.py --path .windsurf/plans
    python ops_scripts/ci/validate_hitl_format.py --path docs/reports/plans
    python ops_scripts/ci/validate_hitl_format.py --all
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


# Packet header required fields (§HITL-0 format)
_PACKET_HEADER_FIELDS = [
    "Recommended:",
    "Why it wins:",
    "What you are optimizing for:",
    "What is being traded off:",
    "Candidates evaluated:",
]

# Confidence score pattern in option labels: [0.NN HIGH] or [0.NN MEDIUM]
# LOW band is suppressed and should never appear in surfaced options
_CONFIDENCE_LABEL_RE = re.compile(r"\[0\.\d{2}\s+(HIGH|MEDIUM)\]")

# Star marker for recommended option
_STAR_MARKER_RE = re.compile(r'"⭐\s+[^"]+\[0\.\d{2}\s+HIGH\]"')

# Banned LOW confidence band (should be suppressed, not surfaced)
_LOW_CONFIDENCE_RE = re.compile(r"\[0\.\d{2}\s+LOW\]")

# §HITL-10 required field in option description
_DECISION_THESIS_RE = re.compile(r"decision_thesis:")

# Banned patterns from old format
_BANNED_PATTERNS = [
    re.compile(r"^\*\*Pros\*\*:", re.MULTILINE),
    re.compile(r"^\*\*Cons\*\*:", re.MULTILINE),
    re.compile(r"Pros:\s"),
    re.compile(r"Cons:\s"),
]


def validate_file(file_path: Path) -> List[Tuple[int, str, str]]:
    """
    Validate a single markdown file for HITL §HITL-10 format compliance.

    Checks:
    - ask_user_question blocks have packet header with required fields
    - Option labels contain confidence score band [0.NN HIGH|MEDIUM]
    - Option descriptions contain decision_thesis:
    - Banned old-format patterns (**Pros**/**Cons**) are absent

    Returns:
        List of (line_number, issue_type, message) tuples for violations
    """
    violations = []
    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Detect ask_user_question blocks
    in_hitl_block = False
    block_start = 0
    block_lines: List[str] = []

    for i, line in enumerate(lines, start=1):
        if "ask_user_question" in line:
            in_hitl_block = True
            block_start = i
            block_lines = [line]
            continue
        if in_hitl_block:
            block_lines.append(line)
            # End of block at closing paren on its own line
            if line.strip() in (")", ")") or (line.strip().startswith(")") and len(block_lines) > 3):
                block_text = "\n".join(block_lines)

                # Check packet header fields
                for field in _PACKET_HEADER_FIELDS:
                    if field not in block_text:
                        violations.append(
                            (
                                block_start,
                                "MISSING_PACKET_HEADER",
                                f"ask_user_question block missing packet header field: {field!r}",
                            )
                        )

                # Check confidence score in at least one label
                if "label:" in block_text and not _CONFIDENCE_LABEL_RE.search(block_text):
                    violations.append(
                        (
                            block_start,
                            "MISSING_CONFIDENCE_SCORE",
                            "ask_user_question block has option labels but none contain confidence score [0.NN HIGH|MEDIUM]",
                        )
                    )

                # Check decision_thesis in description
                if "description:" in block_text and not _DECISION_THESIS_RE.search(block_text):
                    violations.append(
                        (
                            block_start,
                            "MISSING_DECISION_THESIS",
                            "ask_user_question block has option descriptions but none contain decision_thesis:",
                        )
                    )

                # Check for LOW confidence band (should be suppressed, not surfaced)
                low_conf_matches = _LOW_CONFIDENCE_RE.findall(block_text)
                if low_conf_matches:
                    violations.append(
                        (
                            block_start,
                            "LOW_CONFIDENCE_SURFACED",
                            f"LOW confidence band options should be suppressed (below 0.72 threshold), not surfaced: {low_conf_matches}",
                        )
                    )

                # Check for ⭐ star marker on highest-confidence option
                # The recommended option (highest confidence) MUST have ⭐ prefix in label
                if "label:" in block_text and _CONFIDENCE_LABEL_RE.search(block_text):
                    # Extract all confidence scores to find the highest
                    scores = []
                    for match in _CONFIDENCE_LABEL_RE.finditer(block_text):
                        score_str = match.group(0).split("[")[1].split()[0]
                        try:
                            score = float(score_str)
                            scores.append((score, match.start()))
                        except ValueError:
                            pass

                    if scores:
                        max_score = max(scores, key=lambda x: x[0])[0]
                        # If highest score >= 0.85 (HIGH band), check for star marker
                        if max_score >= 0.85:
                            # Look for star marker in the label text near the highest score
                            has_star = _STAR_MARKER_RE.search(block_text)
                            if not has_star:
                                violations.append(
                                    (
                                        block_start,
                                        "MISSING_STAR_MARKER",
                                        f"Recommended option (highest confidence {max_score}) MUST have ⭐ prefix in label: e.g., label: \"⭐ Option Title [{max_score} HIGH]\"",
                                    )
                                )

                in_hitl_block = False
                block_lines = []

    # Check banned old-format patterns anywhere in file
    for pattern in _BANNED_PATTERNS:
        for match in pattern.finditer(content):
            line_num = content[: match.start()].count("\n") + 1
            violations.append(
                (
                    line_num,
                    "BANNED_OLD_FORMAT",
                    f"Banned old-format pattern found: {match.group().strip()!r} — use §HITL-10 decision_thesis shape instead",
                )
            )

    return violations


def main():
    parser = argparse.ArgumentParser(description="Validate HITL format compliance")
    parser.add_argument("--path", type=str, help="Path to scan (file or directory)")
    parser.add_argument("--all", action="store_true", help="Scan both .windsurf/plans and docs/reports/plans")
    args = parser.parse_args()

    paths_to_scan = []
    if args.all:
        paths_to_scan.extend(
            [
                Path(".windsurf/plans"),
                Path("docs/reports/plans"),
            ]
        )
    elif args.path:
        paths_to_scan.append(Path(args.path))
    else:
        parser.error("Must specify --path or --all")

    all_violations = []
    files_scanned = 0

    for path in paths_to_scan:
        if path.is_file() and path.suffix == ".md":
            files = [path]
        elif path.is_dir():
            files = list(path.glob("*.md"))
        else:
            print(f"Warning: {path} is not a valid file or directory", file=sys.stderr)
            continue

        for file_path in files:
            files_scanned += 1
            violations = validate_file(file_path)
            if violations:
                all_violations.append((file_path, violations))

    # Report results
    print("\nHITL Format Validation Report")
    print("=" * 50)
    print(f"Files scanned: {files_scanned}")
    print(f"Files with violations: {len(all_violations)}")
    print(f"Total violations: {sum(len(v) for _, v in all_violations)}")

    if all_violations:
        print("\n" + "=" * 50)
        print("VIOLATIONS:")
        print("=" * 50)
        for file_path, violations in all_violations:
            print(f"\n{file_path}:")
            for line_num, issue_type, message in violations:
                if line_num > 0:
                    print(f"  Line {line_num} [{issue_type}]: {message}")
                else:
                    print(f"  [{issue_type}]: {message}")
        print("\n" + "=" * 50)
        print("FAILED: HITL format violations found")
        print("=" * 50)
        sys.exit(1)
    else:
        print("\n" + "=" * 50)
        print("PASSED: All HITL decisions comply with format requirements")
        print("=" * 50)
        sys.exit(0)


if __name__ == "__main__":
    main()
