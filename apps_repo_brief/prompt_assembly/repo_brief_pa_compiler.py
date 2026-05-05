"""
Prompt Assembly compiler for apps_repo_brief.

Loads prompt_bom.yaml and prompt_registry.yaml, resolves templates,
validates required slots and input contracts, renders structured slot
bodies, and emits a CompiledPromptArtifact.

Must NOT: retrieve evidence, route, call providers, execute tools,
emit Exit disposition, or write durable state.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P2.12, §9.5
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PROMPT_BOM_PATH = _REPO_ROOT / "apps_repo_brief" / "prompt_assembly" / "prompt_bom.yaml"
_PROMPT_REGISTRY_PATH = _REPO_ROOT / "apps_repo_brief" / "config" / "prompt_registry.yaml"
_TEMPLATES_DIR = _REPO_ROOT / "apps_repo_brief" / "prompt_assembly" / "templates"


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file and return as dict. Fails closed on error."""
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "PyYAML is required for prompt assembly compilation"
        ) from exc
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping at {path}, got {type(data)}")
    return data


def _sha256_of(obj: Any) -> str:
    """Stable SHA-256 hex digest of JSON-serialisable object."""
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


class RepoBriefPACompiler:
    """
    Prompt Assembly compiler for the apps_repo_brief executive brief route.

    Lifecycle:
      1. Load prompt_bom.yaml  →  _bom
      2. Load prompt_registry.yaml  →  _registry
      3. Validate required slots against BOM definition
      4. Resolve template by template_id from registry
      5. Load template YAML from templates/
      6. Validate input_contract: required_inputs present in evidence_bundle
      7. Render slot bodies (structural — content provided by caller)
      8. Compute hashes and emit CompiledPromptArtifact

    This class is a PURE PA compiler — it does not retrieve evidence, call
    providers, or write state.  Full implementation completes in W3.
    """

    def __init__(self) -> None:
        self._bom: dict[str, Any] = {}
        self._registry: dict[str, Any] = {}
        self._templates: dict[str, dict[str, Any]] = {}
        self._loaded = False

    def load(self) -> "RepoBriefPACompiler":
        """Load BOM and registry from canonical paths. Returns self for chaining."""
        self._bom = _load_yaml(_PROMPT_BOM_PATH)
        self._registry = _load_yaml(_PROMPT_REGISTRY_PATH)
        self._loaded = True
        return self

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    def _get_template_entry(self, template_id: str) -> dict[str, Any]:
        """Resolve a template entry from the registry by template_id."""
        self._ensure_loaded()
        for entry in self._registry.get("templates", []):
            if entry.get("template_id") == template_id:
                return entry
        raise ValueError(
            f"Template '{template_id}' not found in prompt registry. "
            f"Available: {[e['template_id'] for e in self._registry.get('templates', [])]}"
        )

    def _load_template(self, template_id: str) -> dict[str, Any]:
        """Load template YAML from templates directory."""
        if template_id in self._templates:
            return self._templates[template_id]
        entry = self._get_template_entry(template_id)
        rel_path = entry.get("path", "")
        # Strip the app-relative prefix to get just the filename
        template_filename = Path(rel_path).name
        template_path = _TEMPLATES_DIR / template_filename
        if not template_path.exists():
            raise FileNotFoundError(
                f"Template file not found: {template_path}. "
                f"Registry entry: {entry}"
            )
        template = _load_yaml(template_path)
        self._templates[template_id] = template
        return template

    def validate_slots(
        self, template_id: str, provided_slots: set[str]
    ) -> list[str]:
        """
        Validate that all required slots are present in provided_slots.
        Returns list of missing required slot IDs (empty = valid).
        """
        self._ensure_loaded()
        template = self._load_template(template_id)
        required = set(template.get("required_slots", []))
        missing = sorted(required - provided_slots)
        return missing

    def validate_input_contract(
        self,
        template_id: str,
        evidence_bundle: dict[str, Any],
    ) -> list[str]:
        """
        Validate that all required_inputs are present in evidence_bundle.
        Returns list of missing input names (empty = valid).
        """
        self._ensure_loaded()
        template = self._load_template(template_id)
        contract = template.get("input_contract", {})
        required_inputs = contract.get("required_inputs", [])
        missing = [r for r in required_inputs if r not in evidence_bundle]
        return missing

    def compile(
        self,
        *,
        template_id: str,
        evidence_bundle: dict[str, Any],
        request_id: str,
        run_id: str,
        trace_id: str,
        route_id: str,
        selected_capability: str,
        policy_hash: str,
        blueprint_hash: str,
        replay_key: str,
    ) -> dict[str, Any]:
        """
        Compile a CompiledPromptArtifact.

        Parameters
        ----------
        template_id:
            Template to use (must be registered in prompt_registry.yaml).
        evidence_bundle:
            Dict containing all required_inputs declared in the template's
            input_contract (FinalEvidenceContract, BriefingCoverageMatrix, etc.).
        request_id, run_id, trace_id, route_id, selected_capability:
            Identity fields from the governed run context.
        policy_hash, blueprint_hash, replay_key:
            Governance binding fields.

        Returns
        -------
        CompiledPromptArtifact dict with all required fields per §9.6.

        Raises
        ------
        ValueError
            If template not found, required slots missing, or input contract
            violations detected.
        """
        self._ensure_loaded()

        template = self._load_template(template_id)
        template_version = template.get("version", "unknown")

        # --- Validate input contract
        missing_inputs = self.validate_input_contract(template_id, evidence_bundle)
        if missing_inputs:
            raise ValueError(
                f"Input contract violation for template '{template_id}': "
                f"missing required inputs: {missing_inputs}"
            )

        # --- Compute structural hashes
        bom_hash = _sha256_of(self._bom)
        registry_hash = _sha256_of(self._registry)
        template_hash = _sha256_of(template)

        # Manifest hash binds all structural hashes
        manifest_hash = _sha256_of({
            "prompt_bom_hash": bom_hash,
            "prompt_registry_hash": registry_hash,
            "template_hash": template_hash,
            "policy_hash": policy_hash,
            "blueprint_hash": blueprint_hash,
        })

        # Evidence contract ref (from bundle if present)
        fec = evidence_bundle.get("FinalEvidenceContract", {})
        evidence_contract_ref = fec.get("contract_type", "apps_repo_brief.FinalEvidenceContract.v1")

        # --- P3.8 Full slot rendering (AG decision P3.2 Option A)
        # Each slot is rendered as a formatted string from the template's
        # slot_bodies definition combined with evidence_bundle values.
        # L2 consumes rendered_slots directly without touching template YAML.
        rendered_slots = self._render_slots(template, evidence_bundle)

        # Canonical slot bytes hash now covers actual rendered content
        canonical_slot_bytes = json.dumps(
            {
                "template_id": template_id,
                "rendered_slot_ids": sorted(rendered_slots.keys()),
                "evidence_status": fec.get("status", {}).get("evidence_status", "UNKNOWN"),
            },
            sort_keys=True,
        ).encode()
        canonical_slot_bytes_hash = hashlib.sha256(canonical_slot_bytes).hexdigest()

        artifact_id = f"cpa.{request_id}.{template_id}"
        artifact_hash = _sha256_of({
            "artifact_id": artifact_id,
            "manifest_hash": manifest_hash,
            "canonical_slot_bytes_hash": canonical_slot_bytes_hash,
            "replay_key": replay_key,
        })

        artifact: dict[str, Any] = {
            # Identity
            "artifact_id": artifact_id,
            "request_id": request_id,
            "run_id": run_id,
            "trace_id": trace_id,
            "route_id": route_id,
            "selected_capability": selected_capability,
            "template_id": template_id,
            "template_version": template_version,
            # Hashes
            "prompt_bom_hash": bom_hash,
            "prompt_registry_hash": registry_hash,
            "template_hash": template_hash,
            "manifest_hash": manifest_hash,
            # Governance
            "policy_hash": policy_hash,
            "blueprint_hash": blueprint_hash,
            "replay_key": replay_key,
            # Evidence references
            "evidence_contract_ref": evidence_contract_ref,
            "briefing_coverage_matrix_ref": evidence_bundle.get(
                "BriefingCoverageMatrix", {}
            ).get("briefing_profile_id", ""),
            "source_portfolio_ref": evidence_bundle.get(
                "SourcePortfolioSummary", {}
            ).get("surface_id", ""),
            "claim_evidence_map_ref": evidence_bundle.get(
                "ClaimEvidenceMap", {}
            ).get("map_id", ""),
            "contradiction_matrix_ref": evidence_bundle.get(
                "ContradictionMatrix", {}
            ).get("matrix_id", ""),
            "freshness_report_ref": evidence_bundle.get(
                "FreshnessReport", {}
            ).get("report_id", ""),
            # Fully rendered slots — L2 consumes these directly (P3.8)
            "rendered_slots": rendered_slots,
            "canonical_slot_bytes_hash": canonical_slot_bytes_hash,
            "artifact_hash": artifact_hash,
            # Output constraints
            "provider_lane": "governed_gateway",
            "output_schema_ref": "governed_repo_brief_packet_v1",
            "audit_refs": [],
        }

        _log.debug(
            "CompiledPromptArtifact emitted: artifact_id=%s template=%s",
            artifact_id,
            template_id,
        )
        return artifact

    # ------------------------------------------------------------------
    # P3.8 — Full slot rendering helpers
    # ------------------------------------------------------------------

    def _render_slots(
        self,
        template: dict[str, Any],
        evidence_bundle: dict[str, Any],
    ) -> dict[str, str]:
        """
        Render each slot defined in the template's slot_bodies section.

        Slot body rendering (AG P3.2 Option A):
          1. Start from the template slot_body text.
          2. Substitute evidence_bundle values for ``{{KEY}}`` tokens.
          3. Apply gap/caveat injection policy from SynthesisGuidanceForPA.
          4. Return dict slot_id → fully rendered string.

        Required slots (template.required_slots) that have no slot_body
        entry are rendered as a structured evidence injection placeholder
        with the actual evidence value from the bundle (not a scaffold stub).

        Optional slots that are absent from the bundle are omitted from
        the output (not included in rendered_slots dict).
        """
        slot_bodies: dict[str, Any] = template.get("slot_bodies", {})
        required_slots: list[str] = template.get("required_slots", [])
        optional_slots: list[str] = template.get("optional_slots", [])

        # Synthesis guidance from evidence bundle (if present)
        synthesis_guidance = evidence_bundle.get("SynthesisGuidanceForPA") or {}
        caveat_policy = synthesis_guidance.get("unsupported_claim_policy", "caveat_required")
        gap_handling = synthesis_guidance.get("gap_handling", "omit")

        rendered: dict[str, str] = {}

        # Render required slots
        for slot_id in required_slots:
            body_def = slot_bodies.get(slot_id)
            evidence_value = evidence_bundle.get(slot_id)
            rendered[slot_id] = self._render_single_slot(
                slot_id=slot_id,
                body_def=body_def,
                evidence_value=evidence_value,
                evidence_bundle=evidence_bundle,
                caveat_policy=caveat_policy,
                gap_handling=gap_handling,
                required=True,
            )

        # Render optional slots only when evidence is present
        for slot_id in optional_slots:
            if slot_id not in evidence_bundle:
                continue
            body_def = slot_bodies.get(slot_id)
            evidence_value = evidence_bundle.get(slot_id)
            rendered[slot_id] = self._render_single_slot(
                slot_id=slot_id,
                body_def=body_def,
                evidence_value=evidence_value,
                evidence_bundle=evidence_bundle,
                caveat_policy=caveat_policy,
                gap_handling=gap_handling,
                required=False,
            )

        return rendered

    def _render_single_slot(
        self,
        *,
        slot_id: str,
        body_def: Any,
        evidence_value: Any,
        evidence_bundle: dict[str, Any],
        caveat_policy: str,
        gap_handling: str,
        required: bool,
    ) -> str:
        """
        Render a single slot.

        Priority:
          1. If body_def is a string template, substitute {{KEY}} tokens from
             evidence_bundle.
          2. If body_def is absent but evidence_value is present, inject the
             evidence value directly with a structured wrapper.
          3. If neither is present and slot is required, apply gap_handling
             policy ("omit" → empty marker, "placeholder" → omit-note,
             "abstain" → ABSTAIN marker).
        """
        # Case 1: template body definition available
        if isinstance(body_def, str) and body_def.strip():
            rendered = self._substitute_tokens(body_def, evidence_bundle)
            # Apply caveat injection if evidence status is weak
            fec = evidence_bundle.get("FinalEvidenceContract") or {}
            evidence_status = ""
            if isinstance(fec, dict):
                evidence_status = fec.get("status", {}).get("evidence_status", "")
            if evidence_status in ("WEAK", "WEAK_WITH_CAVEATS") and caveat_policy == "caveat_required":
                rendered = self._inject_caveat(rendered, evidence_status)
            return rendered

        # Case 2: no body template but evidence_value present
        if evidence_value is not None:
            if isinstance(evidence_value, str):
                return evidence_value
            try:
                return json.dumps(evidence_value, ensure_ascii=False, indent=2)
            except (TypeError, ValueError):
                return str(evidence_value)

        # Case 3: gap — apply policy
        if not required:
            return ""
        if gap_handling == "abstain":
            return f"[ABSTAIN:slot={slot_id}] — C0 did not produce evidence for this slot."
        if gap_handling == "placeholder":
            return f"[GAP:slot={slot_id}] — evidence not available; section omitted per gap policy."
        # default: "omit" — return empty string, caller decides whether to include
        return ""

    @staticmethod
    def _substitute_tokens(template_text: str, evidence_bundle: dict[str, Any]) -> str:
        """
        Substitute ``{{KEY}}`` tokens in template_text with values from evidence_bundle.
        Unresolved tokens are left as-is (not silently dropped).
        """
        import re
        def replacer(m: "re.Match[str]") -> str:
            key = m.group(1).strip()
            val = evidence_bundle.get(key)
            if val is None:
                return m.group(0)  # leave unresolved tokens intact
            if isinstance(val, str):
                return val
            try:
                return json.dumps(val, ensure_ascii=False)
            except (TypeError, ValueError):
                return str(val)
        return re.sub(r"\{\{([^}]+)\}\}", replacer, template_text)

    @staticmethod
    def _inject_caveat(text: str, evidence_status: str) -> str:
        """Append a caveat note when evidence is weak."""
        note = (
            "\n\n[Caveat: Evidence for this section is partial. "
            f"Claims should be read with appropriate qualification. "
            f"Evidence status: {evidence_status}]"
        )
        return text + note

    def list_templates(self) -> list[str]:
        """Return list of registered template_ids."""
        self._ensure_loaded()
        return [e.get("template_id", "") for e in self._registry.get("templates", [])]
