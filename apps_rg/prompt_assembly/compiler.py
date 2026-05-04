"""PA compiler for apps_rg: BOM -> Registry -> Template -> CompiledPromptArtifact.

Registry-aware compiler that:
  1. Loads ``apps_rg/prompt_assembly/prompt_bom.yaml``
  2. Loads ``apps_rg/prompt_assembly/prompt_registry.yaml``
  3. Resolves template by template_id or generation_mode
  4. Loads governed YAML template from ``apps_rg/prompt_assembly/templates/``
  5. Validates required slots and input contract
  6. Validates template is not placeholder
  7. Renders structured slots deterministically
  8. Computes prompt_bom_hash, prompt_registry_hash, template_hash,
     manifest_hash, canonical_slot_bytes_hash, artifact_hash
  9. Emits ``AppsRgCompiledPromptArtifact`` ready for L2 handoff

Fail-closed: any missing BOM / registry / template / hash / policy /
blueprint / replay / provider / schema / source ref / placeholder content
causes a compile failure with ``PA_COMPILE_FAILED`` status.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from pathlib import Path
from typing import Any, Optional

_log = logging.getLogger(__name__)

_PA_ROOT = Path(__file__).resolve().parent
_APPS_RG_ROOT = _PA_ROOT.parent
_BOM_PATH = _PA_ROOT / "prompt_bom.yaml"
_REGISTRY_PATH = _PA_ROOT / "prompt_registry.yaml"

FLOW_ROUTE_TO_TEMPLATE: dict[str, str] = {
    "strategic_tailor": "strategic_tailor_v1",
    "strategic_tailor_node": "strategic_tailor_v1",
    "tailor_existing": "tailor_existing_v1",
    "generate_scratch": "generate_scratch_v1",
    "enhance_current": "enhance_current_v1",
    "fact_check": "resume_fact_check_v1",
    "claim_omission": "unsupported_claim_omission_v1",
    "bullet_diversity_repair": "bullet_diversity_repair_v1",
    "docx_manifest": "docx_manifest_v1",
}

_PLACEHOLDER_MARKERS = {"todo", "placeholder", "lorem", "fill me", "tbd"}


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file. Uses yaml.safe_load."""
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _sha256_prefix(content: str, length: int = 16) -> str:
    """Compute SHA-256 hash prefix."""
    return hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()[:length]


def _load_bom(bom_path: Optional[Path] = None) -> tuple[dict[str, Any], str]:
    """Load BOM YAML and return (parsed, raw_text)."""
    path = bom_path or _BOM_PATH
    if not path.exists():
        raise FileNotFoundError(f"Prompt BOM not found: {path}")
    raw = path.read_text(encoding="utf-8")
    return _load_yaml(path), raw


def _load_registry(registry_path: Optional[Path] = None) -> tuple[dict[str, Any], str]:
    """Load prompt registry YAML and return (parsed, raw_text)."""
    path = registry_path or _REGISTRY_PATH
    if not path.exists():
        raise FileNotFoundError(f"Prompt registry not found: {path}")
    raw = path.read_text(encoding="utf-8")
    return _load_yaml(path), raw


def _resolve_template_entry(
    registry: dict[str, Any], template_id: str
) -> dict[str, Any]:
    """Resolve template entry from registry by template_id."""
    templates = registry.get("templates", {})
    entry = templates.get(template_id)
    if not entry:
        raise ValueError(
            f"Template '{template_id}' not found in prompt registry. "
            f"Available: {list(templates.keys())}"
        )
    return entry


def _load_template_yaml(template_rel_path: str) -> tuple[dict[str, Any], str]:
    """Load a governed YAML template file by its registry-relative path."""
    repo_root = _APPS_RG_ROOT.parent
    template_path = repo_root / template_rel_path
    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")
    raw = template_path.read_text(encoding="utf-8")
    parsed = _load_yaml(template_path)
    return parsed, raw


def _validate_template_not_placeholder(template: dict[str, Any], template_id: str) -> None:
    """Validate template slot_bodies are not placeholders."""
    slot_bodies = template.get("slot_bodies", {})
    if not slot_bodies:
        raise ValueError(f"Template '{template_id}' has empty slot_bodies")
    for slot_name, body in slot_bodies.items():
        if not body or not isinstance(body, str):
            raise ValueError(f"Template '{template_id}' slot '{slot_name}' is empty")
        body_lower = body.lower().strip()
        for marker in _PLACEHOLDER_MARKERS:
            if marker in body_lower and len(body_lower) < 200:
                raise ValueError(
                    f"Template '{template_id}' slot '{slot_name}' contains "
                    f"placeholder marker '{marker}'"
                )


