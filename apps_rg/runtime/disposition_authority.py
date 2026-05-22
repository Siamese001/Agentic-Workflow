"""Normalized disposition authority labels for apps_rg runtime receipts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

DISPOSITION_AUTHORITY_SPINE = "spine"
DISPOSITION_AUTHORITY_LANE = "lane"
DISPOSITION_AUTHORITY_BINDING_HELPER = "binding_helper"

LANE_X3_ARTIFACT = "x3_disposition.json"
EXIT_DISPOSITION_RECEIPT_ARTIFACT = "exit_disposition_receipt.json"

_VALID_AUTHORITIES = frozenset(
    {
        DISPOSITION_AUTHORITY_SPINE,
        DISPOSITION_AUTHORITY_LANE,
        DISPOSITION_AUTHORITY_BINDING_HELPER,
    }
)


def lane_x3_disposition_overlay() -> dict[str, Any]:
    """Fields merged into section lane ``x3_disposition.json`` payloads."""
    return {
        "disposition_authority": DISPOSITION_AUTHORITY_LANE,
        "section_x3_authoritative": False,
        "section_x3_mirror_only": True,
        "spine_x3_claimed": False,
    }


def apply_lane_x3_authority_fields(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return payload with lane disposition authority labels (does not mutate input)."""
    out = dict(payload)
    out.update(lane_x3_disposition_overlay())
    return out


def _load_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _x3_code_from_doc(doc: Mapping[str, Any]) -> str | None:
    for key in ("x3_code", "final_x3_code", "apps_rg_package_x3_disposition"):
        val = doc.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    nested = doc.get("x3_disposition")
    if isinstance(nested, Mapping):
        code = nested.get("x3_code")
        if isinstance(code, str) and code.strip():
            return code.strip()
    return None


def resolve_lane_x3_from_artifact_refs(
    *,
    artifact_refs: Mapping[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    """Prefer ``exit_disposition_receipt.json`` over lane ``x3_disposition.json`` mirror."""
    receipt_rel = str(artifact_refs.get(EXIT_DISPOSITION_RECEIPT_ARTIFACT) or "").strip()
    mirror_rel = str(artifact_refs.get(LANE_X3_ARTIFACT) or "").strip()

    receipt_path = (repo_root / receipt_rel).resolve() if receipt_rel else None
    mirror_path = (repo_root / mirror_rel).resolve() if mirror_rel else None

    if receipt_path is not None and receipt_path.is_file():
        doc = _load_json(receipt_path)
        code = _x3_code_from_doc(doc)
        authority = str(doc.get("disposition_authority") or DISPOSITION_AUTHORITY_LANE)
        if authority not in _VALID_AUTHORITIES:
            authority = DISPOSITION_AUTHORITY_LANE
        return {
            "x3_code": code,
            "disposition_authority": authority,
            "authoritative_artifact": EXIT_DISPOSITION_RECEIPT_ARTIFACT,
            "section_x3_mirror_only": bool(doc.get("section_x3_mirror_only", True)),
            "spine_x3_claimed": bool(doc.get("spine_x3_claimed", False)),
            "canonical_exit_claimed": bool(doc.get("canonical_exit_claimed", False)),
        }

    if mirror_path is not None and mirror_path.is_file():
        doc = _load_json(mirror_path)
        code = _x3_code_from_doc(doc)
        return {
            "x3_code": code,
            "disposition_authority": str(
                doc.get("disposition_authority") or DISPOSITION_AUTHORITY_LANE
            ),
            "authoritative_artifact": LANE_X3_ARTIFACT,
            "section_x3_mirror_only": True,
            "spine_x3_claimed": False,
            "canonical_exit_claimed": False,
        }

    return {
        "x3_code": None,
        "disposition_authority": DISPOSITION_AUTHORITY_LANE,
        "authoritative_artifact": None,
        "section_x3_mirror_only": True,
        "spine_x3_claimed": False,
        "canonical_exit_claimed": False,
    }

