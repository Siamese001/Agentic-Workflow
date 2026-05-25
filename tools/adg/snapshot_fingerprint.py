"""Snapshot identity helpers for three-bucket audit receipts (W3.3)."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def snapshot_fingerprint(path: Path) -> dict[str, Any]:
    """Return stable identity fields for an ADG sqlite snapshot file."""
    path = Path(path).resolve()
    stat = path.stat()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "source_snapshot": path.name,
        "source_snapshot_path": str(path),
        "source_snapshot_sha256": digest,
        "source_snapshot_mtime_iso": datetime.fromtimestamp(
            stat.st_mtime, tz=timezone.utc
        ).isoformat(),
        "source_snapshot_size_bytes": stat.st_size,
    }


def print_audit_receipt(report: dict[str, Any], *, prefix: str = "AUDIT_RECEIPT") -> None:
    """Emit a single-line stdout receipt tying a gap report to its snapshot."""
    print(
        f"{prefix}: "
        f"snapshot={report.get('snapshot', '')} "
        f"sha256={report.get('source_snapshot_sha256', 'MISSING')} "
        f"mtime={report.get('source_snapshot_mtime_iso', 'MISSING')} "
        f"generated_at={report.get('generated_at', '')} "
        f"health_pct={report.get('health_score_pct_triplet_attested', 0.0)} "
        f"runtime_proof={report.get('runtime_proof_status', '')}"
    )