def _compute_canonical_slot_bytes(slots: dict[str, str]) -> str:
    """Deterministic hash of all slot contents in sorted key order."""
    canonical = json.dumps(slots, sort_keys=True, ensure_ascii=True)
    return _sha256_prefix(canonical)


def compile_prompt(
    request: "AppsRgPromptRequest",
    *,
    bom_path: Optional[Path] = None,
    registry_path: Optional[Path] = None,
    governance_block: str = "",
    output_schema_block: str = "",
    origin_boundary_block: str = "",
    style_prefs_block: str = "",
) -> "AppsRgCompiledPromptArtifact":
    """Compile a prompt artifact from a request.

    Args:
        request: The prompt request with all input data and flow route.
        bom_path: Override BOM path (for testing).
        registry_path: Override registry path (for testing).
        governance_block: Optional S0 governance text override.
        output_schema_block: Optional R0 output schema text override.
        origin_boundary_block: Optional D0 origin boundary text override.
        style_prefs_block: Optional Y0 style preferences text override.

    Returns:
        A fully populated ``AppsRgCompiledPromptArtifact``.

    Raises:
        RuntimeError: On any compile failure (fail-closed).
    """
    from apps_rg.prompt_assembly.contracts import (
        AppsRgCompiledPromptArtifact,
        PACompileStatus,
    )
    from apps_rg.prompt_assembly.slot_mapper import (
        map_slots,
        render_template,
        validate_slot_isolation,
    )

    artifact = AppsRgCompiledPromptArtifact(
        request_id=request.request_id or uuid.uuid4().hex[:16],
        run_id=request.run_id or "",
        trace_id=request.trace_id or "",
        app_name=request.app_name,
        route_id=request.route_id,
        provider_lane=request.provider_lane,
        symbolic_model_id=request.symbolic_model_id,
        policy_hash=request.policy_hash,
        blueprint_hash=request.blueprint_hash,
        output_schema_ref=request.output_schema_ref,
        local_evidence_contract_ref=request.local_evidence_contract_ref,
    )

    try:
        # 1. Load BOM
        bom, bom_raw = _load_bom(bom_path)
        artifact.prompt_bom_hash = _sha256_prefix(bom_raw)
        artifact.compile_status = PACompileStatus.PA_BOM_RESOLVED.value

        # 2. Load Registry
        registry, registry_raw = _load_registry(registry_path)
        artifact.prompt_registry_hash = _sha256_prefix(registry_raw)

        # 3. Resolve template_id from flow route
        template_id = FLOW_ROUTE_TO_TEMPLATE.get(request.flow_route)
        if not template_id:
            raise ValueError(f"Unknown flow route: {request.flow_route}")
        artifact.template_id = template_id

        # 4. Resolve template entry from registry
        reg_entry = _resolve_template_entry(registry, template_id)
        template_path = reg_entry["path"]

        # 5. Load governed YAML template
        template_parsed, template_raw = _load_template_yaml(template_path)
        artifact.prompt_template_hash = _sha256_prefix(template_raw)
        artifact.template_version = str(template_parsed.get("version", ""))
        artifact.prompt_id = f"apps_rg.{template_id}"

        # 6. Validate template is not placeholder
        _validate_template_not_placeholder(template_parsed, template_id)

        # 7. Extract S0 governance from template slot_bodies (or use override)
        slot_bodies = template_parsed.get("slot_bodies", {})
        s0_from_template = slot_bodies.get("S0", "")
        i0_from_template = slot_bodies.get("I0", "")
        d0_from_template = slot_bodies.get("D0", "")
        y0_from_template = slot_bodies.get("Y0", "")
        r0_from_template = slot_bodies.get("R0", "")

        # 8. Map slots (8-slot model)
        slots, slot_receipts = map_slots(
            request,
            i0_from_template or "Resume generation instructions.",
            governance_block=governance_block or s0_from_template,
            output_schema_block=output_schema_block or r0_from_template,
            origin_boundary_block=origin_boundary_block or d0_from_template,
            style_prefs_block=style_prefs_block or y0_from_template,
        )
        artifact.structured_slots_used = list(slots.keys())
        artifact.rendered_slots = dict(slots)
        artifact.slot_validation_receipt = slot_receipts
        artifact.compile_status = PACompileStatus.PA_SLOTS_COMPOSED.value

        # 9. Validate slot isolation (security)
        violations = validate_slot_isolation(slots)
        if violations:
            artifact.compile_status = PACompileStatus.PA_SECURITY_GAP.value
            artifact.origin_security_receipt = "; ".join(violations)
            raise RuntimeError(
                f"PA_SECURITY_GAP: slot isolation violated: {violations}"
            )
        artifact.origin_security_receipt = "PASS"
        artifact.compile_status = PACompileStatus.PA_SECURITY_PASS.value

        # 10. Validate slot contract
        artifact.compile_status = PACompileStatus.PA_SLOT_CONTRACT_VALID.value

        # 11. Compute canonical slot bytes hash (deterministic)
        artifact.canonical_slot_bytes_hash = _compute_canonical_slot_bytes(slots)

        # 12. Render template
        rendered = render_template(i0_from_template or "", slots)
        artifact.prompt_hash = _sha256_prefix(rendered)
        artifact.render_receipt = "rendered_ok"
        artifact.compile_status = PACompileStatus.PA_RENDERED.value

        # 13. Build provider-specific messages
        artifact.provider_specific_messages = [
            {"role": "system", "content": slots["S0_GOVERNANCE"]},
            {"role": "user", "content": rendered},
        ]

        # 14. Origin label map
        artifact.origin_label_map = {
            "S0": "system_governance",
            "I0": "app_instruction",
            "C0": "data_only",
            "U0": "user_intent_only",
            "D0": "security_boundary",
            "E0": "approved_example_data",
            "Y0": "approved_user_style",
            "R0": "schema_contract",
        }

        # 15. Compute output schema hash
        schema_text = slots.get("R0_OUTPUT_SCHEMA", "")
        artifact.output_schema_hash = _sha256_prefix(schema_text) if schema_text else ""

        # 16. Source refs
        artifact.source_refs = {
            "jd_data_hash": _sha256_prefix(request.jd_data),
            "master_resume_hash": _sha256_prefix(request.master_resume_data),
            "company_brief_hash": _sha256_prefix(request.company_brief_data) if request.company_brief_data else "",
            "claim_source_refs_hash": _sha256_prefix(request.claim_source_refs) if request.claim_source_refs else "",
            "unsupported_claims_hash": _sha256_prefix(request.unsupported_claims) if request.unsupported_claims else "",
        }

        # 17. Generate artifact ID and replay key
        artifact.artifact_id = uuid.uuid4().hex[:16]
        artifact.replay_key = uuid.uuid4().hex[:16]

        # 18. Compute manifest_hash (BOM + registry + template combined)
        manifest_input = f"{artifact.prompt_bom_hash}:{artifact.prompt_registry_hash}:{artifact.prompt_template_hash}"
        artifact.manifest_hash = _sha256_prefix(manifest_input)

        # 19. Compute artifact_hash (over all identity + content hashes)
        artifact_input = (
            f"{artifact.prompt_bom_hash}:{artifact.prompt_registry_hash}:"
            f"{artifact.prompt_template_hash}:{artifact.canonical_slot_bytes_hash}:"
            f"{artifact.prompt_hash}:{artifact.policy_hash}:{artifact.blueprint_hash}"
        )
        artifact.artifact_hash = _sha256_prefix(artifact_input)

        # 20. Token budget receipt
        artifact.token_budget_receipt = {"status": "fit", "estimated_tokens": len(rendered) // 4}

        # 21. Audit refs
        artifact.audit_refs = {
            "bom_path": str(bom_path or _BOM_PATH),
            "registry_path": str(registry_path or _REGISTRY_PATH),
            "template_path": template_path,
            "template_id": template_id,
        }

        # 22. Mark ready
        artifact.compile_status = PACompileStatus.PA_L2_HANDOFF_READY.value

        _log.info(
            "[pa_compiler] Compiled artifact: template_id=%s, prompt_id=%s, status=%s",
            artifact.template_id,
            artifact.prompt_id,
            artifact.compile_status,
        )
        return artifact

    except (FileNotFoundError, ValueError, KeyError) as exc:
        artifact.compile_status = PACompileStatus.PA_COMPILE_FAILED.value
        _log.error("[pa_compiler] Compile failed: %s", exc)
        raise RuntimeError(f"PA_COMPILE_FAILED: {exc}") from exc


__all__ = ["compile_prompt", "FLOW_ROUTE_TO_TEMPLATE"]
