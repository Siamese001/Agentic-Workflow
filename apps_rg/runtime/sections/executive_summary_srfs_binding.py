"""Default executive_summary SRFS binding: materialize + resolve active SelectedRoleFactSet on disk.

Selection uses ``select_candidate_facts_for_role`` (enhanced graph / arsenal-backed executive
slice). Runtime default CLI must consume this artifact without ``--selected-role-fact-set``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.candidate_fact_ledger import (
    default_ledger_path,
    default_taxonomy_path,
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
)
from apps_rg.fact_inventory.selected_role_fact_set import (
    digest_text,
    select_candidate_facts_for_role,
    selected_role_fact_set_to_json_dict,
    utc_timestamp_slug,
    write_selected_role_fact_set_artifacts,
)

ACTIVE_SRFS_JSON_REL = "artifacts/apps_rg/fact_inventory/selected_role_fact_set_active.json"
ACTIVE_SRFS_MANIFEST_REL = "artifacts/apps_rg/fact_inventory/selected_role_fact_set_active_manifest.json"
MANIFEST_SCHEMA = "executive_summary_srfs_active_manifest_v1"


def active_srfs_paths(repo_root: Path) -> tuple[Path, Path]:
    root = repo_root.resolve()
    return root / Path(ACTIVE_SRFS_JSON_REL), root / Path(ACTIVE_SRFS_MANIFEST_REL)


def build_targeting_binding_digest(
    *,
    target_company: str,
    target_role: str,
    jd_text: str,
    briefing_text: str,
    repo_root: Path,
) -> str:
    """Stable digest for active SRFS manifest (re-materialize when targeting/ledger binding changes)."""
    root = repo_root.resolve()
    ledger_path = default_ledger_path(root)
    ledger_ref = (
        str(ledger_path.relative_to(root)) if ledger_path.is_relative_to(root) else str(ledger_path)
    )
    tax_path = default_taxonomy_path(root)
    tax_ref = str(tax_path.relative_to(root)) if tax_path.is_relative_to(root) else str(tax_path)
    material = "|".join(
        (
            target_company.strip(),
            target_role.strip(),
            digest_text(jd_text.strip()),
            digest_text(briefing_text.strip()),
            ledger_ref,
            tax_ref,
            "augmented_skills_graph:master_skills_arsenal_graph_v1",
        )
    )
    return digest_text(material)


def _load_manifest(manifest_path: Path) -> dict[str, Any] | None:
    if not manifest_path.is_file():
        return None
    try:
        doc = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None
    return doc if isinstance(doc, dict) else None


def materialize_active_selected_role_fact_set(
    *,
    repo_root: Path,
    target_company: str,
    target_role: str,
    jd_text: str,
    briefing_text: str,
    broad_skills_ledger_path: str | None = None,
) -> Path:
    """Run graph-skills-backed SRFS selection and write active JSON + manifest under fact_inventory."""
    root = repo_root.resolve()
    json_path, manifest_path = active_srfs_paths(root)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    ledger_path = Path(broad_skills_ledger_path) if broad_skills_ledger_path else default_ledger_path(root)
    if not ledger_path.is_file():
        raise ValueError(
            "executive_summary SRFS binding BLOCKED: candidate fact ledger missing at "
            f"{ledger_path}; cannot materialize SelectedRoleFactSet from enhanced graph skills."
        )

    ledger = load_master_candidate_fact_ledger(path=ledger_path)
    taxonomy = load_master_role_family_taxonomy(repo_root=root)
    tax_path = default_taxonomy_path(root)
    ledger_ref = (
        str(ledger_path.relative_to(root)) if ledger_path.is_relative_to(root) else str(ledger_path)
    )
    tax_ref = str(tax_path.relative_to(root)) if tax_path.is_relative_to(root) else str(tax_path)

    slug = utc_timestamp_slug()
    srfs = select_candidate_facts_for_role(
        target_company=target_company,
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
        ledger=ledger,
        taxonomy=taxonomy,
        source_ledger_path=ledger_ref,
        taxonomy_ref=tax_ref,
        now_slug=slug,
        repo_root=root,
    )
    exec_slice = list(srfs.selected_facts_by_section.get("executive_summary") or [])
    if not exec_slice:
        raise ValueError(
            "executive_summary SRFS binding BLOCKED: enhanced graph selection produced an empty "
            "executive_summary slice; cannot run default CLI without SRFS proof pool."
        )

    binding_digest = build_targeting_binding_digest(
        target_company=target_company,
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
        repo_root=root,
    )
    srfs_json = selected_role_fact_set_to_json_dict(srfs)
    json_path.write_text(json.dumps(srfs_json, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "binding_digest": binding_digest,
        "selection_id": srfs.selection_id,
        "selected_at": srfs.selected_at,
        "active_srfs_json": ACTIVE_SRFS_JSON_REL,
        "executive_summary_fact_count": len(exec_slice),
        "source_ledger_ref": ledger_ref,
        "taxonomy_ref": tax_ref,
        "proof_authority": "selected_role_fact_set",
        "graph_skills_projection": "select_candidate_facts_for_role_with_exec_summary_arsenal",
        "materialized_at_utc": slug,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return json_path


def resolve_executive_summary_default_srfs_path(
    *,
    repo_root: Path,
    target_company: str,
    target_role: str,
    jd_text: str,
    briefing_text: str,
    broad_skills_ledger_path: str | None = None,
) -> str:
    """Return repo-relative path to active SRFS JSON; materialize when missing or targeting digest stale."""
    root = repo_root.resolve()
    json_path, manifest_path = active_srfs_paths(root)
    binding_digest = build_targeting_binding_digest(
        target_company=target_company,
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
        repo_root=root,
    )
    manifest = _load_manifest(manifest_path)
    if json_path.is_file() and manifest and str(manifest.get("binding_digest") or "") == binding_digest:
        return (
            str(json_path.relative_to(root)) if json_path.is_relative_to(root) else str(json_path)
        )

    materialized = materialize_active_selected_role_fact_set(
        repo_root=root,
        target_company=target_company,
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
        broad_skills_ledger_path=broad_skills_ledger_path,
    )
    return (
        str(materialized.relative_to(root))
        if materialized.is_relative_to(root)
        else str(materialized)
    )


__all__ = [
    "ACTIVE_SRFS_JSON_REL",
    "ACTIVE_SRFS_MANIFEST_REL",
    "active_srfs_paths",
    "build_targeting_binding_digest",
    "materialize_active_selected_role_fact_set",
    "resolve_executive_summary_default_srfs_path",
]
