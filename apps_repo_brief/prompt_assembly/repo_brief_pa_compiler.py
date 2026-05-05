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

        # --- Compute hashes
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

        # Canonical slot bytes hash (structural — slot rendering is W3)
        canonical_slot_bytes = json.dumps(
            {
                "template_id": template_id,
                "required_slots": template.get("required_slots", []),
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

        # Full slot rendering is completed in W3 (repo_brief_pa_compiler full impl).
        # W2 scaffold emits structural artifact with hashes only.
        rendered_slots: dict[str, str] = {
            slot_id: f"[SLOT:{slot_id} — full rendering in W3]"
            for slot_id in template.get("required_slots", [])
        }

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
            # Slots
            "rendered_slots": rendered_slots,
            "canonical_slot_bytes_hash": canonical_slot_bytes_hash,
            "artifact_hash": artifact_hash,
            # Output constraints
            "provider_lane": "governed_gateway",
            "output_schema_ref": "governed_repo_brief_packet_v1",
            "audit_refs": [],
            # Scaffold flag — removed in W3 when full slot rendering lands
            "_scaffold_w2": True,
        }

        _log.debug(
            "CompiledPromptArtifact emitted: artifact_id=%s template=%s",
            artifact_id,
            template_id,
        )
        return artifact
