#!/usr/bin/env python3
"""
Forward-only plan format validator.

Validates a single provided plan file against the simplified-plan-format-v1 specification.
Does NOT scan historical plans by default.
Does NOT mutate files.
Does NOT register in CI during W1.

Usage:
    python tools/analysis/check_plan_format_forward.py <plan_file.md>

Exit codes:
    0 — Valid (or only WARN/INFO)
    1 — FAIL or ERROR violations found
    2 — Usage error (file not found, etc.)
"""

import argparse
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple


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


class PlanFormatValidator:
    """Validates a single plan file against simplified-plan-format-v1."""

    # Canonical enums
    PLAN_STATUSES = {"TODO", "IN_PROGRESS", "DONE", "BLOCKED", "DEFERRED", "WAITING", "RETIRED", "ARCHIVED"}
    WAVE_STATUSES = {"TODO", "IN_PROGRESS", "DONE", "BLOCKED"}
    PHASE_STATUSES = {"TODO", "IN_PROGRESS", "DONE", "BLOCKED"}
    DOD_STATUSES = {"TODO", "IN_PROGRESS", "DONE", "BLOCKED", "DEFERRED"}
    AUTHORIZATION_STATUSES = {"NOT_REQUIRED", "REQUIRED", "GRANTED", "DENIED"}
    COMPLETION_VALUES = {"YES", "NO"}

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
    DOD_STATUS_RE = re.compile(r'- Status:\s*(\S+)')
    TABLE_START_RE = re.compile(r'^\|[-]+\|')
    EMOJI_RE = re.compile(r'[🔲✅🔄❌⚠️⛔🟢🔵🟡🟣⚪]')
    FENCE_START_RE = re.compile(r'^```')
    FENCE_END_RE = re.compile(r'^```')

    def __init__(self, content: str, filepath: str):
        self.lines = content.split('\n')
        self.filepath = filepath
        self.violations: List[Violation] = []

    def validate(self) -> List[Violation]:
        """Run all validation rules."""
        self._validate_top_level_markers()
        self._validate_enums()
        self._validate_emoji_usage()
        self._validate_wave_structure()
        self._validate_consistency()
        self._validate_authorization()
        return self.violations

    def _add(self, severity: Severity, rule_id: str, line_num: int, message: str):
        self.violations.append(Violation(severity, rule_id, line_num, message))

    def _get_fenced_code_line_ranges(self) -> List[Tuple[int, int]]:
        """Find all line ranges inside fenced code blocks."""
        ranges = []
        in_fence = False
        fence_start = 0
        
        for i, line in enumerate(self.lines, 1):
            if self.FENCE_START_RE.match(line):
                if not in_fence:
                    in_fence = True
                    fence_start = i
                else:
                    # End of fence
                    ranges.append((fence_start, i))
                    in_fence = False
        
        # Handle unclosed fence (treat as ending at EOF)
        if in_fence:
            ranges.append((fence_start, len(self.lines)))
        
        return ranges
    
    def _is_line_in_fenced_code(self, line_num: int, fenced_ranges: List[Tuple[int, int]]) -> bool:
        """Check if a line number is inside any fenced code block."""
        for start, end in fenced_ranges:
            if start < line_num <= end:  # Line after ``` start to ``` end
                return True
        return False

    def _find_marker(self, pattern: re.Pattern) -> Optional[Tuple[int, str]]:
        """Find first occurrence of a marker pattern."""
        for i, line in enumerate(self.lines, 1):
            match = pattern.match(line)
            if match:
                return (i, match.group(1))
        return None

    def _find_all_markers(self, pattern: re.Pattern) -> List[Tuple[int, str]]:
        """Find all occurrences of a marker pattern."""
        results = []
        for i, line in enumerate(self.lines, 1):
            match = pattern.match(line)
            if match:
                results.append((i, match.group(1)))
            # Also search inline for phase/dod markers
            match = pattern.search(line)
            if match and (i, match.group(1)) not in results:
                results.append((i, match.group(1)))
        return results

    def _find_first_table(self) -> Optional[int]:
        """Find line number of first table."""
        for i, line in enumerate(self.lines, 1):
            if self.TABLE_START_RE.match(line):
                return i
        return None

    def _validate_top_level_markers(self):
        """Category 1: Top-Level Marker Requirements."""
        markers = [
            (self.FORMAT_VERSION_RE, "FORMAT_VERSION", "TLM-1"),
            (self.PLAN_STATUS_RE, "PLAN_STATUS", "TLM-2"),
            (self.CURRENT_WAVE_RE, "CURRENT_WAVE", "TLM-3"),
            (self.LAST_COMPLETED_RE, "LAST_COMPLETED_WAVE", "TLM-4"),
            (self.LAST_UPDATED_RE, "LAST_UPDATED", "TLM-5"),
        ]

        for pattern, name, rule_id in markers:
            result = self._find_marker(pattern)
            if result is None:
                self._add(Severity.FAIL, rule_id, 0, f"Missing required marker: {name}")

    def _validate_enums(self):
        """Category 2: Enum Validity."""
        fenced_ranges = self._get_fenced_code_line_ranges()
        
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
                continue  # Skip fenced code blocks
            if value not in self.WAVE_STATUSES:
                self._add(Severity.FAIL, "ENUM-2", line_num,
                         f"Invalid WAVE_STATUS: '{value}'. Must be one of: {', '.join(sorted(self.WAVE_STATUSES))}")

        # PHASE_STATUS (skip if in fenced code block)
        for line_num, value in self._find_all_markers(self.PHASE_MARKER_RE):
            if self._is_line_in_fenced_code(line_num, fenced_ranges):
                continue  # Skip fenced code blocks
            if value not in self.PHASE_STATUSES:
                self._add(Severity.FAIL, "ENUM-3", line_num,
                         f"Invalid PHASE_STATUS: '{value}'. Must be one of: {', '.join(sorted(self.PHASE_STATUSES))}")

        # DOD_STATUS (skip if in fenced code block)
        for line_num, value in self._find_all_markers(self.DOD_STATUS_RE):
            if self._is_line_in_fenced_code(line_num, fenced_ranges):
                continue  # Skip fenced code blocks
            if value not in self.DOD_STATUSES:
                self._add(Severity.FAIL, "ENUM-4", line_num,
                         f"Invalid DOD_STATUS: '{value}'. Must be one of: {', '.join(sorted(self.DOD_STATUSES))}")

        # AUTHORIZATION_STATUS (skip if in fenced code block)
        for line_num, value in self._find_all_markers(self.AUTHORIZATION_STATUS_RE):
            if self._is_line_in_fenced_code(line_num, fenced_ranges):
                continue  # Skip fenced code blocks
            if value not in self.AUTHORIZATION_STATUSES:
                self._add(Severity.FAIL, "AUTH-1", line_num,
                         f"Invalid AUTHORIZATION_STATUS: '{value}'. Must be one of: {', '.join(sorted(self.AUTHORIZATION_STATUSES))}")

    def _validate_emoji_usage(self):
        """Category 3: Emoji Prohibition in canonical status fields."""
        fenced_ranges = self._get_fenced_code_line_ranges()
        
        status_patterns = [
            (self.PLAN_STATUS_RE, "PLAN_STATUS", "EMOJI-1"),
            (self.WAVE_STATUS_RE, "WAVE_STATUS", "EMOJI-2"),
        ]

        for pattern, name, rule_id in status_patterns:
            result = self._find_marker(pattern)
            if result:
                line_num, value = result
                if self.EMOJI_RE.search(value):
                    self._add(Severity.FAIL, rule_id, line_num,
                             f"Emojis not allowed in {name}: '{value}'")

        # Check phase status inline (skip fenced code blocks)
        for i, line in enumerate(self.lines, 1):
            if self._is_line_in_fenced_code(i, fenced_ranges):
                continue  # Skip fenced code blocks
            if "PHASE_STATUS:" in line:
                match = self.PHASE_MARKER_RE.search(line)
                if match and self.EMOJI_RE.search(match.group(1)):
                    self._add(Severity.FAIL, "EMOJI-3", i,
                             f"Emojis not allowed in PHASE_STATUS: '{match.group(1)}'")

        # Check DOD status (skip fenced code blocks)
        for i, line in enumerate(self.lines, 1):
            if self._is_line_in_fenced_code(i, fenced_ranges):
                continue  # Skip fenced code blocks
            if self.DOD_STATUS_RE.search(line) and self.EMOJI_RE.search(line):
                match = self.DOD_STATUS_RE.search(line)
                if match and self.EMOJI_RE.search(match.group(1)):
                    self._add(Severity.FAIL, "EMOJI-4", i,
                             f"Emojis not allowed in DOD_STATUS: '{match.group(1)}'")

        # Warn on emojis in prose (allowed but flagged)
        for i, line in enumerate(self.lines, 1):
            # Skip marker lines we already checked
            if any(marker in line for marker in ["PLAN_STATUS:", "WAVE_STATUS:", "PHASE_STATUS:"]):
                continue
            if self.EMOJI_RE.search(line):
                # Check if it's just a table decoration or actual status
                if '|' in line and any(s in line for s in ["TODO", "IN_PROGRESS", "DONE", "BLOCKED"]):
                    continue  # Probably a reference table
                self._add(Severity.WARN, "EMOJI-7", i, "Emojis detected in prose (allowed, but prefer ASCII in new plans)")

    def _validate_wave_structure(self):
        """Category 4: Table Containment and Category 7: Completeness."""
        fenced_ranges = self._get_fenced_code_line_ranges()
        
        # Find wave sections (skip fenced code blocks)
        wave_sections = []
        current_wave_start = None
        
        for i, line in enumerate(self.lines, 1):
            if self._is_line_in_fenced_code(i, fenced_ranges):
                continue  # Skip fenced code blocks
            if self.WAVE_SECTION_RE.match(line):
                if current_wave_start:
                    wave_sections.append((current_wave_start, i - 1))
                current_wave_start = i
        
        if current_wave_start:
            wave_sections.append((current_wave_start, len(self.lines)))

        # Validate each wave section
        for start, end in wave_sections:
            wave_lines = self.lines[start-1:end]
            
            # Check for WAVE_STATUS (skip fenced code blocks)
            wave_status_line = None
            for j, line in enumerate(wave_lines, start):
                if self._is_line_in_fenced_code(j, fenced_ranges):
                    continue  # Skip fenced code blocks
                if self.WAVE_STATUS_RE.match(line):
                    wave_status_line = j
                    break
            
            if not wave_status_line:
                self._add(Severity.FAIL, "COMP-3", start, "Missing WAVE_STATUS for declared wave")
                continue
            
            # Check for WAVE_COMPLETE (skip fenced code blocks)
            wave_complete_line = None
            for j, line in enumerate(wave_lines, start):
                if self._is_line_in_fenced_code(j, fenced_ranges):
                    continue  # Skip fenced code blocks
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

        # Check for status only in table cells (heuristic: status in table row without marker)
        in_table = False
        for i, line in enumerate(self.lines, 1):
            if self.TABLE_START_RE.match(line):
                in_table = True
                continue
            if in_table and not line.startswith('|'):
                in_table = False
            
            if in_table and '|' in line:
                # Check for emoji status in table cells
                cells = [c.strip() for c in line.split('|')[1:-1]]
                for cell in cells:
                    if self.EMOJI_RE.search(cell) and any(s in cell for s in ['TODO', 'DONE', 'IN_PROGRESS', 'BLOCKED']):
                        # Skip if this is a header or separator
                        if cell.replace('-', '').replace(':', '').strip() == '':
                            continue
                        self._add(Severity.FAIL, "TABLE-1", i,
                                 f"Status stored only in table cell: '{cell[:50]}...'")

    def _validate_consistency(self):
        """Category 5: Consistency Requirements."""
        # Get plan status
        plan_status_result = self._find_marker(self.PLAN_STATUS_RE)
        if not plan_status_result:
            return
        
        plan_status = plan_status_result[1]
        
        # Get all DoD statuses
        dod_statuses = self._find_all_markers(self.DOD_STATUS_RE)
        
        if plan_status == "DONE":
            # Check all DoD are DONE or DEFERRED
            for line_num, value in dod_statuses:
                if value not in {"DONE", "DEFERRED"}:
                    self._add(Severity.ERROR, "CONS-2", line_num,
                             f"PLAN_STATUS=DONE but DoD item has Status: {value}")
        
        # Check wave/phase consistency
        wave_completes = self._find_all_markers(self.WAVE_COMPLETE_RE)
        phase_completes = self._find_all_markers(self.PHASE_COMPLETE_RE)
        
        for wave_line, wave_complete in wave_completes:
            if wave_complete == "YES":
                # Check all phases in this wave are complete
                # This is a simplified check - full implementation would parse wave boundaries
                pass  # Complex logic deferred to full implementation

    def _validate_authorization(self):
        """Category 7: Authorization Status validation."""
        # Find wave sections and their authorization status
        wave_sections = []
        current_wave_start = None
        current_wave_auth = None
        current_wave_status = None
        current_wave_complete = None
        
        for i, line in enumerate(self.lines, 1):
            if line.startswith("## Wave "):
                if current_wave_start:
                    wave_sections.append((current_wave_start, i - 1, current_wave_auth, current_wave_status, current_wave_complete))
                current_wave_start = i
                current_wave_auth = None
                current_wave_status = None
                current_wave_complete = None
            
            auth_match = self.AUTHORIZATION_STATUS_RE.match(line)
            if auth_match:
                current_wave_auth = (i, auth_match.group(1))
            
            status_match = self.WAVE_STATUS_RE.match(line)
            if status_match:
                current_wave_status = (i, status_match.group(1))
            
            complete_match = self.WAVE_COMPLETE_RE.match(line)
            if complete_match:
                current_wave_complete = (i, complete_match.group(1))
        
        if current_wave_start:
            wave_sections.append((current_wave_start, len(self.lines), current_wave_auth, current_wave_status, current_wave_complete))
        
        # Validate each wave's authorization state
        for start, end, auth, wave_status, wave_complete in wave_sections:
            # AUTH-3: REQUIRED with BLOCKED is suspicious
            if auth and wave_status:
                auth_line, auth_value = auth
                status_line, status_value = wave_status
                if auth_value == "REQUIRED" and status_value == "BLOCKED":
                    self._add(Severity.WARN, "AUTH-3", status_line,
                             "AUTHORIZATION_STATUS=REQUIRED with WAVE_STATUS=BLOCKED is suspicious. BLOCKED should indicate technical barrier, not authorization need.")
            
            # CONS-5: DENIED requires WAVE_COMPLETE=NO
            if auth and wave_complete:
                auth_line, auth_value = auth
                complete_line, complete_value = wave_complete
                if auth_value == "DENIED" and complete_value == "YES":
                    self._add(Severity.ERROR, "CONS-5", complete_line,
                             "AUTHORIZATION_STATUS=DENIED but WAVE_COMPLETE=YES. Denied authorization must prevent completion.")
            
            # Check if prose declares authorization requirement but marker is missing
            wave_content = '\n'.join(self.lines[start-1:end])
            prose_requires_auth = any(phrase in wave_content.lower() for phrase in [
                "requires user authorization", "requires authorization", "user must authorize",
                "modifies shared templates", "modifies shared", "modifies ci", "modifies governance"
            ])
            if prose_requires_auth and not auth:
                self._add(Severity.FAIL, "AUTH-7", start,
                         "Wave prose declares authorization requirement but AUTHORIZATION_STATUS marker is missing.")


