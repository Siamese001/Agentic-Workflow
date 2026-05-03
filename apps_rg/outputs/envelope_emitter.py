"""Emit ResumeBankEnvelope sidecar for apps_rg resume bank YAML.

Plan: apps-cross-app-precursors-c94c71 Wave 3.4 (GAP-4).

Threads `master_resume_source_sha256` lineage so downstream consumers can
detect when the bank drifts from the master_resume it was derived from.
"""

from __future__ import annotations

import argparse
import hashlib
import uuid
from pathlib import Path

import yaml

from apps_shared.contracts.cross_app.resume_bank import (
    ResumeBankEnvelope,
    ResumeBankPayload,
)

_DEFAULT_MASTER_RESUME = Path("apps_shared/data/master_resume.json")


def _sha256_of_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_payload(
    bank_path: Path, master_resume_path: Path | None = None
) -> ResumeBankPayload:
    raw = yaml.safe_load(bank_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"Resume bank YAML at {bank_path} is not a mapping.")

    master = master_resume_path or _DEFAULT_MASTER_RESUME
    if master.is_file():
        master_sha = _sha256_of_file(master)
    else:
        master_sha = "0" * 64  # unknown lineage sentinel

    return ResumeBankPayload(
        source_file=str(bank_path).replace("\\", "/"),
        master_resume_source_sha256=master_sha,
        points=list(raw.get("points") or []),
        star_bank=dict(raw.get("star_bank") or {}),
        rca_bank=list(raw.get("rca_bank") or []),
    )


def emit(
    *,
    bank_path: Path,
    master_resume_path: Path | None = None,
    trace_id: str | None = None,
    out_path: Path | None = None,
) -> Path:
    if not bank_path.is_file():
        raise FileNotFoundError(f"Resume bank not found: {bank_path}")
    trace_id = trace_id or uuid.uuid4().hex[:12]
    payload = build_payload(bank_path, master_resume_path)
    env = ResumeBankEnvelope.emit(trace_id=trace_id, payload=payload)
    if out_path is None:
        out_path = env.default_sidecar_path(bank_path.parent)
    env.write_sidecar(out_path)
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument(
        "--master-resume", type=Path, default=None, help="for lineage hash"
    )
    parser.add_argument("--trace-id", default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    written = emit(
        bank_path=args.bank,
        master_resume_path=args.master_resume,
        trace_id=args.trace_id,
        out_path=args.out,
    )
    print(f"Wrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
