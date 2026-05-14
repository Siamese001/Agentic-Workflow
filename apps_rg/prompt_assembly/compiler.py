# apps_rg Prompt Assembly Compiler
# Local compile/validation path — no runtime wiring, no agentic_core imports

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Optional

import yaml

from .contracts import (
    AUTHORITY_PRECEDENCE,
    CompiledPromptArtifact,
    ComponentHashMap,
    EvidenceSource,
    PromptAssemblyError,
    PromptAssemblyInput,
    PromptSlotPayload,
    SlotAuthority,
)


# =============================================================================
# Canonical Slot Ordering (S0 > D0 > I0 > C0 > E0 > Y0 > U0 > R0 > H0 > M0)
# =============================================================================
CANONICAL_SLOT_ORDER = [
    "S0",  # SYSTEM_AUTHORITY - sovereign, must be first
    "D0",  # BINDING_AUTHORITY - security fences
    "I0",  # GOVERNED_AUTHORITY - domain instructions
    "C0",  # INFORMATIONAL_AUTHORITY - evidence data (source-separated)
    "E0",  # EXAMPLE_AUTHORITY - approved examples
    "Y0",  # STYLE_AUTHORITY - synthesis preferences (advisory)
    "U0",  # ZERO_AUTHORITY - user intent only
    "R0",  # SCHEMA_AUTHORITY - output contract
    "H0",  # REPAIR_HINTS - healing guidance
    "M0",  # PROVIDER_RENDER_CONTROL - model/token control
]

# Authority class mapping
SLOT_TO_AUTHORITY: dict[str, SlotAuthority] = {
    "S0": SlotAuthority.SYSTEM_AUTHORITY,
    "D0": SlotAuthority.BINDING_AUTHORITY,
    "I0": SlotAuthority.GOVERNED_AUTHORITY,
    "C0": SlotAuthority.INFORMATIONAL_AUTHORITY,
    "E0": SlotAuthority.EXAMPLE_AUTHORITY,
    "Y0": SlotAuthority.STYLE_AUTHORITY,
    "U0": SlotAuthority.ZERO_AUTHORITY,
    "R0": SlotAuthority.SCHEMA_AUTHORITY,
    "H0": SlotAuthority.REPAIR_HINTS,
    "M0": SlotAuthority.PROVIDER_RENDER_CONTROL,
}

# =============================================================================
# W7: Lower-Authority Override Detection Patterns
# =============================================================================
# These patterns in lower-authority slots (U0, C0, E0, Y0, H0) attempting
# to override higher-authority slots (S0, D0, I0, R0) must be blocked.
OVERRIDE_ATTEMPT_PATTERNS: list[str] = [
    # Direct instruction overrides
    "ignore previous instructions",
    "ignore the above",
    "ignore all prior",
    "disregard previous",
    "override system instructions",
    "override the system prompt",
    "bypass the system",
    "system prompt override",
    
    # Fabrication requests
    "fabricate metrics",
    "fabricate achievements",
    "invent metrics",
    "invent achievements",
    "make up numbers",
    "create fake",
    
    # Source/confidence attacks
    "do not cite sources",
    "no need to cite",
    "skip the sources",
    "treat jd as candidate experience",
    "treat job description as experience",
    "jd proves experience",
    
    # Schema/format overrides
    "bypass schema",
    "ignore the schema",
    "change output format",
    "different format than specified",
    "instead of json",
    "output as plain text",
    
    # Authority confusion
    "you are now a different",
    "new instructions replace",
    "forget your training",
]

# Slots that can NEVER contain override attempts (lower authority)
LOWER_AUTHORITY_SLOTS = {"U0", "C0", "E0", "Y0", "H0", "M0"}

# Slots that are PROTECTED from override (higher authority)
PROTECTED_SLOTS = {"S0", "D0", "I0", "R0"}


