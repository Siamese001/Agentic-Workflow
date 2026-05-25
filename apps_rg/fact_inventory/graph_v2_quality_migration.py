"""Controlled graph v2 migration audit + remediation (graph-skills-quality W3)."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import default_augmented_skills_graph_path, load_augmented_skills_graph
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    skill_row_eligible_for_external_claim,
    validate_arsenal_ledger_shape,
)
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
ACTIVE_PREFIXES = ("ACTIVE", "ACTIVE_CONFIRMED")
VALID_SECTIONS = frozenset(GENERATED_LANES)
INVALID_LEGACY_SECTIONS = frozenset({"early_career"})


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _ledger_digest(ledger: dict[str, Any]) -> str:
    return _sha256_hex(json.dumps(ledger, sort_keys=True, ensure_ascii=False, separators=(",", ":")))


def _is_active(row: dict[str, Any]) -> bool:
    status = str(row.get("activation_status") or "")
    return status == "ACTIVE" or status.startswith("ACTIVE_")


def derive_graph_hop_path(row: dict[str, Any]) -> list[str]:
    """Runtime-canonical hop shape for W3 ACTIVE rows."""
    track = str(row.get("career_track_id") or "TRACK_UNKNOWN")
    track_slug = track.lower() if track.startswith("TRACK_") else track
    pillar = str(row.get("pillar") or row.get("subpillar") or "pillar_unknown")
    sid = str(row.get("skill_id") or "")
    links = [str(x) for x in (row.get("fact_id_links") or []) if str(x).strip()]
    fid = links[0] if links else "fact_missing"
    return [track_slug, pillar, sid, fid]


def sanitize_allowed_sections(sections: list[Any]) -> list[str]:
    out = [str(s) for s in sections if str(s) in VALID_SECTIONS]
    return sorted(set(out))


def audit_active_skill_orphans(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    """Return orphan violations for ACTIVE / ACTIVE_CONFIRMED skill rows."""
    nodes = {
        str(n.get("node_id"))
        for n in (ledger.get("graph_nodes") or [])
        if isinstance(n, dict) and n.get("node_id")
    }
    orphans: list[dict[str, Any]] = []
    for row in ledger.get("skill_rows") or []:
        if not isinstance(row, dict) or not _is_active(row):
            continue
        sid = str(row.get("skill_id") or "")
        reasons: list[str] = []
        links = row.get("fact_id_links") or []
        if not links:
            reasons.append("empty_fact_id_links")
        if sid and sid not in nodes:
            reasons.append("missing_graph_node")
        sections = list(row.get("allowed_sections") or [])
        if not sections:
            reasons.append("empty_allowed_sections")
        invalid = [s for s in sections if s not in VALID_SECTIONS]
        if invalid:
            reasons.append(f"invalid_allowed_sections:{invalid}")
        hop = row.get("graph_hop_path") or []
        if not hop:
            reasons.append("missing_graph_hop_path")
        elif len(hop) < 2:
            reasons.append("graph_hop_path_too_short")
        if str(row.get("activation_status")) == "ACTIVE_CONFIRMED" and not skill_row_eligible_for_external_claim(row):
            reasons.append("not_eligible_for_external_claim")
        if reasons:
            orphans.append({"skill_id": sid, "reasons": reasons, "activation_status": row.get("activation_status")})
    return orphans


def _ensure_link_class(row: dict[str, Any]) -> dict[str, str]:
    existing = row.get("link_class_by_fact")
    if isinstance(existing, dict) and existing:
        return {str(k): str(v) for k, v in existing.items()}
    out: dict[str, str] = {}
    for fid in row.get("fact_id_links") or []:
        out[str(fid)] = "primary"
    return out


def apply_w3_controlled_remediation(ledger: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Patch ACTIVE rows: strip legacy sections, materialize hop paths + migration metadata."""
    migrations: list[dict[str, Any]] = []
    rows = ledger.get("skill_rows") or []
    for row in rows:
        if not isinstance(row, dict) or not _is_active(row):
            continue
        sid = str(row.get("skill_id") or "")
        before_sections = list(row.get("allowed_sections") or [])
        invalid = [s for s in before_sections if s not in VALID_SECTIONS]
        needs_hop = not (row.get("graph_hop_path") or [])
        needs_links_meta = not row.get("link_class_by_fact") or not row.get("source_ledger_ref")
        if not invalid and not needs_hop and not needs_links_meta:
            continue
        after_sections = sanitize_allowed_sections(before_sections)
        if not after_sections and (row.get("fact_id_links") or []):
            after_sections = ["competencies"]
        before = {
            "allowed_sections": before_sections,
            "graph_hop_path": row.get("graph_hop_path"),
            "link_class_by_fact": row.get("link_class_by_fact"),
            "source_ledger_ref": row.get("source_ledger_ref"),
        }
        row["allowed_sections"] = after_sections
        row["graph_hop_path"] = derive_graph_hop_path(row)
        row["link_class_by_fact"] = _ensure_link_class(row)
        primary = (row.get("fact_id_links") or [None])[0]
        row["source_ledger_ref"] = str(row.get("source_ledger_ref") or primary or sid)
        migrations.append(
            {
                "skill_id": sid,
                "activation_status": row.get("activation_status"),
                "before": before,
                "after": {
                    "allowed_sections": after_sections,
                    "graph_hop_path": row["graph_hop_path"],
                    "link_class_by_fact": row["link_class_by_fact"],
                    "source_ledger_ref": row["source_ledger_ref"],
                },
                "migration_note": "W3 strip invalid allowed_sections; derive graph_hop_path",
            }
        )
    gmeta = ledger.setdefault("graph_metadata", {})
    if not isinstance(gmeta, dict):
        gmeta = {}
        ledger["graph_metadata"] = gmeta
    gmeta["graph_skills_quality_w3"] = {
        "plan_id": PLAN_ID,
        "schema_tag": "master_skills_arsenal_graph_v2_quality",
        "applied_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return ledger, migrations


def compute_graph_v2_digest(ledger: dict[str, Any]) -> str:
    """Pinned digest for W10 Brown fixture checks (graph + ACTIVE skill slice)."""
    active_rows = [
        {
            "skill_id": r.get("skill_id"),
            "allowed_sections": r.get("allowed_sections"),
            "fact_id_links": r.get("fact_id_links"),
            "graph_hop_path": r.get("graph_hop_path"),
            "activation_status": r.get("activation_status"),
        }
        for r in (ledger.get("skill_rows") or [])
        if isinstance(r, dict) and _is_active(r)
    ]
    active_rows.sort(key=lambda x: str(x.get("skill_id")))
    payload = {
        "graph_metadata": ledger.get("graph_metadata"),
        "active_skill_rows": active_rows,
    }
    return _sha256_hex(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")))


def backup_ledger_v1(ledger_path: Path, *, backups_dir: Path | None = None) -> Path:
    root = _repo_root()
    dest_dir = backups_dir or (root / "artifacts/apps_rg/fact_inventory/backups")
    dest_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = dest_dir / f"master_skills_arsenal_ledger_pre_graph_v2_w3_{ts}.json"
    shutil.copy2(ledger_path, dest)
    return dest


def run_w3_migration(
    *,
    repo_root: Path | None = None,
    apply_patches: bool = True,
    rematerialize_sqlite: bool = True,
) -> dict[str, Any]:
    root = repo_root or _repo_root()
    ledger_path = default_augmented_skills_graph_path(root)
    ledger_before = json.loads(ledger_path.read_text(encoding="utf-8"))
    digest_before = _ledger_digest(ledger_before)
    orphans_before = audit_active_skill_orphans(ledger_before)
    backup_path = backup_ledger_v1(ledger_path) if apply_patches else None

    ledger = ledger_before
    migrations: list[dict[str, Any]] = []
    if apply_patches:
        ledger, migrations = apply_w3_controlled_remediation(dict(ledger))
        validate_arsenal_ledger_shape(ledger)
        ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")

    orphans_after = audit_active_skill_orphans(ledger)
    digest_after = _ledger_digest(ledger)
    graph_v2_digest = compute_graph_v2_digest(ledger)

    sqlite_summary: dict[str, Any] | None = None
    if rematerialize_sqlite and not orphans_after:
        from apps_rg.fact_inventory.augmented_skills_graph_sqlite import materialize_augmented_skills_graph_sqlite

        sqlite_summary = materialize_augmented_skills_graph_sqlite(graph=ledger, repo_root=root)

    status = "PASS" if not orphans_after else "FAIL"
    return {
        "schema": "graph_v2_migration_receipt_v1",
        "plan_id": PLAN_ID,
        "wave": "W3",
        "status": status,
        "ledger_path": ledger_path.relative_to(root).as_posix(),
        "backup_v1_path": backup_path.relative_to(root).as_posix() if backup_path else None,
        "ledger_digest_before": digest_before,
        "ledger_digest_after": digest_after,
        "graph_v2_digest_pinned": graph_v2_digest,
        "active_orphan_count_before": len(orphans_before),
        "active_orphan_count_after": len(orphans_after),
        "orphans_before": orphans_before,
        "orphans_after": orphans_after,
        "controlled_migrations": migrations,
        "sqlite_materialization": sqlite_summary,
        "rollback_doc": "docs/apps_rg/graph_skills_graph_v2_rollback.md",
    }


__all__ = [
    "audit_active_skill_orphans",
    "apply_w3_controlled_remediation",
    "compute_graph_v2_digest",
    "derive_graph_hop_path",
    "run_w3_migration",
]
