#!/usr/bin/env python3
"""
Plan format compliance CI gate.

Validates plan files against simplified-plan-format-v1 specification.
Intended for CI integration to enforce forward-only plan format compliance.

Usage:
    # Advisory mode (exit 0 regardless of findings)
    python ops_scripts/ci/check_plan_format_compliance.py --advisory --paths plan1.md plan2.md
    
    # Strict mode (exit non-zero on FAIL/ERROR)
    python ops_scripts/ci/check_plan_format_compliance.py --strict --paths plan1.md plan2.md
    
    # With artifact output
    python ops_scripts/ci/check_plan_format_compliance.py --strict --paths plan.md --artifact artifacts/ci/plan_format_compliance.json

Exit codes:
    0 — All checks passed (or advisory mode)
    1 — FAIL or ERROR violations found (strict mode)
    2 — Usage error (file not found, invalid arguments)
    3 — Unclassified WARN found (strict mode only)

Modes:
    --advisory: Report findings but always exit 0
    --strict: Fail on FAIL/ERROR and unclassified WARN

Scopes:
    --paths: One or more explicit file paths to validate
    --artifact: Write JSON receipt to specified path
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple


class Severity(Enum):
    FAIL = "FAIL"
    ERROR = "ERROR"
    WARN = "WARN"
    INFO = "INFO"


@dataclass
class Violation:
    severity: Severity
    rule_id: str
    line_num: int
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity.value,
            "rule_id": self.rule_id,
            "line_num": self.line_num,
            "message": self.message,
        }


class PlanFormatValidator:
    """Validates a plan file against simplified-plan-format-v1."""

    # Canonical enums
    PLAN_STATUSES = {"TODO", "IN_PROGRESS", "DONE", "BLOCKED", "DEFERRED", "WAITING", "RETIRED", "ARCHIVED"}
    WAVE_STATUSES = {"TODO", "IN_PROGRESS", "DONE", "BLOCKED"}
    PHASE_STATUSES = {"TODO", "IN_PROGRESS", "DONE", "BLOCKED"}
    DOD_STATUSES = {"TODO", "IN_PROGRESS", "DONE", "BLOCKED", "DEFERRED"}
    AUTHORIZATION_STATUSES = {"NOT_REQUIRED", "REQUIRED", "GRANTED", "DENIED"}
    COMPLETION_VALUES = {"YES", "NO"}
    FORMAT_VERSION_VALUE = "simplified-plan-format-v1"

    # Regex patterns
    FORMAT_VERSION_RE = re.compile(r'^FORMAT_VERSION:\s*(\S+)')
    PLAN_STATUS_RE = re.compile(r'^PLAN_STATUS:\s*(\S+)')
    CURRENT_WAVE_RE = re.compile(r'^CURRENT_WAVE:\s*(\S+)')
    LAST_COMPLETED_RE = re.compile(r'^LAST_COMPLETED_WAVE:\s*(\S+)')
    LAST_UPDATED_RE = re.compile(r'^LAST_UPDATED:\s*(\d{4}-\d{2}-\d{2})')
    WAVE_ID_RE = re.compile(r'^WAVE_ID:\s*(W\d+)')
    WAVE_STATUS_RE = re.compile(r'^WAVE_STATUS:\s*(\S+)')
    WAVE_COMPLETE_RE = re.compile(r'^WAVE_COMPLETE:\s*(\S+)')
    WAVE_SECTION_RE = re.compile(r'^## Wave \d+')
    AUTHORIZATION_STATUS_RE = re.compile(r'^AUTHORIZATION_STATUS:\s*(\S+)')
    CHECKPOINT_RE = re.compile(r'^CHECKPOINT:\s*(\S+)')
    PHASE_MARKER_RE = re.compile(r'PHASE_STATUS:\s*(\S+)')
    PHASE_COMPLETE_RE = re.compile(r'PHASE_COMPLETE:\s*(\S+)')
    DOD_STATUS_RE = re.compile(r'^DoD-\d+:.+- Status:\s*(\S+)', re.MULTILINE)
    TABLE_START_RE = re.compile(r'^\|[-]+\|')
    EMOJI_RE = re.compile(r'[🔲✅🔄❌⚠️⛔🟢🔵🟡🟣⚪]')
    FENCE_START_RE = re.compile(r'^```')
    FENCE_END_RE = re.compile(r'^```')

    def __init__(self, content: str, filepath: str):
        self.lines = content.split('\n')
        self.filepath = filepath
        self.violations: List[Violation] = []

    def _get_fenced_code_line_ranges(self) -> List[Tuple[int, int]]:
        """Return list of (start, end) line ranges for fenced code blocks."""
        ranges = []
        in_fence = False
        fence_start = 0
        
        for i, line in enumerate(self.lines, 1):
            if self.FENCE_START_RE.match(line):
                if not in_fence:
                    in_fence = True
                    fence_start = i
                else:
                    in_fence = False
                    ranges.append((fence_start, i))
        
        return ranges

    def _is_line_in_fenced_code(self, line_num: int, ranges: List[Tuple[int, int]]) -> bool:
        """Check if a line number is inside any fenced code block."""
        for start, end in ranges:
            if start <= line_num <= end:
                return True
        return False

    def _add(self, severity: Severity, rule_id: str, line_num: int, message: str):
        self.violations.append(Violation(severity, rule_id, line_num, message))

    def _find_marker(self, pattern: re.Pattern) -> Optional[Tuple[int, str]]:
        """Find first match of pattern, return (line_num, value)."""
        for i, line in enumerate(self.lines, 1):
            match = pattern.match(line)
            if match:
                return (i, match.group(1))
        return None

    def _find_all_markers(self, pattern: re.Pattern) -> List[Tuple[int, str]]:
        """Find all matches of pattern, return list of (line_num, value)."""
        results = []
        for i, line in enumerate(self.lines, 1):
            match = pattern.match(line)
            if match:
                results.append((i, match.group(1)))
        return results

    def _validate_required_markers(self, fenced_ranges: List[Tuple[int, int]]):
        """TLM-1 through TLM-5: Required top-level markers."""
        required = [
            (self.FORMAT_VERSION_RE, "FORMAT_VERSION", "TLM-1"),
            (self.PLAN_STATUS_RE, "PLAN_STATUS", "TLM-2"),
            (self.CURRENT_WAVE_RE, "CURRENT_WAVE", "TLM-3"),
            (self.LAST_COMPLETED_RE, "LAST_COMPLETED_WAVE", "TLM-4"),
            (self.LAST_UPDATED_RE, "LAST_UPDATED", "TLM-5"),
        ]
        
        for pattern, name, rule_id in required:
            result = self._find_marker(pattern)
            if not result:
                self._add(Severity.FAIL, rule_id, 0, f"Missing required marker: {name}")

    def _validate_format_version(self, fenced_ranges: List[Tuple[int, int]]):
        """TLM-1b: FORMAT_VERSION value."""
        result = self._find_marker(self.FORMAT_VERSION_RE)
        if result:
            line_num, value = result
            if value != self.FORMAT_VERSION_VALUE:
                self._add(Severity.FAIL, "TLM-1b", line_num,
                         f"Invalid FORMAT_VERSION: '{value}'. Must be: {self.FORMAT_VERSION_VALUE}")

    def _validate_enums(self, fenced_ranges: List[Tuple[int, int]]):
        """ENUM-1 through ENUM-5: Status enum validation."""
        # PLAN_STATUS (top-level, never in fenced block)
        result = self._find_marker(self.PLAN_STATUS_RE)
        if result:
            line_num, value = result
            if value not in self.PLAN_STATUSES:
                self._add(Severity.FAIL, "ENUM-1", line_num,
                         f"Invalid PLAN_STATUS: '{value}'. Must be one of: {', '.join(sorted(self.PLAN_STATUSES))}")
        
        # WAVE_STATUS (skip if in fenced code block)
        for line_num, value in self._find_all_markers(self.WAVE_STATUS_RE):
            if self._is_line_in_fenced_code(line_num, fenced_ranges):
                continue
            if value not in self.WAVE_STATUSES:
                self._add(Severity.FAIL, "ENUM-2", line_num,
                         f"Invalid WAVE_STATUS: '{value}'. Must be one of: {', '.join(sorted(self.WAVE_STATUSES))}")
        
        # WAVE_COMPLETE (skip fenced)
        for line_num, value in self._find_all_markers(self.WAVE_COMPLETE_RE):
            if self._is_line_in_fenced_code(line_num, fenced_ranges):
                continue
            if value not in self.COMPLETION_VALUES:
                self._add(Severity.FAIL, "ENUM-3", line_num,
                         f"Invalid WAVE_COMPLETE: '{value}'. Must be YES or NO")
        
        # PHASE_STATUS inline (skip fenced)
        for i, line in enumerate(self.lines, 1):
            if self._is_line_in_fenced_code(i, fenced_ranges):
                continue
            match = self.PHASE_MARKER_RE.search(line)
            if match:
                value = match.group(1)
                if value not in self.PHASE_STATUSES:
                    self._add(Severity.FAIL, "ENUM-4", i,
                             f"Invalid PHASE_STATUS: '{value}'. Must be one of: {', '.join(sorted(self.PHASE_STATUSES))}")
        
        # AUTHORIZATION_STATUS (skip fenced)
        for line_num, value in self._find_all_markers(self.AUTHORIZATION_STATUS_RE):
            if self._is_line_in_fenced_code(line_num, fenced_ranges):
                continue
            if value not in self.AUTHORIZATION_STATUSES:
                self._add(Severity.FAIL, "ENUM-5", line_num,
                         f"Invalid AUTHORIZATION_STATUS: '{value}'. Must be one of: {', '.join(sorted(self.AUTHORIZATION_STATUSES))}")

    def _validate_emoji_usage(self, fenced_ranges: List[Tuple[int, int]]):
        """EMOJI-1 through EMOJI-7: Emoji prohibition in canonical markers."""
        status_patterns = [
            (self.PLAN_STATUS_RE, "PLAN_STATUS", "EMOJI-1"),
            (self.WAVE_STATUS_RE, "WAVE_STATUS", "EMOJI-2"),
            (self.WAVE_COMPLETE_RE, "WAVE_COMPLETE", "EMOJI-4"),
            (self.AUTHORIZATION_STATUS_RE, "AUTHORIZATION_STATUS", "EMOJI-6"),
        ]
        
        for pattern, name, rule_id in status_patterns:
            for line_num, value in self._find_all_markers(pattern):
                if self._is_line_in_fenced_code(line_num, fenced_ranges):
                    continue
                if self.EMOJI_RE.search(value):
                    self._add(Severity.FAIL, rule_id, line_num,
                             f"Emojis not allowed in {name}: '{value}'")
        
        # Check phase status inline (skip fenced)
        for i, line in enumerate(self.lines, 1):
            if self._is_line_in_fenced_code(i, fenced_ranges):
                continue
            if "PHASE_STATUS:" in line:
                match = self.PHASE_MARKER_RE.search(line)
                if match and self.EMOJI_RE.search(match.group(1)):
                    self._add(Severity.FAIL, "EMOJI-3", i,
                             f"Emojis not allowed in PHASE_STATUS: '{match.group(1)}'")
            
            if "PHASE_COMPLETE:" in line:
                match = self.PHASE_COMPLETE_RE.search(line)
                if match and self.EMOJI_RE.search(match.group(1)):
                    self._add(Severity.FAIL, "EMOJI-5", i,
                             f"Emojis not allowed in PHASE_COMPLETE: '{match.group(1)}'")
        
        # Prose emoji check (WARN only, skip fenced)
        for i, line in enumerate(self.lines, 1):
            if self._is_line_in_fenced_code(i, fenced_ranges):
                continue
            if self.EMOJI_RE.search(line):
                # Check if it's just a table decoration or actual status
                if '|' in line and any(s in line for s in ["TODO", "IN_PROGRESS", "DONE", "BLOCKED"]):
                    continue  # Probably a reference table
                self._add(Severity.WARN, "EMOJI-7", i, "Emojis detected in prose (allowed, but prefer ASCII in new plans)")

    def _validate_wave_structure(self, fenced_ranges: List[Tuple[int, int]]):
        """COMP-1 through COMP-4: Wave section completeness."""
        # Find wave sections (skip fenced code blocks)
        wave_sections = []
        current_wave_start = None
        
        for i, line in enumerate(self.lines, 1):
            if self._is_line_in_fenced_code(i, fenced_ranges):
                continue
            if self.WAVE_SECTION_RE.match(line):
                if current_wave_start:
                    wave_sections.append((current_wave_start, i - 1))
                current_wave_start = i
        
        if current_wave_start:
            wave_sections.append((current_wave_start, len(self.lines)))

        # Validate each wave section
        for start, end in wave_sections:
            wave_lines = self.lines[start-1:end]
            
            # Check for WAVE_STATUS (skip fenced)
            wave_status_line = None
            for j, line in enumerate(wave_lines, start):
                if self._is_line_in_fenced_code(j, fenced_ranges):
                    continue
                if self.WAVE_STATUS_RE.match(line):
                    wave_status_line = j
                    break
            
            if not wave_status_line:
                self._add(Severity.FAIL, "COMP-3", start, "Missing WAVE_STATUS for declared wave")
                continue
            
            # Check for WAVE_COMPLETE (skip fenced)
            wave_complete_line = None
            for j, line in enumerate(wave_lines, start):
                if self._is_line_in_fenced_code(j, fenced_ranges):
                    continue
                if self.WAVE_COMPLETE_RE.match(line):
                    wave_complete_line = j
                    break
            
            if not wave_complete_line:
                self._add(Severity.FAIL, "COMP-4", start, "Missing WAVE_COMPLETE for declared wave")
                continue
            
            # Find first table in this wave section
            first_table = None
            for j, line in enumerate(wave_lines, start):
                if self.TABLE_START_RE.match(line):
                    first_table = j
                    break
            
            if first_table:
                # Check WAVE_STATUS comes before first table
                if wave_status_line > first_table:
                    self._add(Severity.FAIL, "TABLE-2", first_table,
                             "WAVE_STATUS must appear before first table in wave section")
                
                # Check WAVE_COMPLETE comes before first table
                if wave_complete_line > first_table:
                    self._add(Severity.FAIL, "TABLE-3", first_table,
                             "WAVE_COMPLETE must appear before first table in wave section")

    def validate(self) -> List[Violation]:
        """Run all validation rules."""
        self.violations = []
        fenced_ranges = self._get_fenced_code_line_ranges()
        
        self._validate_required_markers(fenced_ranges)
        self._validate_format_version(fenced_ranges)
        self._validate_enums(fenced_ranges)
        self._validate_emoji_usage(fenced_ranges)
        self._validate_wave_structure(fenced_ranges)
        
        return self.violations


def validate_file(filepath: str) -> Tuple[List[Violation], bool]:
    """Validate a single file. Returns (violations, success)."""
    path = Path(filepath)
    if not path.exists():
        return [Violation(Severity.ERROR, "FILE-NOT-FOUND", 0, f"File not found: {filepath}")], False
    
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [Violation(Severity.ERROR, "READ-ERROR", 0, f"Cannot read {filepath}: {e}")], False
    
    validator = PlanFormatValidator(content, filepath)
    violations = validator.validate()
    
    return violations, True


def has_unclassified_warn(violations: List[Violation]) -> bool:
    """Check if any WARN is not cosmetic (EMOJI-7)."""
    for v in violations:
        if v.severity == Severity.WARN and v.rule_id != "EMOJI-7":
            return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Plan format compliance CI gate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --advisory --paths plan.md
  %(prog)s --strict --paths plan1.md plan2.md --artifact out.json
        """
    )
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--advisory", action="store_true",
                          help="Report findings but always exit 0")
    mode_group.add_argument("--strict", action="store_true",
                          help="Fail on FAIL/ERROR and unclassified WARN")
    
    parser.add_argument("--paths", nargs="+", required=True,
                       help="One or more plan file paths to validate")
    parser.add_argument("--artifact", type=str,
                       help="Write JSON receipt to specified path")
    
    args = parser.parse_args()
    
    all_results = []
    total_fail = 0
    total_error = 0
    total_warn = 0
    total_unclassified_warn = 0
    
    for filepath in args.paths:
        violations, success = validate_file(filepath)
        
        if not success and any(v.rule_id == "FILE-NOT-FOUND" for v in violations):
            print(f"[ERROR] {filepath}: File not found", file=sys.stderr)
            sys.exit(2)
        
        file_fail = sum(1 for v in violations if v.severity == Severity.FAIL)
        file_error = sum(1 for v in violations if v.severity == Severity.ERROR)
        file_warn = sum(1 for v in violations if v.severity == Severity.WARN)
        file_unclassified = sum(1 for v in violations if v.severity == Severity.WARN and v.rule_id != "EMOJI-7")
        
        total_fail += file_fail
        total_error += file_error
        total_warn += file_warn
        total_unclassified_warn += file_unclassified
        
        status = "PASS" if file_fail == 0 and file_error == 0 else "FAIL"
        print(f"[{status}] {filepath}: {file_fail} FAIL, {file_error} ERROR, {file_warn} WARN")
        
        for v in violations:
            print(f"  [{v.severity.value}] {filepath}:{v.line_num} — {v.rule_id}: {v.message}")
        
        all_results.append({
            "filepath": filepath,
            "status": status,
            "violations": [v.to_dict() for v in violations],
            "summary": {
                "fail": file_fail,
                "error": file_error,
                "warn": file_warn,
            }
        })
    
    # Summary
    print(f"\n{'='*60}")
    print(f"TOTAL: {total_fail} FAIL, {total_error} ERROR, {total_warn} WARN ({total_unclassified_warn} unclassified)")
    
    # Write artifact if requested
    if args.artifact:
        artifact_path = Path(args.artifact)
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        
        receipt = {
            "mode": "advisory" if args.advisory else "strict",
            "total_files": len(args.paths),
            "total_fail": total_fail,
            "total_error": total_error,
            "total_warn": total_warn,
            "total_unclassified_warn": total_unclassified_warn,
            "results": all_results,
        }
        
        artifact_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        print(f"Artifact written: {args.artifact}")
    
    # Exit code
    if args.advisory:
        sys.exit(0)
    elif args.strict:
        if total_fail > 0 or total_error > 0:
            sys.exit(1)
        if total_unclassified_warn > 0:
            sys.exit(3)
        sys.exit(0)


if __name__ == "__main__":
    main()
