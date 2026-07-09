"""Final-materialized input binding shared by section X2 and X3 gates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

FINAL_MATERIALIZED_INPUT_BINDING_SCHEMA = "apps_rg.final_materialized_input_binding.v1"


def canonical_json_for_digest(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_text(canonical_json_for_digest(value))


def _load_json(path: Path) -> dict[str, Any]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return doc if isinstance(doc, dict) else {}


def _load_json_any(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def resolve_final_materialized_text(artifact_dir: Path) -> tuple[str, str]:
    """Resolve the final display artifact used by the lane, independent of raw provider text."""
    command_output = artifact_dir / "command_output.txt"
    if command_output.is_file():
        text = _load_text(command_output).strip()
        if text:
            return text, command_output.name
    output_candidates = sorted(
        p for p in artifact_dir.glob("*_output.txt") if p.is_file()
    )
    for path in output_candidates:
        text = _load_text(path).strip()
        if text:
            return text, path.name
    l2 = _load_json(artifact_dir / "l2_output.json")
    for key in (
        "resume_display_text",
        "headline_line",
        "narrative_sentence",
        "summary_text",
    ):
        text = str(l2.get(key) or "").strip()
        if text:
            return text, "l2_output.json"
    bullets = l2.get("bullets")
    if isinstance(bullets, list) and bullets:
        lines = [
            str(row.get("bullet_text") or "").strip()
            for row in bullets
            if isinstance(row, dict) and str(row.get("bullet_text") or "").strip()
        ]
        if lines:
            return "\n".join(f"- {line}" for line in lines), "l2_output.json"
    competencies = l2.get("competencies")
    if isinstance(competencies, list) and competencies:
        labels = [
            str(row.get("label") or row.get("category") or "").strip()
            for row in competencies
            if isinstance(row, dict) and str(row.get("label") or row.get("category") or "").strip()
        ]
        if labels:
            return "\n".join(labels), "l2_output.json"
    return "", ""


def final_claim_ledger_rows(artifact_dir: Path) -> list[dict[str, Any]]:
    doc = _load_json_any(artifact_dir / "claim_ledger.json")
    if isinstance(doc, list):
        return [dict(r) for r in doc if isinstance(r, dict)]
    l2 = _load_json(artifact_dir / "l2_output.json")
    rows = l2.get("claim_ledger")
    if isinstance(rows, list):
        return [dict(r) for r in rows if isinstance(r, dict)]
    return []


def build_final_materialized_input_binding(
    artifact_dir: Path,
    *,
    section_id: str,
) -> dict[str, Any]:
    """Digest-bind the final display text, L2 output, and claim ledger used by X2."""
    output_text, output_ref = resolve_final_materialized_text(artifact_dir)
    l2_output = _load_json(artifact_dir / "l2_output.json")
    claim_ledger = final_claim_ledger_rows(artifact_dir)
    return {
        "schema_version": FINAL_MATERIALIZED_INPUT_BINDING_SCHEMA,
        "section_id": str(section_id or "").strip(),
        "final_materialized_output_ref": output_ref,
        "final_materialized_output_present": bool(output_text.strip()),
        "final_materialized_output_char_count": len(output_text),
        "final_materialized_output_sha256": sha256_text(output_text) if output_text else "",
        "l2_output_present": (artifact_dir / "l2_output.json").is_file(),
        "l2_output_sha256": sha256_json(l2_output) if l2_output else "",
        "final_claim_ledger_present": bool(claim_ledger),
        "final_claim_ledger_row_count": len(claim_ledger),
        "final_claim_ledger_sha256": sha256_json(claim_ledger) if claim_ledger else "",
    }


def augment_x2_payload_with_final_materialized_binding(
    payload: dict[str, Any],
    *,
    artifact_dir: Path,
    section_id: str,
) -> dict[str, Any]:
    out = dict(payload)
    binding = build_final_materialized_input_binding(artifact_dir, section_id=section_id)
    out["final_materialized_input_binding"] = binding
    out["final_materialized_output_sha256"] = binding["final_materialized_output_sha256"]
    out["final_claim_ledger_sha256"] = binding["final_claim_ledger_sha256"]
    out["l2_output_sha256"] = binding["l2_output_sha256"]
    return out


def validate_final_materialized_input_binding(
    binding: dict[str, Any] | None,
    *,
    artifact_dir: Path,
    section_id: str,
) -> tuple[bool, list[str], dict[str, Any]]:
    current = build_final_materialized_input_binding(artifact_dir, section_id=section_id)
    if not isinstance(binding, dict) or not binding:
        return False, ["x2_final_materialized_binding_missing"], current
    failures: list[str] = []
    schema = str(binding.get("schema_version") or "").strip()
    if schema != FINAL_MATERIALIZED_INPUT_BINDING_SCHEMA:
        failures.append("x2_final_materialized_binding_schema_mismatch")
    bound_section = str(binding.get("section_id") or "").strip()
    if bound_section and bound_section != str(section_id or "").strip():
        failures.append("x2_final_materialized_binding_section_mismatch")
    for key in (
        "final_materialized_output_sha256",
        "final_claim_ledger_sha256",
    ):
        if str(binding.get(key) or "") != str(current.get(key) or ""):
            failures.append(f"x2_final_materialized_binding_{key}_mismatch")
    return not failures, failures, current


__all__ = [
    "FINAL_MATERIALIZED_INPUT_BINDING_SCHEMA",
    "augment_x2_payload_with_final_materialized_binding",
    "build_final_materialized_input_binding",
    "canonical_json_for_digest",
    "final_claim_ledger_rows",
    "resolve_final_materialized_text",
    "sha256_json",
    "sha256_text",
    "validate_final_materialized_input_binding",
]