class PromptCompiler:
    """Local PA compiler for apps_rg declarative prompt artifacts.
    
    NO agentic_core imports — self-contained for apps_rg local use.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize compiler with path to prompt_assembly directory."""
        if base_path is None:
            # Default: apps_rg/prompt_assembly relative to this file
            self.base_path = Path(__file__).parent
        else:
            self.base_path = Path(base_path)
        
        self._bom: Optional[dict] = None
        self._registry: Optional[dict] = None
        self._schema: Optional[dict] = None
    
    def load_bom(self) -> dict:
        """Load prompt_bom.yaml defining 8-slot authority model."""
        if self._bom is not None:
            return self._bom
        
        bom_path = self.base_path / "prompt_bom.yaml"
        if not bom_path.exists():
            raise PromptAssemblyError(
                code="MISSING_BOM",
                message=f"prompt_bom.yaml not found at {bom_path}",
            )
        
        try:
            with open(bom_path, "r", encoding="utf-8") as f:
                self._bom = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise PromptAssemblyError(
                code="INVALID_BOM_YAML",
                message=f"Failed to parse prompt_bom.yaml: {e}",
            )
        
        return self._bom
    
    def load_registry(self) -> dict:
        """Load prompt_registry.yaml mapping template IDs to files."""
        if self._registry is not None:
            return self._registry
        
        registry_path = self.base_path / "prompt_registry.yaml"
        if not registry_path.exists():
            raise PromptAssemblyError(
                code="MISSING_REGISTRY",
                message=f"prompt_registry.yaml not found at {registry_path}",
            )
        
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                self._registry = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise PromptAssemblyError(
                code="INVALID_REGISTRY_YAML",
                message=f"Failed to parse prompt_registry.yaml: {e}",
            )
        
        return self._registry
    
    def load_schema(self) -> dict:
        """Load rg_output_schema.json as R0 schema contract."""
        if self._schema is not None:
            return self._schema
        
        # Schema is in apps_rg root, not prompt_assembly
        schema_path = self.base_path.parent / "rg_output_schema.json"
        if not schema_path.exists():
            raise PromptAssemblyError(
                code="MISSING_SCHEMA",
                message=f"rg_output_schema.json not found at {schema_path}",
            )
        
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                self._schema = json.load(f)
        except json.JSONDecodeError as e:
            raise PromptAssemblyError(
                code="INVALID_SCHEMA_JSON",
                message=f"Failed to parse rg_output_schema.json: {e}",
            )
        
        return self._schema
    
    def resolve_template(self, template_id: str) -> dict:
        """Resolve template ID to template definition from registry."""
        registry = self.load_registry()
        
        templates = registry.get("templates", {})
        # Templates is a dict keyed by template_id
        if template_id in templates:
            return templates[template_id]
        
        raise PromptAssemblyError(
            code="UNKNOWN_TEMPLATE_ID",
            message=f"Template '{template_id}' not found in registry",
            context={"available_templates": list(templates.keys())},
        )
    
    def load_template_file(self, file_path: str) -> dict:
        """Load template YAML file from templates directory.
        
        file_path is relative to base_path (e.g., 'templates/strategic_tailor_v1.yaml').
        """
        full_path = self.base_path / file_path
        if not full_path.exists():
            raise PromptAssemblyError(
                code="MISSING_TEMPLATE_FILE",
                message=f"Template file not found: {full_path}",
                context={"file_path": file_path},
            )
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise PromptAssemblyError(
                code="INVALID_TEMPLATE_YAML",
                message=f"Failed to parse template file {file_path}: {e}",
                context={"file_path": file_path},
            )
    
    def validate_slot_order(self, slots: list[str]) -> bool:
        """Validate that slots follow canonical authority precedence."""
        # W7: Check for duplicate slot IDs
        seen_slots = set()
        for slot in slots:
            if slot in seen_slots:
                raise PromptAssemblyError(
                    code="DUPLICATE_SLOT_ID",
                    message=f"Duplicate slot ID '{slot}' found in compilation order",
                    slot_id=slot,
                    context={"slots": slots},
                )
            seen_slots.add(slot)
        
        # Build list of (slot, precedence) for input slots
        slot_prec = []
        for slot in slots:
            authority = SLOT_TO_AUTHORITY.get(slot)
            if authority is None:
                raise PromptAssemblyError(
                    code="UNKNOWN_SLOT",
                    message=f"Unknown slot ID: {slot}",
                    context={"valid_slots": list(SLOT_TO_AUTHORITY.keys())},
                )
            prec = AUTHORITY_PRECEDENCE.get(authority, 0)
            slot_prec.append((slot, prec))
        
        # Check descending order (higher precedence first)
        for i in range(len(slot_prec) - 1):
            current_prec = slot_prec[i][1]
            next_prec = slot_prec[i + 1][1]
            if current_prec < next_prec:
                raise PromptAssemblyError(
                    code="INVALID_SLOT_ORDER",
                    message=(
                        f"Slot '{slot_prec[i+1][0]}' (precedence={next_prec}) "
                        f"cannot precede lower-authority slots after "
                        f"'{slot_prec[i][0]}' (precedence={current_prec})"
                    ),
                    context={
                        "canonical_order": CANONICAL_SLOT_ORDER,
                        "actual_order": slots,
                    },
                )
        
        return True
    
    def detect_override_attempts(self, slot_id: str, content: str) -> None:
        """W7: Detect lower-authority override attempts in slot content.
        
        Raises PromptAssemblyError if override patterns are detected in
        lower-authority slots (U0, C0, E0, Y0, H0, M0) attempting to
        override protected slots (S0, D0, I0, R0).
        """
        # Only check lower-authority slots
        if slot_id not in LOWER_AUTHORITY_SLOTS:
            return
        
        content_lower = content.lower()
        
        for pattern in OVERRIDE_ATTEMPT_PATTERNS:
            if pattern.lower() in content_lower:
                raise PromptAssemblyError(
                    code="OVERRIDE_ATTEMPT_DETECTED",
                    message=(
                        f"Lower-authority slot '{slot_id}' contains override attempt: "
                        f"'{pattern}'. This violates authority boundaries."
                    ),
                    slot_id=slot_id,
                    context={
                        "detected_pattern": pattern,
                        "protected_slots": list(PROTECTED_SLOTS),
                        "safe_downstream_instruction": (
                            "REJECT compilation and alert security team. "
                            "Do not process prompts with override attempts."
                        ),
                    },
                )
    
    def validate_c0_separation(self, input_data: PromptAssemblyInput) -> None:
        """W7: Validate C0 evidence separation requirements."""
        # Check candidate_facts present and non-empty
        if not input_data.c0_candidate_facts or not input_data.c0_candidate_facts.content.strip():
            raise PromptAssemblyError(
                code="C0_MISSING_CANDIDATE_FACTS",
                message="C0 slot requires candidate_facts evidence",
                slot_id="C0",
                context={
                    "safe_downstream_instruction": "Provide structured candidate_facts evidence",
                },
            )
        
        # Check jd_requirements present and non-empty
        if not input_data.c0_jd_requirements or not input_data.c0_jd_requirements.content.strip():
            raise PromptAssemblyError(
                code="C0_MISSING_JD_REQUIREMENTS",
                message="C0 slot requires jd_requirements evidence",
                slot_id="C0",
                context={
                    "safe_downstream_instruction": "Provide structured jd_requirements evidence",
                },
            )
        
        # Validate source tags are present and distinct
        cf_tag = input_data.c0_candidate_facts.source_tag
        jd_tag = input_data.c0_jd_requirements.source_tag
        
        if not cf_tag:
            raise PromptAssemblyError(
                code="C0_MISSING_SOURCE_TAG",
                message="candidate_facts must have source_tag",
                slot_id="C0",
            )
        if not jd_tag:
            raise PromptAssemblyError(
                code="C0_MISSING_SOURCE_TAG",
                message="jd_requirements must have source_tag",
                slot_id="C0",
            )
        
        # Ensure tags are different
        if cf_tag == jd_tag:
            raise PromptAssemblyError(
                code="C0_DUPLICATE_SOURCE_TAGS",
                message=f"candidate_facts and jd_requirements must have different source_tags, both have '{cf_tag}'",
                slot_id="C0",
            )
    
    def validate_r0_schema(self, input_data: PromptAssemblyInput) -> None:
        """W7: Validate R0 schema reference is present and valid JSON."""
        if not input_data.r0_response_schema:
            raise PromptAssemblyError(
                code="R0_MISSING_SCHEMA",
                message="R0 slot requires response_schema (JSON or schema ref)",
                slot_id="R0",
                context={
                    "safe_downstream_instruction": "Provide valid JSON schema in r0_response_schema field",
                },
            )
        
        # Validate it's valid JSON (even if it's just a schema reference string)
        try:
            json.loads(input_data.r0_response_schema)
        except json.JSONDecodeError as e:
            raise PromptAssemblyError(
                code="R0_INVALID_JSON_SCHEMA",
                message=f"R0 response_schema is not valid JSON: {e}",
                slot_id="R0",
                context={
                    "safe_downstream_instruction": "Provide valid JSON schema",
                },
            )
    
    def compile(self, input_data: PromptAssemblyInput) -> CompiledPromptArtifact:
        """Compile PromptAssemblyInput into CompiledPromptArtifact."""
        # Validate required fields
        if not input_data.template_id:
            raise PromptAssemblyError(
                code="MISSING_TEMPLATE_ID",
                message="template_id is required",
                context={"safe_downstream_instruction": "Provide valid template_id from prompt_registry.yaml"},
            )
        
        # W7: Validate C0 evidence separation before compilation
        self.validate_c0_separation(input_data)
        
        # W7: Validate R0 schema reference
        self.validate_r0_schema(input_data)
        
        # Resolve template
        template_def = self.resolve_template(input_data.template_id)
        template_file = template_def.get("path", "")
        template_version = template_def.get("version", "1.0.0")
        
        # Load template YAML
        template_yaml = self.load_template_file(template_file)
        
        # Get required slots from template
        required_slots = template_def.get("required_slots", [])
        
        # Build slot payloads in canonical order
        slot_payloads = []
        slot_contents = {}
        
        for slot_id in CANONICAL_SLOT_ORDER:
            content = self._get_slot_content(input_data, slot_id)
            if content is not None:
                # W7: Detect override attempts in lower-authority slots
                self.detect_override_attempts(slot_id, content)
                
                authority = SLOT_TO_AUTHORITY.get(slot_id, SlotAuthority.ZERO_AUTHORITY)
                content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                
                payload = PromptSlotPayload(
                    slot_id=slot_id,
                    slot_name=f"{slot_id}_{authority.name}",
                    authority_class=authority,
                    content=content,
                    content_hash=content_hash,
                    source_tag=self._get_source_tag(slot_id),
                )
                slot_payloads.append(payload)
                slot_contents[slot_id] = content
        
        # Validate all required slots present
        present_slots = {p.slot_id for p in slot_payloads}
        for required in required_slots:
            if required not in present_slots:
                raise PromptAssemblyError(
                    code="MISSING_REQUIRED_SLOT",
                    message=f"Required slot '{required}' not found in input",
                    slot_id=required,
                )
        
        # Validate canonical order
        actual_order = [p.slot_id for p in slot_payloads]
        self.validate_slot_order(actual_order)
        
        # Build component hash map
        component_hash_map = ComponentHashMap(
            s0_hash=slot_contents.get("S0", "")[:16] if slot_contents.get("S0") else "",
            i0_hash=slot_contents.get("I0", "")[:16] if slot_contents.get("I0") else "",
            c0_candidate_hash=self._hash_evidence(input_data.c0_candidate_facts),
            c0_jd_hash=self._hash_evidence(input_data.c0_jd_requirements),
            u0_hash=slot_contents.get("U0", "")[:16] if slot_contents.get("U0") else "",
            r0_hash=slot_contents.get("R0", "")[:16] if slot_contents.get("R0") else "",
            d0_hash=slot_contents.get("D0", "")[:16] if slot_contents.get("D0") else None,
            e0_hash=slot_contents.get("E0", "")[:16] if slot_contents.get("E0") else None,
            y0_hash=slot_contents.get("Y0", "")[:16] if slot_contents.get("Y0") else None,
            template_hash=hashlib.sha256(json.dumps(template_yaml, sort_keys=True).encode()).hexdigest()[:16],
        )
        
        # Build system prompt (concatenate slots in order)
        system_parts = []
        for payload in slot_payloads:
            system_parts.append(f"<!-- SLOT: {payload.slot_id} -->")
            system_parts.append(payload.content)
            system_parts.append("")
        system_prompt = "\n".join(system_parts)
        
        # Build messages format
        messages = [{"role": "system", "content": system_prompt}]
        
        # Compute prompt hash
        hash_input = {
            "template_id": input_data.template_id,
            "template_version": template_version,
            "slot_order": actual_order,
            "component_hashes": component_hash_map.to_dict(),
            "system_prompt_length": len(system_prompt),
        }
        prompt_hash = hashlib.sha256(
            json.dumps(hash_input, sort_keys=True, separators=(',', ':')).encode()
        ).hexdigest()[:32]
        
        # Build lineage map
        slot_lineage_map = {
            p.slot_id: f"{p.slot_id}:{p.content_hash}@{component_hash_map.to_dict().get(p.slot_id, 'unknown')}"
            for p in slot_payloads
        }
        
        # Build manifests
        provider_render_manifest = {
            "model": "unspecified",  # Not wired to runtime
            "max_tokens": template_yaml.get("compilation_constraints", {}).get("max_response_tokens", 200),
            "temperature": template_yaml.get("provider_control", {}).get("temperature", 0.7),
        }
        
        replay_manifest = {
            "input": {
                "template_id": input_data.template_id,
                "request_id": input_data.request_id,
                "run_id": input_data.run_id,
            },
            "compiled_at": str(component_hash_map.to_dict()),
            "prompt_hash": prompt_hash,
        }
        
        # Build schema ref
        schema = self.load_schema()
        response_schema_ref = schema.get("$id", "apps_rg/rg_output_schema.json")
        
        # Create artifact
        artifact = CompiledPromptArtifact(
            messages=messages,
            system_prompt=system_prompt,
            canonical_slot_order=actual_order,
            slot_payloads=slot_payloads,
            slot_lineage_map=slot_lineage_map,
            template_id=input_data.template_id,
            template_version=template_version,
            component_hash_map=component_hash_map,
            prompt_hash=prompt_hash,
            response_schema_ref=response_schema_ref,
            provider_render_manifest=provider_render_manifest,
            replay_manifest=replay_manifest,
            slot_count=len(slot_payloads),
            token_estimate=len(system_prompt) // 4,  # Rough estimate
            has_no_fabrication_oath="NO FABRICATION" in (slot_contents.get("S0", "")),
            has_source_separation="candidate_facts" in (slot_contents.get("C0", "")),
            has_schema_reference=bool(response_schema_ref),
        )
        
        return artifact
    
    def _get_slot_content(self, input_data: PromptAssemblyInput, slot_id: str) -> Optional[str]:
        """Get content for a slot from input data."""
        slot_map = {
            "S0": input_data.s0_system_preamble,
            "D0": input_data.d0_fences,
            "I0": input_data.i0_instructions,
            "E0": input_data.e0_examples,
            "Y0": input_data.y0_style_preferences,
            "U0": input_data.u0_user_task,
            "H0": input_data.h0_healing_hints,
            "M0": input_data.m0_provider_control,
            "R0": input_data.r0_response_schema,
        }
        
        if slot_id == "C0":
            # Build C0 with source separation
            parts = []
            parts.append(input_data.c0_candidate_facts.to_tagged())
            parts.append(input_data.c0_jd_requirements.to_tagged())
            if input_data.c0_company_brief:
                parts.append(input_data.c0_company_brief.to_tagged())
            if input_data.c0_alignment_map:
                parts.append(input_data.c0_alignment_map.to_tagged())
            return "\n\n".join(parts)
        
        return slot_map.get(slot_id)
    
    def _get_source_tag(self, slot_id: str) -> Optional[str]:
        """Get source tag for a slot."""
        if slot_id == "C0":
            return "evidence_container"
        return None
    
    def _hash_evidence(self, evidence: EvidenceSource) -> str:
        """Hash an EvidenceSource for component hash map."""
        content = f"{evidence.source_type}:{evidence.content}:{evidence.confidence}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


# =============================================================================
# Module-level convenience functions
# =============================================================================

def compile_prompt(input_data: PromptAssemblyInput, base_path: Optional[Path] = None) -> CompiledPromptArtifact:
    """Compile a PromptAssemblyInput into a CompiledPromptArtifact.
    
    Convenience function that creates a PromptCompiler and compiles the input.
    """
    compiler = PromptCompiler(base_path=base_path)
    return compiler.compile(input_data)


def map_slots(input_data: PromptAssemblyInput) -> dict[str, str]:
    """Map input data to slot contents without full compilation.
    
    Returns a dictionary mapping slot IDs to content strings.
    """
    compiler = PromptCompiler()
    
    slot_contents = {}
    for slot_id in CANONICAL_SLOT_ORDER:
        content = compiler._get_slot_content(input_data, slot_id)
        if content:
            slot_contents[slot_id] = content
    
    return slot_contents
