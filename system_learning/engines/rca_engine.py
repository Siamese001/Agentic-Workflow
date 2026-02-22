"""G-16-24: RCA engine for System Learning root cause analysis.

Pure analyzer producing deterministic RCA reports from audit slices.

Invariants:
  - Deterministic parsing rules
  - No randomness/time/env
  - Fail-closed on malformed input
  - Read-only inputs, proposal-only outputs
"""

from __future__ import annotations

import hashlib
import re

from system_learning.types.rca_types import RCAFinding, create_rca_report

# =============================================================================
# Exceptions
# =============================================================================


class RCAAnalysisError(RuntimeError):
    """Raised when RCA analysis fails."""


# =============================================================================
# Classification Rules
# =============================================================================

# Deterministic pattern rules for failure classification
# Each rule: (category, regex_pattern, signature_extractor)
CLASSIFICATION_RULES = [
    # SYNTAX errors
    ("SYNTAX", re.compile(r"SyntaxError:"), lambda line: "SyntaxError"),
    ("SYNTAX", re.compile(r"IndentationError:"), lambda line: "IndentationError"),
    ("SYNTAX", re.compile(r"TabError:"), lambda line: "TabError"),
    # IMPORT errors
    ("IMPORT", re.compile(r"ModuleNotFoundError:"), lambda line: "ModuleNotFoundError"),
    ("IMPORT", re.compile(r"ImportError:"), lambda line: "ImportError"),
    # TEST_DISCOVERY errors
    (
        "TEST_DISCOVERY",
        re.compile(r"ERROR collecting"),
        lambda line: "pytest_collection_error",
    ),
    (
        "TEST_DISCOVERY",
        re.compile(r"collection errors"),
        lambda line: "pytest_collection_errors",
    ),
    # POLICY_BLOCK errors
    (
        "POLICY_BLOCK",
        re.compile(r"SourceMutationBlocked"),
        lambda line: "SourceMutationBlocked",
    ),
    (
        "POLICY_BLOCK",
        re.compile(r"AuthorityViolation"),
        lambda line: "AuthorityViolation",
    ),
    # TIMEOUT errors
    ("TIMEOUT", re.compile(r"TimeoutError"), lambda line: "TimeoutError"),
    ("TIMEOUT", re.compile(r"timeout"), lambda line: "timeout"),
]


def classify_line(line: str) -> tuple[str, str] | None:
    """Classify a line into (category, signature).

    Parameters
    ----------
    line : str
        The line to classify.

    Returns
    -------
    tuple[str, str] | None
        (category, signature) if matched, None otherwise.
    """
    for category, pattern, signature_fn in CLASSIFICATION_RULES:
        if pattern.search(line):
            signature = signature_fn(line)
            return (category, signature)
    return None


# =============================================================================
# RCA Engine
# =============================================================================


def analyze_failures(
    snapshot_id: str,
    audit_slice: bytes,
    window_start_utc: int,
    window_end_utc: int,
) -> object:  # Returns RCAReport
    """Analyze failures from audit slice and produce RCA report.

    Deterministic parsing rules:
      - Treat audit_slice as UTF-8 text lines
      - Classify into categories by stable pattern rules
      - Count occurrences per (category, signature)
      - evidence_hash = SHA-256 of canonical normalized evidence bytes

    Parameters
    ----------
    snapshot_id : str
        The snapshot this RCA is based on.
    audit_slice : bytes
        Raw audit data to analyze.
    window_start_utc : int
        Start of analysis window.
    window_end_utc : int
        End of analysis window.

    Returns
    -------
    RCAReport
        Deterministic RCA report.

    Raises
    ------
    RCAAnalysisError
        If audit_slice cannot be decoded or window is invalid.
    """
    # Validate window
    if window_start_utc >= window_end_utc:
        raise RCAAnalysisError(f"Invalid window: start={window_start_utc} >= end={window_end_utc}")

    # Decode audit slice (fail-closed)
    try:
        audit_text = audit_slice.decode("utf-8")
    except UnicodeDecodeError as e:
        raise RCAAnalysisError(f"Failed to decode audit_slice as UTF-8: {e}") from e

    # Parse lines and classify
    lines = audit_text.splitlines()
    findings_dict: dict[tuple[str, str], list[str]] = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        classification = classify_line(line)
        if classification:
            category, signature = classification
            key = (category, signature)
            if key not in findings_dict:
                findings_dict[key] = []
            findings_dict[key].append(line)

    # If no findings, add UNKNOWN category
    if not findings_dict:
        findings_dict[("UNKNOWN", "no_patterns_matched")] = ["<no matching patterns>"]

    # Build findings
    findings = []
    for (category, signature), evidence_lines in findings_dict.items():
        count = len(evidence_lines)

        # Compute evidence_hash from canonical normalized evidence
        # Canonical: sorted lines, joined with newlines
        canonical_evidence = "\n".join(sorted(evidence_lines)).encode("utf-8")
        evidence_hash = hashlib.sha256(canonical_evidence).hexdigest()

        findings.append(
            RCAFinding(
                category=category,
                signature=signature,
                count=count,
                evidence_hash=evidence_hash,
            )
        )

    # Create report with deterministic hash
    return create_rca_report(
        snapshot_id=snapshot_id,
        window_start_utc=window_start_utc,
        window_end_utc=window_end_utc,
        findings=tuple(findings),
    )
