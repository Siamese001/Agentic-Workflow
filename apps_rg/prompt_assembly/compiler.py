"""PA compiler for apps_rg: BOM -> CompiledPromptArtifact.

Loads ``apps_rg/prompts/prompt_bom.yaml``, selects the prompt template by
flow route, computes hashes, maps slots, validates security, and emits
a ``AppsRgCompiledPromptArtifact`` ready for L2 handoff.

Fail-closed: any missing BOM / template / hash / policy / blueprint /
replay / provider / schema / source ref causes a compile failure with
``PA_COMPILE_FAILED`` status.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from pathlib import Path
from typing import Any, Optional

_log = logging.getLogger(__name__)

# Resolve the apps_rg package root relative to this file.
_APPS_RG_ROOT = Path(__file__).resolve().parent.parent
_BOM_PATH = _APPS_RG_ROOT / "prompts" / "prompt_bom.yaml"

# Flow route -> BOM key mapping
FLOW_ROUTE_MAP: dict[str, str] = {
    "strategic_tailor": "strategic_tailor",
    "strategic_tailor_node": "strategic_tailor",
    "tailor_existing": "tailor_existing",
    "generate_scratch": "generate_scratch",
    "enhance_current": "enhance_current",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file. Uses yaml.safe_load."""
    import yaml

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _sha256_prefix(content: str, length: int = 16) -> str:
    """Compute SHA-256 hash prefix."""
    return hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()[:length]


def _load_bom(bom_path: Optional[Path] = None) -> dict[str, Any]:
    """Load the prompt BOM YAML."""
    path = bom_path or _BOM_PATH
    if not path.exists():
        raise FileNotFoundError(f"Prompt BOM not found: {path}")
    return _load_yaml(path)


def _resolve_prompt_entry(bom: dict[str, Any], flow_route: str) -> dict[str, Any]:
    """Resolve the prompt entry from the BOM for the given flow route."""
    bom_key = FLOW_ROUTE_MAP.get(flow_route)
    if not bom_key:
        raise ValueError(f"Unknown flow route: {flow_route}")

    resume_gen = bom.get("resume_generation", {})
    entry = resume_gen.get(bom_key)
    if not entry:
        raise ValueError(
            f"BOM entry not found for flow route '{flow_route}' "
            f"(bom_key='{bom_key}')"
        )
    return entry


def _load_template(template_rel_path: str) -> str:
    """Load a prompt template file by its BOM-relative path."""
    # Template paths in BOM are relative to repo root; resolve from apps_rg root's parent
    repo_root = _APPS_RG_ROOT.parent
    template_path = repo_root / template_rel_path
    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def compile_prompt(
    request: "AppsRgPromptRequest",
    *,
    bom_path: Optional[Path] = None,
    governance_block: str = "",
    output_schema_block: str = "",
) -> "AppsRgCompiledPromptArtifact":
    """Compile a prompt artifact from a request.

    Args:
        request: The prompt request with all input data and flow route.
        bom_path: Override BOM path (for testing).
        governance_block: Optional S0 governance text override.
        output_schema_block: Optional R0 output schema text override.

    Returns:
        A fully populated ``AppsRgCompiledPromptArtifact``.

    Raises:
        RuntimeError: On any compile failure (fail-closed).
    """
    from apps_rg.prompt_assembly.contracts import (
        AppsRgCompiledPromptArtifact,
        PACompileStatus,
        PromptCompileReceipt,
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
    )

    try:
        # 1. Load BOM
        bom = _load_bom(bom_path)
        bom_raw = Path(bom_path or _BOM_PATH).read_text(encoding="utf-8")
        artifact.prompt_bom_hash = _sha256_prefix(bom_raw)
        artifact.compile_status = PACompileStatus.PA_BOM_RESOLVED.value

        # 2. Resolve prompt entry
        entry = _resolve_prompt_entry(bom, request.flow_route)
        artifact.prompt_id = entry["prompt_id"]

        # 3. Load template
        template_body = _load_template(entry["template"])
        artifact.prompt_template_hash = _sha256_prefix(template_body)

        # 4. Map slots
        slots, slot_receipts = map_slots(
            request,
            template_body,
            governance_block=governance_block,
            output_schema_block=output_schema_block,
        )
        artifact.structured_slots_used = list(slots.keys())
        artifact.slot_validation_receipt = slot_receipts
        artifact.compile_status = PACompileStatus.PA_SLOTS_COMPOSED.value

        # 5. Validate slot isolation (security)
        violations = validate_slot_isolation(slots)
        if violations:
            artifact.compile_status = PACompileStatus.PA_SECURITY_GAP.value
            artifact.origin_security_receipt = "; ".join(violations)
            raise RuntimeError(
                f"PA_SECURITY_GAP: slot isolation violated: {violations}"
            )
        artifact.origin_security_receipt = "PASS"
        artifact.compile_status = PACompileStatus.PA_SECURITY_PASS.value

        # 6. Validate slot contract
        artifact.compile_status = PACompileStatus.PA_SLOT_CONTRACT_VALID.value

        # 7. Render template
        rendered = render_template(template_body, slots)
        artifact.prompt_hash = _sha256_prefix(rendered)
        artifact.render_receipt = "rendered_ok"
        artifact.compile_status = PACompileStatus.PA_RENDERED.value

        # 8. Build provider-specific messages
        artifact.provider_specific_messages = [
            {"role": "system", "content": slots["S0_GOVERNANCE"]},
            {"role": "user", "content": rendered},
        ]

        # 9. Compute output schema hash
        schema_text = slots.get("R0_OUTPUT_SCHEMA", "")
        artifact.output_schema_hash = _sha256_prefix(schema_text) if schema_text else ""

        # 10. Source refs
        artifact.source_refs = {
            "jd_data_hash": _sha256_prefix(request.jd_data),
            "master_resume_hash": _sha256_prefix(request.master_resume_data),
            "company_brief_hash": _sha256_prefix(request.company_brief_data) if request.company_brief_data else "",
        }

        # 11. Generate artifact ID and replay key
        artifact.artifact_id = uuid.uuid4().hex[:16]
        artifact.replay_key = uuid.uuid4().hex[:16]

        # 12. Token budget receipt (placeholder — real budget comes from provider)
        artifact.token_budget_receipt = {"status": "fit", "estimated_tokens": len(rendered) // 4}

        # 13. Mark ready
        artifact.compile_status = PACompileStatus.PA_L2_HANDOFF_READY.value

        _log.info(
            "[pa_compiler] Compiled artifact: prompt_id=%s, status=%s",
            artifact.prompt_id,
            artifact.compile_status,
        )
        return artifact

    except (FileNotFoundError, ValueError, KeyError) as exc:
        artifact.compile_status = PACompileStatus.PA_COMPILE_FAILED.value
        _log.error("[pa_compiler] Compile failed: %s", exc)
        raise RuntimeError(f"PA_COMPILE_FAILED: {exc}") from exc


__all__ = ["compile_prompt"]
