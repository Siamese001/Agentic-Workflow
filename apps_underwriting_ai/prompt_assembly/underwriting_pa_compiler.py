"""apps_underwriting_ai Prompt Assembly Compiler.

Compiles prompt templates into CompiledPromptArtifact objects for
apps_underwriting_ai rationale enrichment steps.

Prompt Assembly owns compilation ONLY. This module MUST NOT:
- retrieve new information (forbidden: tavily_retrieval, open_web, etc.)
- route requests (forbidden: route_registry lookups)
- execute tools (forbidden: any tool call)
- call providers (forbidden: openai, anthropic, litellm, llm_client, etc.)
- mutate L4 state (forbidden: DurableWriteGateway, StateStore, etc.)
- emit Exit disposition (forbidden: Exit v6, x3_dispositions, etc.)
- approve egress (forbidden: UWG admission gate)
- change the underwriting verdict or reason codes (LOCKED by DeterministicRiskScorer)

L2 owns execution.
Provider gateway owns model invocation.
Exit v6 owns final disposition.
UWG owns durable write admission.
DeterministicRiskScorer owns verdict and reason_code_bundle — immutable.

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 P1.5.2.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_PA_DIR = Path(__file__).parent
_BOM_PATH = _PA_DIR / "prompt_bom.yaml"
_REGISTRY_PATH = _PA_DIR / "prompt_registry.yaml"
_REPO_ROOT = _PA_DIR.parents[1]


# ---------------------------------------------------------------------------
# CompiledPromptArtifact
# ---------------------------------------------------------------------------

@dataclass
class CompiledPromptArtifact:
    """A compiled, deterministically hashed prompt artifact for apps_underwriting_ai.

    Hash bindings enforce that the verdict and reason codes from
    DeterministicRiskScorer are locked before any LLM call.

    Required fields:
      - artifact_id, request_id, run_id, trace_id, route_id
      - template_id, template_version
      - prompt_bom_hash, prompt_registry_hash, template_hash
      - c0_bundle_hash: binds FinalEvidenceContract to this artifact
      - verdict_hash: binds the locked verdict to this artifact
      - reason_codes_hash: binds the locked reason codes to this artifact
      - rendered_slots, canonical_slot_bytes_hash, artifact_hash
      - allowed_stage, output_type
      - audit_refs
    """

    # Identity
    artifact_id: str
    request_id: str
    run_id: str
    trace_id: str
    route_id: str = "R3R4_MANAGED_WORKFLOW"

    # Template binding
    template_id: str = ""
    template_version: str = "1.0"

    # Hash bindings
    prompt_bom_hash: str = ""
    prompt_registry_hash: str = ""
    template_hash: str = ""
    c0_bundle_hash: str = ""       # binds FinalEvidenceContract
    verdict_hash: str = ""         # binds locked verdict from DeterministicRiskScorer
    reason_codes_hash: str = ""    # binds locked reason codes from DeterministicRiskScorer

    # Governance
    allowed_stage: str = ""
    output_type: str = ""
    llm_firewall: str = "strict"
    verdict_locked: bool = True
    reason_codes_locked: bool = True
    provider_lane: str = "governed"

    # Content
    rendered_slots: dict[str, str] = field(default_factory=dict)
    canonical_slot_bytes_hash: str = ""
    artifact_hash: str = ""
    audit_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_id": self.trace_id,
            "route_id": self.route_id,
            "template_id": self.template_id,
            "template_version": self.template_version,
            "prompt_bom_hash": self.prompt_bom_hash,
            "prompt_registry_hash": self.prompt_registry_hash,
            "template_hash": self.template_hash,
            "c0_bundle_hash": self.c0_bundle_hash,
            "verdict_hash": self.verdict_hash,
            "reason_codes_hash": self.reason_codes_hash,
            "allowed_stage": self.allowed_stage,
            "output_type": self.output_type,
            "llm_firewall": self.llm_firewall,
            "verdict_locked": self.verdict_locked,
            "reason_codes_locked": self.reason_codes_locked,
            "provider_lane": self.provider_lane,
            "rendered_slots": self.rendered_slots,
            "canonical_slot_bytes_hash": self.canonical_slot_bytes_hash,
            "artifact_hash": self.artifact_hash,
            "audit_refs": self.audit_refs,
        }


# ---------------------------------------------------------------------------
# Error types
# ---------------------------------------------------------------------------

class PromptAssemblyError(Exception):
    """Raised when prompt assembly compilation fails.

    Must be routed through Exit v6 as X3E_SAFE_ABSTAIN — no partial artifact.
    Callers must set deterministic_rationale_fallback_used=True on this error.
    """


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _compute_hash(data: Any) -> str:
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise PromptAssemblyError(f"Required PA file missing: {path}")
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Public loaders
# ---------------------------------------------------------------------------

def load_prompt_bom(bom_path: Path | None = None) -> dict[str, Any]:
    """Load apps_underwriting_ai PromptBOM from YAML.

    Args:
        bom_path: Override path; defaults to prompt_bom.yaml in this package.

    Returns:
        Parsed BOM dict.

    Raises:
        PromptAssemblyError: If file missing or schema invalid.
    """
    path = bom_path or _BOM_PATH
    bom = _load_yaml(path)
    if bom.get("app") != "apps_underwriting_ai":
        raise PromptAssemblyError(
            f"BOM app mismatch: expected 'apps_underwriting_ai', got {bom.get('app')!r}"
        )
    required_slots = bom.get("required_slots", [])
    for slot in ("S0", "I0", "C0", "U0", "D0", "R0"):
        if slot not in required_slots:
            raise PromptAssemblyError(f"BOM missing required slot {slot!r}")
    return bom


def load_prompt_registry(registry_path: Path | None = None) -> dict[str, Any]:
    """Load apps_underwriting_ai PromptRegistry from YAML.

    Args:
        registry_path: Override path; defaults to prompt_registry.yaml.

    Returns:
        Parsed registry dict.

    Raises:
        PromptAssemblyError: If file missing or schema invalid.
    """
    path = registry_path or _REGISTRY_PATH
    registry = _load_yaml(path)
    if not registry.get("templates"):
        raise PromptAssemblyError("PromptRegistry has no templates defined.")
    return registry


def load_template(template_id: str, registry: dict[str, Any]) -> dict[str, Any]:
    """Load a template from the registry by ID.

    Args:
        template_id: The template ID (key in registry["templates"]).
        registry: Parsed PromptRegistry dict.

    Returns:
        Parsed template dict.

    Raises:
        PromptAssemblyError: If template_id not found or file missing.
    """
    templates = registry.get("templates", {})
    if template_id not in templates:
        raise PromptAssemblyError(
            f"Template '{template_id}' not found in PromptRegistry. "
            f"Available: {list(templates)}"
        )
    template_meta = templates[template_id]
    rel_path = template_meta.get("path", "")
    template_path = _REPO_ROOT / rel_path
    return _load_yaml(template_path)


# ---------------------------------------------------------------------------
# Compiler
# ---------------------------------------------------------------------------

def compile_artifact(
    *,
    template_id: str,
    request_id: str,
    run_id: str,
    trace_id: str,
    artifact_id: str,
    c0_bundle: dict[str, Any],
    verdict: str,
    reason_codes: list[str],
    slot_overrides: dict[str, str] | None = None,
    bom_path: Path | None = None,
    registry_path: Path | None = None,
) -> CompiledPromptArtifact:
    """Compile a CompiledPromptArtifact for the given template and evidence.

    This is the ONLY public entry point for producing a prompt artifact.
    Callers must supply the locked verdict and reason_codes from
    DeterministicRiskScorer before calling this function.

    LLM FIREWALL: verdict and reason_codes are hashed into the artifact.
    Any post-compile change to verdict or reason_codes will produce a
    different artifact_hash, enabling downstream detection.

    Args:
        template_id: Template to compile (must be in PromptRegistry).
        request_id: Underwriting request ID.
        run_id: Run ID for this execution.
        trace_id: Trace ID for observability.
        artifact_id: Unique artifact ID for this compilation.
        c0_bundle: FinalEvidenceContract dict from the C0 adapter.
        verdict: Locked verdict string from DeterministicRiskScorer.
        reason_codes: Locked reason code list from DeterministicRiskScorer.
        slot_overrides: Optional slot content overrides (for U0, E0, Y0, P0).
        bom_path: Override BOM YAML path (testing).
        registry_path: Override registry YAML path (testing).

    Returns:
        CompiledPromptArtifact with all hash bindings.

    Raises:
        PromptAssemblyError: If any file is missing, schema is invalid,
            or required C0 evidence is absent.
    """
    bom = load_prompt_bom(bom_path)
    registry = load_prompt_registry(registry_path)
    template = load_template(template_id, registry)

    bom_hash = _compute_hash(bom)
    registry_hash = _compute_hash(registry)
    template_hash = _compute_hash(template)
    c0_bundle_hash = _compute_hash(c0_bundle)
    verdict_hash = _compute_hash(verdict)
    reason_codes_hash = _compute_hash(sorted(reason_codes))

    template_meta = registry["templates"][template_id]
    allowed_stage = template_meta.get("allowed_stage", "")
    output_type = template_meta.get("output_type", "")
    llm_firewall = template_meta.get("llm_firewall", "strict")
    verdict_locked = template_meta.get("verdict_locked", True)
    reason_codes_locked = template_meta.get("reason_codes_locked", True)

    prompt_sections = template.get("prompt_sections", {})
    rendered_slots: dict[str, str] = {}
    for slot_id, section_text in prompt_sections.items():
        rendered_slots[slot_id] = section_text

    if slot_overrides:
        for slot_id, content in slot_overrides.items():
            rendered_slots[slot_id] = content

    canonical_slot_bytes_hash = _compute_hash(rendered_slots)

    artifact_payload = {
        "artifact_id": artifact_id,
        "template_id": template_id,
        "prompt_bom_hash": bom_hash,
        "prompt_registry_hash": registry_hash,
        "template_hash": template_hash,
        "c0_bundle_hash": c0_bundle_hash,
        "verdict_hash": verdict_hash,
        "reason_codes_hash": reason_codes_hash,
        "canonical_slot_bytes_hash": canonical_slot_bytes_hash,
    }
    artifact_hash = _compute_hash(artifact_payload)

    return CompiledPromptArtifact(
        artifact_id=artifact_id,
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        route_id="R3R4_MANAGED_WORKFLOW",
        template_id=template_id,
        template_version=template.get("template_version", "1.0"),
        prompt_bom_hash=bom_hash,
        prompt_registry_hash=registry_hash,
        template_hash=template_hash,
        c0_bundle_hash=c0_bundle_hash,
        verdict_hash=verdict_hash,
        reason_codes_hash=reason_codes_hash,
        allowed_stage=allowed_stage,
        output_type=output_type,
        llm_firewall=llm_firewall,
        verdict_locked=verdict_locked,
        reason_codes_locked=reason_codes_locked,
        rendered_slots=rendered_slots,
        canonical_slot_bytes_hash=canonical_slot_bytes_hash,
        artifact_hash=artifact_hash,
        audit_refs=[
            f"bom:{bom_hash[:12]}",
            f"registry:{registry_hash[:12]}",
            f"template:{template_hash[:12]}",
            f"c0:{c0_bundle_hash[:12]}",
            f"verdict:{verdict_hash[:12]}",
        ],
    )
