"""G-16-23: RCA report types for System Learning root cause analysis.

Immutable, content-addressed RCA reports with deterministic hashing.

Invariants:
  - All types are frozen dataclasses
  - Canonical byte serialization for hashing
  - Findings sorted deterministically
  - report_id = report_hash
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RCAFinding:
    """A single RCA finding (failure pattern).

    Fields
    ------
    category : str
        Failure category (e.g., "SYNTAX", "IMPORT", "TIMEOUT").
    signature : str
        Normalized signature identifying the failure pattern.
    count : int
        Number of occurrences of this pattern.
    evidence_hash : str
        SHA-256 hash of canonical normalized evidence for this signature.
    """

    category: str
    signature: str
    count: int
    evidence_hash: str


@dataclass(frozen=True, slots=True)
class RCAReport:
    """Immutable RCA report with content-addressed ID.

    Fields
    ------
    report_id : str
        Content-addressed ID (SHA-256 hash of canonical bytes).
    snapshot_id : str
        The snapshot this RCA is based on.
    window_start_utc : int
        Start of analysis window (Unix timestamp).
    window_end_utc : int
        End of analysis window (Unix timestamp).
    findings : tuple[RCAFinding, ...]
        Findings sorted deterministically by (category, signature).
    report_hash : str
        SHA-256 hash of canonical bytes (same as report_id).
    """

    report_id: str
    snapshot_id: str
    window_start_utc: int
    window_end_utc: int
    findings: tuple[RCAFinding, ...]
    report_hash: str


def canonical_bytes(report: RCAReport) -> bytes:
    """Return deterministic canonical byte representation of RCA report.

    Serialization rules:
      - Fields in fixed order
      - Findings sorted by (category, signature)
      - Delimiter: ASCII unit separator (0x1F)

    Parameters
    ----------
    report : RCAReport
        The RCA report to serialize.

    Returns
    -------
    bytes
        Canonical byte representation.
    """
    sorted_findings = sorted(report.findings, key=lambda f: (f.category, f.signature))
    parts = [
        report.snapshot_id.encode("utf-8"),
        str(report.window_start_utc).encode("utf-8"),
        str(report.window_end_utc).encode("utf-8"),
    ]
    for finding in sorted_findings:
        finding_parts = [
            finding.category.encode("utf-8"),
            finding.signature.encode("utf-8"),
            str(finding.count).encode("utf-8"),
            finding.evidence_hash.encode("utf-8"),
        ]
        parts.append(b"\x1e".join(finding_parts))
    return b"\x1f".join(parts)


def compute_report_hash(report: RCAReport) -> str:
    """Compute SHA-256 hash of canonical bytes.

    Parameters
    ----------
    report : RCAReport
        The RCA report to hash.

    Returns
    -------
    str
        SHA-256 hex digest.
    """
    return hashlib.sha256(canonical_bytes(report)).hexdigest()


def create_rca_report(
    snapshot_id: str, window_start_utc: int, window_end_utc: int, findings: tuple[RCAFinding, ...],
) -> RCAReport:
    """Create an RCA report with content-addressed ID.

    Parameters
    ----------
    snapshot_id : str
        The snapshot this RCA is based on.
    window_start_utc : int
        Start of analysis window.
    window_end_utc : int
        End of analysis window.
    findings : tuple[RCAFinding, ...]
        Findings (will be sorted deterministically).

    Returns
    -------
    RCAReport
        RCA report with report_id = report_hash.
    """
    temp_report = RCAReport(
        report_id="",
        snapshot_id=snapshot_id,
        window_start_utc=window_start_utc,
        window_end_utc=window_end_utc,
        findings=findings,
        report_hash="",
    )
    report_hash = compute_report_hash(temp_report)
    return RCAReport(
        report_id=report_hash,
        snapshot_id=snapshot_id,
        window_start_utc=window_start_utc,
        window_end_utc=window_end_utc,
        findings=findings,
        report_hash=report_hash,
    )
