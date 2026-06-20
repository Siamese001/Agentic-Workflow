"""apps_research Prompt Assembly Compiler.

Compiles prompt templates into CompiledPromptArtifact objects for
apps_research synthesis steps.

Prompt Assembly owns compilation ONLY. This module MUST NOT:
- retrieve new information (forbidden: tavily_retrieval, reranker_adapter, etc.)
- route requests (forbidden: route_registry lookups)
- execute tools (forbidden: any tool call)
- call providers (forbidden: openai, anthropic, llm_client, etc.)
- mutate L4 state (forbidden: research_brief_uwg_writer, DurableWriteGateway, etc.)
- emit Exit disposition (forbidden: Exit v6, x3_dispositions, etc.)
- approve egress (forbidden: UWG admission gate)
- approve writes (forbidden: CommitRequest, StateStore, etc.)

L2 owns execution.
Provider gateway (llm_client.py) owns model invocation.
Exit v6 owns final disposition.
UWG (research_brief_uwg_writer.py) owns durable write admission.

Plan: apps-research-spine-alignment-d4e8f2 P1.5.
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
    """A compiled, deterministically hashed prompt artifact for apps_research.

    Required fields per plan specification (apps-research-spine-alignment-d4e8f2 P1.5):
      - artifact_id, request_id, run_id, trace_id, route_id
      - template_id, template_version
      - prompt_bom_hash, prompt_registry_hash, template_hash
      - c0_bundle_hash (binds C0 evidence to this artifact)
      - rendered_slots, canonical_slot_bytes_hash, artifact_hash
      - depth_profile, allowed_stage
      - audit_refs
    """

    # Identity
    artifact_id: str
    request_id: str
    run_id: str
    trace_id: str
    route_id: str = "R3_SIMPLE_GROUNDED_READ"

    # Template binding
    template_id: str = ""
    template_version: str = "1.0"

    # Hash bindings
    prompt_bom_hash: str = ""
    prompt_registry_hash: str = ""
    template_hash: str = ""
    c0_bundle_hash: str = ""  # binds C0 evidence — absent in apps_lic; required here

    # Governance
    depth_profile: str = ""
    allowed_stage: str = ""
    output_schema_ref: str = ""
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
            "depth_profile": self.depth_profile,
            "allowed_stage": self.allowed_stage,
            "output_schema_ref": self.output_schema_ref,
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
    """Load apps_research PromptBOM from YAML.

    Args:
        bom_path: Override path; defaults to prompt_bom.yaml in this package.

    Returns:
        Parsed BOM dict.

    Raises:
        PromptAssemblyError: If file missing or schema invalid.
    """
    path = bom_path or _BOM_PATH
    bom = _load_yaml(path)
    if bom.get("app") != "apps_research":
        raise PromptAssemblyError(
            f"PromptBOM app mismatch: expected 'apps_research', got '{bom.get('app')}'"
        )
    if not bom.get("required_slots"):
        raise PromptAssemblyError("PromptBOM missing 'required_slots'")
    return bom


def load_prompt_registry(registry_path: Path | None = None) -> dict[str, Any]:
    """Load apps_research prompt registry from YAML.

    Args:
        registry_path: Override path; defaults to prompt_registry.yaml in this package.

    Returns:
        Parsed registry dict.

    Raises:
        PromptAssemblyError: If file missing or schema invalid.
    """
    path = registry_path or _REGISTRY_PATH
    registry = _load_yaml(path)
    if not registry.get("templates"):
        raise PromptAssemblyError("Prompt registry missing 'templates' field")
    return registry


def load_template(template_id: str, registry: dict[str, Any]) -> dict[str, Any]:
    """Load a template from the registry by ID.

    Args:
        template_id: e.g. 'company_brief_synthesis_v1'
        registry: Loaded prompt registry.

    Returns:
        Template dict.

    Raises:
        PromptAssemblyError: If template not found or file missing.
    """
    templates = registry.get("templates", {})
    meta = templates.get(template_id)
    if meta is None:
        raise PromptAssemblyError(
            f"Template '{template_id}' not found in registry. "
            f"Available: {list(templates.keys())}"
        )
    # Resolve path relative to repo root
    raw_path = meta.get("path", "")
    template_path = _REPO_ROOT / raw_path
    if not template_path.exists():
        raise PromptAssemblyError(f"Template file not found: {template_path}")
    return _load_yaml(template_path)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_required_slots(
    template: dict[str, Any], bom: dict[str, Any]
) -> None:
    required = set(bom.get("required_slots", []))
    present_bodies = set(template.get("slot_bodies", {}).keys())
    missing = required - present_bodies
    if missing:
        raise PromptAssemblyError(
            f"Template '{template.get('template_id')}' missing slot bodies for: {missing}"
        )


def _validate_input_contract(
    template: dict[str, Any], input_data: dict[str, Any]
) -> None:
    required = template.get("input_contract", {}).get("required", [])
    missing = [f for f in required if f not in input_data]
    if missing:
        raise PromptAssemblyError(
            f"Template '{template.get('template_id')}' input missing required fields: {missing}"
        )


def _render_slots(
    template: dict[str, Any], input_data: dict[str, Any]
) -> dict[str, str]:
    slot_bodies = template.get("slot_bodies", {})
    rendered: dict[str, str] = {}
    for slot_id, body in slot_bodies.items():
        content = str(body)
        for key, value in input_data.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in content:
                content = content.replace(placeholder, str(value) if value is not None else "")
        rendered[slot_id] = content
    return rendered


# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------

def compute_bom_hash(bom: dict[str, Any]) -> str:
    hash_fields = bom.get("hash_fields", ["schema_version", "bom_id", "required_slots"])
    return _compute_hash({k: bom.get(k) for k in hash_fields})


def compute_registry_hash(registry: dict[str, Any]) -> str:
    hash_fields = registry.get("hash_fields", ["schema_version", "registry_id", "templates"])
    return _compute_hash({k: registry.get(k) for k in hash_fields})


def compute_template_hash(template: dict[str, Any]) -> str:
    hash_fields = template.get(
        "hash_fields", ["template_id", "version", "slot_bodies", "output_contract"]
    )
    return _compute_hash({k: template.get(k) for k in hash_fields})


# ---------------------------------------------------------------------------
# Primary compile entry point
# ---------------------------------------------------------------------------

def compile_prompt(
    template_id: str,
    input_data: dict[str, Any],
    context: dict[str, Any],
    bom_path: Path | None = None,
    registry_path: Path | None = None,
) -> CompiledPromptArtifact:
    """Compile a prompt template into a CompiledPromptArtifact.

    Steps:
    1. Load PromptBOM
    2. Load prompt registry
    3. Resolve template
    4. Validate required slots (BOM contract)
    5. Validate input contract (template contract)
    6. Render slots ({{variable}} substitution)
    7. Compute hashes (BOM, registry, template, slots, artifact)
    8. Emit CompiledPromptArtifact

    Args:
        template_id: Template ID from prompt_registry.yaml.
        input_data: Data for {{variable}} substitution in slot bodies.
        context: Execution context — must contain request_id, run_id, trace_id,
                 c0_bundle_hash, depth_profile.
        bom_path: Override BOM path (default: prompt_bom.yaml in this package).
        registry_path: Override registry path (default: prompt_registry.yaml).

    Returns:
        CompiledPromptArtifact.

    Raises:
        PromptAssemblyError: If any validation or hash step fails.
            Caller must route this through Exit v6 as X3E_SAFE_ABSTAIN.

    FORBIDDEN in this function:
        - retrieve() calls
        - provider/LLM calls
        - tool calls
        - L4 writes
        - Exit disposition emission
    """
    bom = load_prompt_bom(bom_path)
    registry = load_prompt_registry(registry_path)
    template = load_template(template_id, registry)

    _validate_required_slots(template, bom)
    _validate_input_contract(template, input_data)

    rendered_slots = _render_slots(template, input_data)

    # Canonical slot bytes hash
    canonical_bytes = json.dumps(rendered_slots, sort_keys=True, separators=(",", ":"))
    canonical_slot_bytes_hash = hashlib.sha256(canonical_bytes.encode()).hexdigest()

    # Component hashes
    bom_hash = compute_bom_hash(bom)
    registry_hash = compute_registry_hash(registry)
    template_hash = compute_template_hash(template)

    # Context bindings
    request_id = context.get("request_id", "")
    run_id = context.get("run_id", "")
    trace_id = context.get("trace_id", "")
    route_id = context.get("route_id", "R3_SIMPLE_GROUNDED_READ")
    c0_bundle_hash = context.get("c0_bundle_hash", "")
    depth_profile = context.get("depth_profile", "")

    # Artifact ID
    artifact_id = hashlib.sha256(
        f"{template_id}:{template_hash}:{request_id}:{run_id}".encode()
    ).hexdigest()[:32]

    # Final artifact hash
    artifact_hash = _compute_hash({
        "artifact_id": artifact_id,
        "template_id": template_id,
        "template_hash": template_hash,
        "prompt_bom_hash": bom_hash,
        "prompt_registry_hash": registry_hash,
        "c0_bundle_hash": c0_bundle_hash,
        "canonical_slot_bytes_hash": canonical_slot_bytes_hash,
    })

    return CompiledPromptArtifact(
        artifact_id=artifact_id,
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        route_id=route_id,
        template_id=template_id,
        template_version=template.get("version", "1.0"),
        prompt_bom_hash=bom_hash,
        prompt_registry_hash=registry_hash,
        template_hash=template_hash,
        c0_bundle_hash=c0_bundle_hash,
        depth_profile=depth_profile,
        allowed_stage=template.get("allowed_stage", ""),
        output_schema_ref=template.get("output_contract", {}).get("type", ""),
        provider_lane=context.get("provider_lane", "governed"),
        rendered_slots=rendered_slots,
        canonical_slot_bytes_hash=canonical_slot_bytes_hash,
        artifact_hash=artifact_hash,
        audit_refs=context.get("audit_refs", []),
    )


def compile_repair_prompt(
    repair_template_id: str,
    draft_context: dict[str, Any],
    execution_context: dict[str, Any],
) -> CompiledPromptArtifact:
    """Compile a repair-specific prompt (e.g. brief_citation_repair_v1).

    Hard rule: E3 repair steps must use a repair-specific CompiledPromptArtifact.
    No ad hoc repair prompt strings.

    Args:
        repair_template_id: e.g. 'brief_citation_repair_v1'
        draft_context: Context about the draft being repaired.
        execution_context: Execution context (request_id, run_id, c0_bundle_hash, etc.)

    Returns:
        CompiledPromptArtifact for the repair step.
    """
    input_data = {**execution_context, **draft_context}
    return compile_prompt(
        template_id=repair_template_id,
        input_data=input_data,
        context=execution_context,
    )
