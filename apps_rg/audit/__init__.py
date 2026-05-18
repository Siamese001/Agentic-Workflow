"""apps_rg-local audit consumers (SRFS receipt aggregation, etc.)."""

from apps_rg.audit.srfs_audit_advisory_judge import attach_advisory_judge_review, build_advisory_judge_review
from apps_rg.audit.srfs_receipt_aggregator import (
    build_srfs_audit_report,
    load_section_receipts,
    normalize_section_receipt,
    validate_section_inventory,
    write_srfs_audit_report,
)

__all__ = [
    "attach_advisory_judge_review",
    "build_advisory_judge_review",
    "build_srfs_audit_report",
    "load_section_receipts",
    "normalize_section_receipt",
    "validate_section_inventory",
    "write_srfs_audit_report",
]
