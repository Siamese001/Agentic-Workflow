"""
Additional HITL validator tests for star marker and confidence band rules.
"""

import textwrap
from pathlib import Path

import pytest

import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ops_scripts.ci.validate_hitl_format import validate_file


@pytest.fixture()
def tmp_md(tmp_path):
    """Return a factory that writes content to a .md file and returns its Path."""

    def _make(content: str, name: str = "test.md") -> Path:
        p = tmp_path / name
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return p

    return _make


class TestStarMarkerValidation:
    def test_failure_missing_star_marker_on_high_confidence(self, tmp_md):
        """Failure: HIGH confidence option (>=0.85) without star marker -> MISSING_STAR_MARKER."""
        content = '''\
            ask_user_question(
              question="""Recommended: Fix
            Why it wins: best path.
            What you are optimizing for: speed.
            What is being traded off: scope.
            Candidates evaluated: 2 | Surfaced: 1 | Suppressed (low confidence): 1 | Suppressed (non-distinct): 0""",
              options=[
                {
                  label: "Option A [0.91 HIGH]",
                  description: "decision_thesis: Fixes the root cause at source."
                }
              ],
              allowMultiple=false
            )
        '''
        violations = validate_file(tmp_md(content))
        issue_types = [v[1] for v in violations]
        assert "MISSING_STAR_MARKER" in issue_types

    def test_happy_medium_confidence_no_star_required(self, tmp_md):
        """Happy: MEDIUM confidence option (0.72-0.84) does NOT require star marker."""
        content = '''\
            ask_user_question(
              question="""Recommended: Fix
            Why it wins: best path.
            What you are optimizing for: speed.
            What is being traded off: scope.
            Candidates evaluated: 2 | Surfaced: 1 | Suppressed (low confidence): 1 | Suppressed (non-distinct): 0""",
              options=[
                {
                  label: "⭐ Option A [0.88 HIGH]",
                  description: "decision_thesis: Best approach."
                },
                {
                  label: "Option B [0.76 MEDIUM]",
                  description: "decision_thesis: Alternative approach."
                }
              ],
              allowMultiple=false
            )
        '''
        violations = validate_file(tmp_md(content))
        assert violations == [], f"Expected no violations, got: {violations}"


class TestLowConfidenceSuppression:
    def test_failure_low_confidence_surfaced(self, tmp_md):
        """Failure: LOW confidence band surfaced -> LOW_CONFIDENCE_SURFACED (should be suppressed)."""
        content = '''\
            ask_user_question(
              question="""Recommended: Fix
            Why it wins: best path.
            What you are optimizing for: speed.
            What is being traded off: scope.
            Candidates evaluated: 3 | Surfaced: 2 | Suppressed (low confidence): 0 | Suppressed (non-distinct): 0""",
              options=[
                {
                  label: "⭐ Option A [0.91 HIGH]",
                  description: "decision_thesis: Best approach."
                },
                {
                  label: "Option B [0.65 LOW]",
                  description: "decision_thesis: Weak alternative."
                }
              ],
              allowMultiple=false
            )
        '''
        violations = validate_file(tmp_md(content))
        issue_types = [v[1] for v in violations]
        assert "LOW_CONFIDENCE_SURFACED" in issue_types

    def test_happy_low_confidence_suppressed_note(self, tmp_md):
        """Happy: LOW confidence option noted as suppressed in telemetry (not surfaced as option)."""
        content = '''\
            ask_user_question(
              question="""Recommended: Fix
            Why it wins: best path.
            What you are optimizing for: speed.
            What is being traded off: scope.
            Candidates evaluated: 3 | Surfaced: 2 | Suppressed (low confidence): 1 | Suppressed (non-distinct): 0""",
              options=[
                {
                  label: "⭐ Option A [0.91 HIGH]",
                  description: "decision_thesis: Best approach."
                },
                {
                  label: "Option B [0.76 MEDIUM]",
                  description: "decision_thesis: Alternative approach."
                }
              ],
              allowMultiple=false
            )

            **Note**: Option C (score 0.68) suppressed - below 0.72 surface_threshold.
        '''
        violations = validate_file(tmp_md(content))
        # Should pass - low confidence option is only mentioned in note, not surfaced
        assert violations == [], f"Expected no violations for suppressed note, got: {violations}"
