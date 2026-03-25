"""
Phase 2: Auto-disposition processor for ADG violations.

Links test coverage and guardian comments to violations to close the
detection→validation feedback loop.

Key capabilities:
1. Auto-mark violations as 'tested' when covered by tests_execution_of edges
2. Auto-mark violations as 'approved' when guardian comments exist
3. Update disposition_source with test names or guardian comment text
4. Handle line-range overlap detection (violation line within tested function span)
"""

from __future__ import annotations

import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import Generator, NamedTuple, Optional


class ViolationInfo(NamedTuple):
    """Violation data from ADG."""
    id: int
    edge_id: int
    file_path: str
    line_no: int
    evidence: str
    severity: str
    disposition: str


class TestCoverage(NamedTuple):
    """Test coverage data from ADG."""
    test_name: str
    test_file: str
    target_symbol: str
    target_file: str
    target_line_start: int
    target_line_end: int


class GuardianComment(NamedTuple):
    """Parsed guardian comment information."""
    file_path: str
    line_no: int
    comment_text: str
    exception_type: str
    reason: str


class ViolationDispositionProcessor:
    """Phase 2: Auto-disposition violations based on test coverage and guardian comments."""

    def __init__(self, adg_path: Path):
        self.adg_path = adg_path
        self.conn: Optional[sqlite3.Connection] = None

    def __enter__(self) -> ViolationDispositionProcessor:
        self.conn = sqlite3.connect(str(self.adg_path))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.conn:
            self.conn.close()

    def process_all_dispositions(self) -> dict[str, int]:
        """Process all untriaged violations and update dispositions."""
        if not self.conn:
            raise RuntimeError("Processor not used as context manager")

        print("🔗 Phase 2: Auto-linking test coverage and guardian comments...")

        # Load untriaged antipattern violations
        violations = self._load_untriaged_violations()
        print(f"  Processing {len(violations)} untriaged violations")

        # Load test coverage data
        test_coverage = self._load_test_coverage()
        print(f"  Loaded {len(test_coverage)} test coverage links")

        # Load guardian comments
        guardian_comments = self._load_guardian_comments()
        print(f"  Found {len(guardian_comments)} guardian comments")

        # Process dispositions
        results = {
            'tested': 0,
            'approved': 0,
            'remaining': 0
        }

        for violation in violations:
            disposition, source = self._determine_disposition(
                violation, test_coverage, guardian_comments
            )

            if disposition != violation.disposition:
                self._update_violation_disposition(violation.id, disposition, source)
                results[disposition] += 1
            else:
                results['remaining'] += 1

        self.conn.commit()

        print(f"  ✅ Auto-dispositioned: {results['tested']} tested, {results['approved']} approved")
        print(f"  📊 Remaining untriaged: {results['remaining']}")

        return results

    def _load_untriaged_violations(self) -> list[ViolationInfo]:
        """Load untriaged antipattern violations."""
        # Check if disposition column exists (Phase 1 extension)
        cursor = self.conn.execute("PRAGMA table_info(violations)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'disposition' in columns:
            if 'severity' in columns:
                cursor = self.conn.execute("""
                    SELECT id, edge_id, file_path, line_no, evidence, severity, disposition
                    FROM violations
                    WHERE category = 'antipattern'
                      AND disposition = 'untriaged'
                    ORDER BY file_path, line_no
                """)
            else:
                # Phase 1 partial schema - use default severity
                cursor = self.conn.execute("""
                    SELECT id, edge_id, file_path, line_no, evidence, 'MEDIUM', disposition
                    FROM violations
                    WHERE category = 'antipattern'
                      AND disposition = 'untriaged'
                    ORDER BY file_path, line_no
                """)
        else:
            # Pre-Phase 1 schema - all violations are untriaged, use defaults
            cursor = self.conn.execute("""
                SELECT id, edge_id, file_path, line_no, evidence, 'MEDIUM', 'untriaged'
                FROM violations
                WHERE category = 'antipattern'
                ORDER BY file_path, line_no
            """)

        return [ViolationInfo(*row) for row in cursor.fetchall()]

    def _load_test_coverage(self) -> list[TestCoverage]:
        """Load test coverage from tests_execution_of edges with line span info."""
        # Join with nodes to get line span information for target symbols
        cursor = self.conn.execute("""
            SELECT
                src.adg_name as test_name,
                src.resolved_path as test_file,
                dst.adg_name as target_symbol,
                dst.resolved_path as target_file,
                dst.span_line as target_line_start,
                dst.span_end_line as target_line_end
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            JOIN nodes dst ON dst.id = e.dst_id
            WHERE e.relation_type = 'tests_execution_of'
              AND dst.span_line > 0
              AND dst.span_end_line >= dst.span_line
            ORDER BY dst.resolved_path, dst.span_line
        """)

        return [TestCoverage(*row) for row in cursor.fetchall()]

    def _load_guardian_comments(self) -> list[GuardianComment]:
        """Scan source files for guardian comments."""
        # Check if disposition column exists
        cursor = self.conn.execute("PRAGMA table_info(violations)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'disposition' in columns:
            cursor = self.conn.execute("""
                SELECT DISTINCT file_path
                FROM violations
                WHERE category = 'antipattern'
                  AND disposition = 'untriaged'
            """)
        else:
            # Pre-Phase 1 schema - scan all antipattern violations
            cursor = self.conn.execute("""
                SELECT DISTINCT file_path
                FROM violations
                WHERE category = 'antipattern'
            """)

        guardian_comments = []

        for (file_path,) in cursor.fetchall():
            try:
                file_obj = Path(file_path)
                if not file_obj.exists():
                    continue

                content = file_obj.read_text(encoding='utf-8')
                lines = content.splitlines()

                for line_no, line in enumerate(lines, 1):
                    if '# guardian:' in line:
                        comment = self._parse_guardian_comment(file_path, line_no, line)
                        if comment:
                            guardian_comments.append(comment)

            except Exception as e:
                print(f"    ⚠️  Could not scan {file_path}: {e}")

        return guardian_comments

    def _parse_guardian_comment(self, file_path: str, line_no: int, line: str) -> Optional[GuardianComment]:
        """Parse a guardian comment line."""
        # Pattern: # guardian: allow-silent-swallow - <exception_type> is acceptable here
        match = re.search(r'# guardian:\s*allow-silent-swallow\s*-\s*([^-\s]+)', line)
        if not match:
            return None

        exception_type = match.group(1).strip()
        comment_text = line.strip()

        # Extract reason after the exception type
        reason = ''
        if ' - ' in line:
            parts = line.split(' - ', 1)
            if len(parts) > 1:
                reason = parts[1].strip()

        return GuardianComment(file_path, line_no, comment_text, exception_type, reason)

    def _determine_disposition(
        self,
        violation: ViolationInfo,
        test_coverage: list[TestCoverage],
        guardian_comments: list[GuardianComment]
    ) -> tuple[str, str]:
        """Determine the appropriate disposition for a violation."""

        # Priority 1: Check for guardian comment on or before the violation line
        for comment in guardian_comments:
            if (comment.file_path == violation.file_path and
                abs(comment.line_no - violation.line_no) <= 5):  # Within 5 lines
                return 'approved', f'guardian: {comment.comment_text}'

        # Priority 2: Check for test coverage
        for coverage in test_coverage:
            if (coverage.target_file == violation.file_path and
                coverage.target_line_start <= violation.line_no <= coverage.target_line_end):
                return 'tested', f'test:{coverage.test_name}'

        # No disposition change needed
        return violation.disposition, ''

    def _update_violation_disposition(self, violation_id: int, disposition: str, source: str) -> None:
        """Update a single violation's disposition."""
        # Check if disposition columns exist (Phase 1 extension)
        cursor = self.conn.execute("PRAGMA table_info(violations)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'disposition' in columns and 'disposition_source' in columns and 'disposition_date' in columns:
            # Full Phase 1 schema - update all fields
            self.conn.execute("""
                UPDATE violations
                SET disposition = ?, disposition_source = ?, disposition_date = ?
                WHERE id = ?
            """, (disposition, source, datetime.utcnow().isoformat(), violation_id))
        elif 'disposition' in columns:
            # Partial Phase 1 schema - update only disposition
            self.conn.execute("""
                UPDATE violations
                SET disposition = ?
                WHERE id = ?
            """, (disposition, violation_id))
        else:
            # Pre-Phase 1 schema - cannot update, skip
            print(f"    ⚠️  Cannot update disposition: Phase 1 schema not available")
            return


def run_phase2_disposition_processing(adg_path: Path) -> dict[str, int]:
    """Convenience function to run Phase 2 processing."""
    with ViolationDispositionProcessor(adg_path) as processor:
        return processor.process_all_dispositions()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python phase2_disposition_processor.py <path_to_adg.sqlite>")
        sys.exit(1)

    adg_path = Path(sys.argv[1])
    if not adg_path.exists():
        print(f"Error: ADG file not found: {adg_path}")
        sys.exit(1)

    results = run_phase2_disposition_processing(adg_path)
    print(f"\nPhase 2 Results: {results}")
