"""P1–P6 R1B semantic cache chunk assembly — display text, whole-run lanes, claim summaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.cache.r1b_constants import (
    CHUNK_TYPE_CLAIM_LEDGER,
    CHUNK_TYPE_FINAL_RESUME,
    CHUNK_TYPE_SECTION_PROOF,
    SECTION_CHUNK_TYPES,
)
from apps_rg.cache.r1b_ingest import _read_json, _section_chunk_type
from apps_rg.cache.r1b_post_exit_eligibility import POST_EXIT_INGESTION_PHASE
from apps_rg.runtime.full_run_section_status import LANE_DISPLAY_TXT_CANDIDATES
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.runtime_proof_layout import FULL_RESUME_DIR_PREFIX

INGEST_PROFILE_SECTION_LANE = "section_lane"
INGEST_PROFILE_INTEGRATED_WHOLE_RUN = "integrated_whole_run"

_MAX_CHUNK_CHARS = 8000
_MIN_DISPLAY_TEXT_CHARS = 8


def detect_ingest_profile(run_dir: Path, manifest: dict[str, Any]) -> str:
    """Section lane folder vs integrated ``full_resume_*`` root with ``lanes/``."""
    if (run_dir / "lanes").is_dir():
        return INGEST_PROFILE_INTEGRATED_WHOLE_RUN
    if run_dir.name.startswith(FULL_RESUME_DIR_PREFIX):
        return INGEST_PROFILE_INTEGRATED_WHOLE_RUN
    section_id = str(manifest.get("section_id") or "").strip()
    if section_id and section_id not in ("", "integrated_whole_run"):
        return INGEST_PROFILE_SECTION_LANE
    return INGEST_PROFILE_INTEGRATED_WHOLE_RUN


def resolve_section_display_text(
    run_dir: Path,
    section_id: str,
) -> tuple[str, str | None]:
    """P1 — hiring-manager-visible copy from lane display TXT candidates."""
    candidates = LANE_DISPLAY_TXT_CANDIDATES.get(
        section_id,
        ("command_output.txt",),
    )
    for name in candidates:
        path = run_dir / name
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if len(text) >= _MIN_DISPLAY_TEXT_CHARS:
                return text[:_MAX_CHUNK_CHARS], str(path)
    return "", None


def extract_l2_fallback_text(l2_path: Path) -> str:
    """Fallback when display TXT missing — pull prose fields from ``l2_output.json``."""
    data = _read_json(l2_path)
    if not data:
        return ""
    for key in (
        "display_text",
        "resume_display_text",
        "text",
        "resume_text",
        "content",
        "body",
        "narrative",
    ):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()[:_MAX_CHUNK_CHARS]
    bullets = data.get("bullets")
    if isinstance(bullets, list) and bullets:
        lines = [str(b).strip() for b in bullets if str(b).strip()]
        if lines:
            return "\n".join(lines)[:_MAX_CHUNK_CHARS]
    return ""


def build_claim_ledger_chunk_text(ledger_path: Path) -> str:
    """P4 — compact claim lines for embedding (not bare ``claim_ledger_entry`` label)."""
    data = _read_json(ledger_path)
    if not data:
        return ""
    entries = data.get("claims") or data.get("entries") or data.get("claim_rows")
    if not isinstance(entries, list):
        return ""
    lines: list[str] = []
    for row in entries[:40]:
        if not isinstance(row, dict):
            continue
        fid = str(row.get("fact_id") or row.get("id") or "").strip()
        text = str(
            row.get("claim_text")
            or row.get("text")
            or row.get("claim")
            or row.get("statement")
            or ""
        ).strip()
        if fid and text:
            lines.append(f"{fid}: {text[:400]}")
        elif text:
            lines.append(text[:400])
    return "\n".join(lines)[:_MAX_CHUNK_CHARS]


def resolve_final_resume_path(run_dir: Path) -> Path | None:
    """P2 — stitched resume only at assembly root paths."""
    for rel in ("outputs/generated_resume.json", "generated_resume.json"):
        path = run_dir / rel
        if path.is_file() and path.stat().st_size > 0:
            return path
    return None


def _x2_status_for_dir(run_dir: Path) -> str:
    x2 = _read_json(run_dir / "x2_gate_outputs.json") or {}
    if x2.get("x2_failed", 1) == 0:
        return "PASS"
    gates = x2.get("gates")
    if isinstance(gates, list) and gates and all(
        isinstance(g, dict) and g.get("pass", True) for g in gates
    ):
        return "PASS"
    failed = x2.get("failed_gate_ids") or x2.get("x2_failed_gate_ids")
    if isinstance(failed, list) and not failed:
        return "PASS"
    return "FAIL"


def _append_section_output_row(
    rows: list[dict[str, Any]],
    *,
    section_id: str,
    run_dir: Path,
    lane_manifest: dict[str, Any] | None = None,
) -> None:
    text, artifact_ref = resolve_section_display_text(run_dir, section_id)
    if not text and (run_dir / "l2_output.json").is_file():
        text = extract_l2_fallback_text(run_dir / "l2_output.json")
        artifact_ref = artifact_ref or str(run_dir / "l2_output.json")
    if not text:
        return
    x3_doc = _read_json(run_dir / "x3_disposition.json") or {}
    rows.append(
        {
            "chunk_id": f"sec_{section_id}",
            "chunk_type": _section_chunk_type(section_id),
            "section_id": section_id,
            "chunk_text": text,
            "artifact_ref": artifact_ref or str(run_dir),
            "x2_status": _x2_status_for_dir(run_dir),
            "x3_code": str(x3_doc.get("x3_code") or ""),
        }
    )


def _append_claim_ledger_row(
    rows: list[dict[str, Any]],
    *,
    section_id: str,
    run_dir: Path,
) -> None:
    ledger = run_dir / "canonical_claim_ledger_v2.json"
    if not ledger.is_file():
        return
    claim_text = build_claim_ledger_chunk_text(ledger)
    if len(claim_text) < _MIN_DISPLAY_TEXT_CHARS:
        return
    rows.append(
        {
            "chunk_id": f"sec_{section_id}:claims",
            "chunk_type": CHUNK_TYPE_CLAIM_LEDGER,
            "section_id": section_id,
            "chunk_text": claim_text,
            "artifact_ref": str(ledger),
        }
    )


def build_section_lane_chunk_rows(
    run_dir: Path,
    *,
    manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    """P1 section-only ingest — display text + claims; no required ``final_resume`` on lane dir."""
    section_id = str(manifest.get("section_id") or "").strip()
    if not section_id:
        return []
    rows: list[dict[str, Any]] = []
    _append_section_output_row(rows, section_id=section_id, run_dir=run_dir)
    _append_claim_ledger_row(rows, section_id=section_id, run_dir=run_dir)

    final_path = resolve_final_resume_path(run_dir)
    if final_path is not None:
        text = final_path.read_text(encoding="utf-8")[:_MAX_CHUNK_CHARS]
        rows.append(
            {
                "chunk_id": "final_resume",
                "chunk_type": CHUNK_TYPE_FINAL_RESUME,
                "section_id": "assembly",
                "chunk_text": text,
                "artifact_ref": str(final_path),
            }
        )

    proof_eligible = bool(manifest.get("proof_eligible", False))
    runtime_status = str(manifest.get("runtime_generation_status") or "")
    if rows:
        rows.append(
            {
                "chunk_type": CHUNK_TYPE_SECTION_PROOF,
                "section_id": section_id,
                "artifact_ref": str(run_dir),
                "chunk_text": json.dumps(
                    {
                        "run_id": manifest.get("run_id"),
                        "proof_eligible": proof_eligible,
                        "runtime_generation_status": runtime_status,
                        "ingestion_phase": POST_EXIT_INGESTION_PHASE,
                        "ingest_profile": INGEST_PROFILE_SECTION_LANE,
                    },
                    sort_keys=True,
                ),
            }
        )
    return rows


def build_integrated_whole_run_chunk_rows(
    run_dir: Path,
    *,
    manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    """P2/P3 — one parent intent at root; ``final_resume`` + all lane display children."""
    rows: list[dict[str, Any]] = []

    final_path = resolve_final_resume_path(run_dir)
    if final_path is not None:
        text = final_path.read_text(encoding="utf-8")[:_MAX_CHUNK_CHARS]
        rows.append(
            {
                "chunk_id": "final_resume",
                "chunk_type": CHUNK_TYPE_FINAL_RESUME,
                "section_id": "assembly",
                "chunk_text": text,
                "artifact_ref": str(final_path),
            }
        )

    lanes_root = run_dir / "lanes"
    if lanes_root.is_dir():
        for lane in GENERATED_LANES:
            lane_dir = lanes_root / lane
            if not lane_dir.is_dir():
                continue
            lane_manifest = _read_json(lane_dir / "run_manifest.json") or {}
            _append_section_output_row(
                rows,
                section_id=lane,
                run_dir=lane_dir,
                lane_manifest=lane_manifest,
            )
            _append_claim_ledger_row(rows, section_id=lane, run_dir=lane_dir)

    section_id = str(manifest.get("section_id") or "integrated_whole_run")
    if not any(r.get("chunk_type") in SECTION_CHUNK_TYPES for r in rows):
        _append_section_output_row(rows, section_id=section_id, run_dir=run_dir)
        _append_claim_ledger_row(rows, section_id=section_id, run_dir=run_dir)

    proof_eligible = bool(manifest.get("proof_eligible", False))
    runtime_status = str(manifest.get("runtime_generation_status") or "")
    if rows:
        rows.append(
            {
                "chunk_type": CHUNK_TYPE_SECTION_PROOF,
                "section_id": section_id,
                "artifact_ref": str(run_dir),
                "chunk_text": json.dumps(
                    {
                        "run_id": manifest.get("run_id"),
                        "proof_eligible": proof_eligible,
                        "runtime_generation_status": runtime_status,
                        "ingestion_phase": POST_EXIT_INGESTION_PHASE,
                        "ingest_profile": INGEST_PROFILE_INTEGRATED_WHOLE_RUN,
                        "lane_count": sum(
                            1 for lane in GENERATED_LANES if (lanes_root / lane).is_dir()
                        ),
                    },
                    sort_keys=True,
                ),
            }
        )
    return rows


def build_chunk_rows_from_run_dir(
    run_dir: Path,
    *,
    manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    """Route P1 section vs P2 whole-run chunk assembly."""
    profile = detect_ingest_profile(run_dir, manifest)
    if profile == INGEST_PROFILE_INTEGRATED_WHOLE_RUN:
        return build_integrated_whole_run_chunk_rows(run_dir, manifest=manifest)
    return build_section_lane_chunk_rows(run_dir, manifest=manifest)


__all__ = [
    "INGEST_PROFILE_INTEGRATED_WHOLE_RUN",
    "INGEST_PROFILE_SECTION_LANE",
    "build_chunk_rows_from_run_dir",
    "build_claim_ledger_chunk_text",
    "build_integrated_whole_run_chunk_rows",
    "build_section_lane_chunk_rows",
    "detect_ingest_profile",
    "resolve_final_resume_path",
    "resolve_section_display_text",
]
