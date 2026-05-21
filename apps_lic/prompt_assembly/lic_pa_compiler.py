"""
LIC Prompt Assembly Compiler.

Compiles prompt templates into CompiledPromptArtifact objects.

Prompt Assembly owns compilation only.
Prompt Assembly must NOT:
- retrieve
- route
- execute tools
- call providers
- mutate L4
- emit Exit disposition
- approve egress
- approve writes

L2 owns execution.
Provider gateway owns model invocation.
Exit owns final disposition.
UWG owns durable write admission.
"""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


@dataclass
class CompiledPromptArtifact:
    """
    A compiled, signed/deterministically hashed prompt artifact.
    
    Required fields per plan specification:
    - artifact_id, request_id, run_id, trace_id, route_id
    - template_id, template_version
    - prompt_bom_hash, prompt_registry_hash, template_hash
    - manifest_hash, policy_hash, blueprint_hash, replay_key
    - origin_label_map, claim_permission_map, omission_policy
    - send_mode_restrictions, output_schema_ref, provider_lane
    - rendered_slots, canonical_slot_bytes_hash, artifact_hash
    - audit_refs
    """
    
    # Identity
    artifact_id: str
    request_id: str
    run_id: str
    trace_id: str
    route_id: str
    
    # Template binding
    template_id: str
    template_version: str
    
    # Hash bindings
    prompt_bom_hash: str
    prompt_registry_hash: str
    template_hash: str
    manifest_hash: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    
    # Governance fields
    origin_label_map: Dict[str, Any]
    claim_permission_map: Dict[str, Any]
    omission_policy: Dict[str, Any]
    send_mode_restrictions: Dict[str, Any]
    output_schema_ref: str
    provider_lane: str
    
    # Content
    rendered_slots: Dict[str, str]
    canonical_slot_bytes_hash: str
    artifact_hash: str
    audit_refs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
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
            "manifest_hash": self.manifest_hash,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "replay_key": self.replay_key,
            "origin_label_map": self.origin_label_map,
            "claim_permission_map": self.claim_permission_map,
            "omission_policy": self.omission_policy,
            "send_mode_restrictions": self.send_mode_restrictions,
            "output_schema_ref": self.output_schema_ref,
            "provider_lane": self.provider_lane,
            "rendered_slots": self.rendered_slots,
            "canonical_slot_bytes_hash": self.canonical_slot_bytes_hash,
            "artifact_hash": self.artifact_hash,
            "audit_refs": self.audit_refs,
        }


class PromptAssemblyError(Exception):
    """Error during prompt assembly compilation."""
    pass