def main():
    parser = argparse.ArgumentParser(
        description="Validate a single plan file against simplified-plan-format-v1",
        epilog="Forward-only validation - does not scan historical plans by default."
    )
    parser.add_argument(
        "plan_file",
        type=Path,
        help="Path to the plan markdown file to validate"
    )
    parser.add_argument(
        "--bypass",
        action="store_true",
        help="Skip validation (sets PLAN_FORMAT_BYPASS=1)"
    )
    parser.add_argument(
        "--advisory",
        action="store_true",
        help="Treat FAIL as WARN (sets PLAN_FORMAT_ADVISORY=1)"
    )
    
    args = parser.parse_args()
    
    if args.bypass:
        print(f"[BYPASS] {args.plan_file}: Validation skipped (PLAN_FORMAT_BYPASS=1)")
        sys.exit(0)
    
    if not args.plan_file.exists():
        print(f"[ERROR] File not found: {args.plan_file}", file=sys.stderr)
        sys.exit(2)
    
    content = args.plan_file.read_text(encoding="utf-8")
    validator = PlanFormatValidator(content, str(args.plan_file))
    violations = validator.validate()
    
    # Count by severity
    fails = sum(1 for v in violations if v.severity == Severity.FAIL)
    errors = sum(1 for v in violations if v.severity == Severity.ERROR)
    warns = sum(1 for v in violations if v.severity == Severity.WARN)
    infos = sum(1 for v in violations if v.severity == Severity.INFO)
    
    # Adjust severity for advisory mode
    if args.advisory:
        fails, warns = 0, fails + warns
    
    # Print results
    plan_name = args.plan_file.name
    if fails == 0 and errors == 0:
        print(f"[PASS] {plan_name}: 0 FAIL, 0 ERROR, {warns} WARN, {infos} INFO")
    else:
        print(f"[FAIL] {plan_name}: {fails} FAIL, {errors} ERROR, {warns} WARN, {infos} INFO")
    
    for v in violations:
        if v.severity == Severity.FAIL and args.advisory:
            severity_str = "WARN (advisory)"
        else:
            severity_str = v.severity.value
        print(f"[{severity_str}] {plan_name}:{v.line_num} — {v.rule_id}: {v.message}")
    
    sys.exit(1 if (fails > 0 or errors > 0) else 0)


if __name__ == "__main__":
    main()