def _compute_hash(data: Any) -> str:
    """Compute deterministic SHA256 hash of data."""
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def load_prompt_bom(bom_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load PromptBOM from YAML.
    
    Args:
        bom_path: Path to prompt_bom.yaml (default: apps_lic/prompt_assembly/prompt_bom.yaml)
        
    Returns:
        PromptBOM dictionary
        
    Raises:
        PromptAssemblyError: If BOM not found or invalid
    """
    if bom_path is None:
        bom_path = Path("apps_lic/prompt_assembly/prompt_bom.yaml")
    
    if not bom_path.exists():
        raise PromptAssemblyError(f"PromptBOM not found: {bom_path}")
    
    with open(bom_path) as f:
        bom = yaml.safe_load(f)
    
    # Validate required fields
    required = ["schema_version", "bom_id", "required_slots", "slot_definitions"]
    for field_name in required:
        if field_name not in bom:
            raise PromptAssemblyError(f"PromptBOM missing required field: {field_name}")
    
    return bom


def load_prompt_registry(registry_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load prompt registry from YAML.
    
    Args:
        registry_path: Path to prompt_registry.yaml (default: apps_lic/config/prompt_registry.yaml)
        
    Returns:
        Prompt registry dictionary
        
    Raises:
        PromptAssemblyError: If registry not found or invalid
    """
    if registry_path is None:
        registry_path = Path("apps_lic/config/prompt_registry.yaml")
    
    if not registry_path.exists():
        raise PromptAssemblyError(f"Prompt registry not found: {registry_path}")
    
    with open(registry_path) as f:
        registry = yaml.safe_load(f)
    
    # Validate required fields
    if "templates" not in registry:
        raise PromptAssemblyError("Prompt registry missing 'templates' field")
    
    return registry


def load_template(template_id: str, registry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load a template from the registry.
    
    Args:
        template_id: Template identifier
        registry: Loaded prompt registry
        
    Returns:
        Template dictionary
        
    Raises:
        PromptAssemblyError: If template not found
    """
    templates = registry.get("templates", {})
    template_meta = templates.get(template_id)
    
    if template_meta is None:
        raise PromptAssemblyError(f"Template not found in registry: {template_id}")
    
    template_path = Path(template_meta["path"])
    if not template_path.exists():
        raise PromptAssemblyError(f"Template file not found: {template_path}")
    
    with open(template_path) as f:
        template = yaml.safe_load(f)
    
    return template


def validate_required_slots(
    template: Dict[str, Any],
    bom: Dict[str, Any],
) -> None:
    """
    Validate that template has all required slots from BOM.
    
    Args:
        template: Loaded template
        bom: Loaded PromptBOM
        
    Raises:
        PromptAssemblyError: If required slots missing
    """
    required_slots = set(bom.get("required_slots", []))
    template_slots = set(template.get("required_slots", []))
    
    missing = required_slots - template_slots
    if missing:
        raise PromptAssemblyError(f"Template missing required slots: {missing}")
    
    # Also check slot_bodies exist
    slot_bodies = template.get("slot_bodies", {})
    for slot in required_slots:
        if slot not in slot_bodies or not slot_bodies[slot]:
            raise PromptAssemblyError(f"Template missing slot body for: {slot}")


def validate_input_contract(
    template: Dict[str, Any],
    input_data: Dict[str, Any],
) -> None:
    """
    Validate input data against template input_contract.
    
    Args:
        template: Loaded template
        input_data: Input data to validate
        
    Raises:
        PromptAssemblyError: If required fields missing
    """
    input_contract = template.get("input_contract", {})
    required_fields = input_contract.get("required", [])
    
    missing = [f for f in required_fields if f not in input_data]
    if missing:
        raise PromptAssemblyError(f"Input missing required fields: {missing}")


def render_slots(
    template: Dict[str, Any],
    input_data: Dict[str, Any],
) -> Dict[str, str]:
    """
    Render template slots with input data.
    
    Args:
        template: Loaded template
        input_data: Input data for rendering
        
    Returns:
        Dictionary of rendered slot content
    """
    slot_bodies = template.get("slot_bodies", {})
    rendered = {}
    
    for slot_id, slot_template in slot_bodies.items():
        # Simple variable substitution: {{variable_name}}
        content = slot_template
        for key, value in input_data.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in content:
                content = content.replace(placeholder, str(value))
        
        rendered[slot_id] = content
    
    return rendered


def compute_template_hash(template: Dict[str, Any]) -> str:
    """Compute hash of template content."""
    hash_fields = template.get("hash_fields", ["template_id", "version", "slot_bodies"])
    data = {k: template.get(k) for k in hash_fields}
    return _compute_hash(data)


def compute_bom_hash(bom: Dict[str, Any]) -> str:
    """Compute hash of PromptBOM."""
    hash_fields = bom.get("hash_fields", ["schema_version", "bom_id", "required_slots", "slot_definitions"])
    data = {k: bom.get(k) for k in hash_fields}
    return _compute_hash(data)


def compute_registry_hash(registry: Dict[str, Any]) -> str:
    """Compute hash of prompt registry."""
    hash_fields = registry.get("hash_fields", ["schema_version", "registry_id", "templates"])
    data = {k: registry.get(k) for k in hash_fields}
    return _compute_hash(data)


def compile_prompt(
    template_id: str,
    input_data: Dict[str, Any],
    context: Dict[str, Any],
    bom_path: Optional[Path] = None,
    registry_path: Optional[Path] = None,
) -> CompiledPromptArtifact:
    """
    Compile a prompt template into a CompiledPromptArtifact.
    
    This is the main entry point for Prompt Assembly. It:
    1. Loads PromptBOM
    2. Loads prompt registry
    3. Resolves template
    4. Validates required slots
    5. Validates input contract
    6. Renders slots
    7. Computes hashes
    8. Emits CompiledPromptArtifact
    
    Args:
        template_id: Template to compile
        input_data: Input data for template rendering
        context: Execution context containing manifest_hash, policy_hash, etc.
        bom_path: Optional path to PromptBOM
        registry_path: Optional path to prompt registry
        
    Returns:
        CompiledPromptArtifact
        
    Raises:
        PromptAssemblyError: If compilation fails
        
    Note:
        This function does NOT:
        - retrieve new information
        - call providers
        - execute tools
        - mutate L4
        - emit Exit disposition
    """
    # Load BOM and registry
    bom = load_prompt_bom(bom_path)
    registry = load_prompt_registry(registry_path)
    
    # Load template
    template = load_template(template_id, registry)
    
    # Validate required slots
    validate_required_slots(template, bom)
    
    # Validate input contract
    validate_input_contract(template, input_data)
    
    # Render slots
    rendered_slots = render_slots(template, input_data)
    
    # Compute canonical slot bytes hash
    canonical_slot_bytes = json.dumps(rendered_slots, sort_keys=True, separators=(',', ':'))
    canonical_slot_bytes_hash = hashlib.sha256(canonical_slot_bytes.encode('utf-8')).hexdigest()
    
    # Compute all hashes
    template_hash = compute_template_hash(template)
    prompt_bom_hash = compute_bom_hash(bom)
    prompt_registry_hash = compute_registry_hash(registry)
    
    # Extract context bindings
    manifest_hash = context.get("manifest_hash", "")
    policy_hash = context.get("policy_hash", "")
    blueprint_hash = context.get("blueprint_hash", "")
    replay_key = context.get("replay_key", "")
    request_id = context.get("request_id", "")
    run_id = context.get("run_id", "")
    trace_id = context.get("trace_id", "")
    route_id = context.get("route_id", "")
    
    # Generate artifact ID
    artifact_id = hashlib.sha256(
        f"{template_id}:{template_hash}:{request_id}:{run_id}".encode()
    ).hexdigest()[:32]
    
    # Compute final artifact hash
    artifact_data = {
        "artifact_id": artifact_id,
        "template_id": template_id,
        "template_hash": template_hash,
        "prompt_bom_hash": prompt_bom_hash,
        "prompt_registry_hash": prompt_registry_hash,
        "manifest_hash": manifest_hash,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "replay_key": replay_key,
        "canonical_slot_bytes_hash": canonical_slot_bytes_hash,
    }
    artifact_hash = _compute_hash(artifact_data)
    
    # Build artifact
    artifact = CompiledPromptArtifact(
        artifact_id=artifact_id,
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        route_id=route_id,
        template_id=template_id,
        template_version=template.get("version", "1.0"),
        prompt_bom_hash=prompt_bom_hash,
        prompt_registry_hash=prompt_registry_hash,
        template_hash=template_hash,
        manifest_hash=manifest_hash,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
        origin_label_map=context.get("origin_label_map", {}),
        claim_permission_map=context.get("claim_permission_map", {}),
        omission_policy=context.get("omission_policy", {}),
        send_mode_restrictions=context.get("send_mode_restrictions", {}),
        output_schema_ref=template.get("output_contract", {}).get("type", ""),
        provider_lane=context.get("provider_lane", "governed"),
        rendered_slots=rendered_slots,
        canonical_slot_bytes_hash=canonical_slot_bytes_hash,
        artifact_hash=artifact_hash,
        audit_refs=context.get("audit_refs", []),
    )
    
    return artifact


def compile_repair_prompt(
    repair_template_id: str,
    draft_context: Dict[str, Any],
    execution_context: Dict[str, Any],
) -> CompiledPromptArtifact:
    """
    Compile a repair-specific prompt.
    
    Hard rule: E4 repair steps must use repair-specific CompiledPromptArtifact objects.
    No ad hoc repair prompt strings allowed.
    
    Args:
        repair_template_id: Repair template ID (e.g., "unsupported_claim_omission_v1")
        draft_context: Draft context for repair
        execution_context: Execution context
        
    Returns:
        CompiledPromptArtifact for repair
    """
    # Merge contexts for input data
    input_data = {**execution_context, **draft_context}
    
    return compile_prompt(
        template_id=repair_template_id,
        input_data=input_data,
        context=execution_context,
    )


# ============================================================================
# Self-test
# ============================================================================

if __name__ == "__main__":
    print("lic_pa_compiler scaffold loaded successfully")
    
    # Test loading
    try:
        bom = load_prompt_bom()
        print(f"Loaded PromptBOM: {bom['bom_id']}")
        print(f"Required slots: {len(bom['required_slots'])}")
        
        registry = load_prompt_registry()
        print(f"Loaded registry: {registry['registry_id']}")
        print(f"Templates: {list(registry['templates'].keys())}")
        
        # Test template loading
        template = load_template("outreach_draft_v1", registry)
        print(f"Loaded template: {template['template_id']}")
        print(f"Template has {len(template.get('slot_bodies', {}))} slot bodies")
        
    except PromptAssemblyError as e:
        print(f"Expected error (files may not exist yet): {e}")
    except Exception as e:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        print(f"Error: {e}")
