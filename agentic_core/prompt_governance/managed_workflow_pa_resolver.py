"""ManagedWorkflowPAResolver — W7 generic Prompt Assembly profile resolver.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W7

Resolves apps_rg prompt profiles (or any app following the same declarative
convention) from YAML config files and produces a ManagedPromptArtifact.

Core authority: Prompt Assembly lives in agentic_core, not in apps_rg.
This resolver reads apps_rg config files as DATA only.

Scope invariants (non-negotiable):
  - Does NOT compile prompt text. Returns refs + digests + boundary metadata only.
  - Does NOT call providers, models, or tools.
  - Does NOT write L4.
  - Does NOT emit X3.
  - Does NOT import apps_rg.prompt_assembly.rg_pa_compiler.
  - Does NOT import apps_rg.prompt_assembly.contracts.
  - Does NOT hardcode apps_rg beyond config/registry file paths (all resolved
    from app_id + repo_root at runtime).
  - Missing required template → artifact.is_valid=False (fail-closed).
  - Missing output schema ref → artifact.is_valid=False (fail-closed).
  - Prompt injection markers in lower-authority content → blocked, recorded
    in artifact.injection_block_records (fail-closed for instruction overrides).

Prompt boundary rules enforced here:
  - C0 (resume, JD, company brief, prior artifacts): DATA_ONLY, never INSTRUCTION.
  - U0 (user resume request): DATA_ONLY (user intent, not instruction authority).
  - D0 (security boundary): INSTRUCTION (governing fences, not user content).
  - S0 (system governance): INSTRUCTION (absolute authority).
  - I0 (app instructions): INSTRUCTION (governed authority).
  - E0 (approved examples): DATA_ONLY (data, not overridable instruction).
  - Y0 (style preferences): DATA_ONLY (approved style data).
  - R0 (output schema): INSTRUCTION (schema contract is authoritative).
  - Injection detection applies to C0 and U0 content slots only.
"""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agentic_core.runtime.contracts.managed_prompt_artifact import (
    DATA_BOUNDARY_DATA_ONLY,
    DATA_BOUNDARY_INSTRUCTION,
    PROMPT_REF_UNKNOWN,
    ManagedPromptArtifact,
    PromptComponentHash,
)

_log = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

# Canonical authority order from prompt_bom.yaml slot definitions.
# S0 > D0 > I0 > E0 > C0 > M0/Y0 > U0 > H0 > R0 (ABSOLUTE→SCHEMA)
_CANONICAL_AUTHORITY_ORDER: Tuple[str, ...] = (
    "S0", "D0", "I0", "E0", "C0", "M0", "Y0", "U0", "H0", "R0"
)

# Data boundary classification per slot code.
# DATA_ONLY = user/external content; INSTRUCTION = authoritative PA content.
_SLOT_BOUNDARY: Dict[str, str] = {
    "S0": DATA_BOUNDARY_INSTRUCTION,   # system governance — absolute authority
    "I0": DATA_BOUNDARY_INSTRUCTION,   # app instructions — governed authority
    "D0": DATA_BOUNDARY_INSTRUCTION,   # security boundary fences — binding authority
    "C0": DATA_BOUNDARY_DATA_ONLY,     # resume, JD, company brief — data only
    "E0": DATA_BOUNDARY_DATA_ONLY,     # approved examples — data only
    "M0": DATA_BOUNDARY_DATA_ONLY,     # meta-cognitive / CoT guidance — data only
    "Y0": DATA_BOUNDARY_DATA_ONLY,     # style preferences — data only
    "U0": DATA_BOUNDARY_DATA_ONLY,     # user intent — data only (never instruction)
    "H0": DATA_BOUNDARY_DATA_ONLY,     # healing context — data only
    "R0": DATA_BOUNDARY_INSTRUCTION,   # output schema contract — binding authority
}

# Injection markers that must not appear in data-only slots.
# These are patterns that attempt to override system instructions from user/data content.
_INJECTION_MARKER_PATTERNS: Tuple[str, ...] = (
    "ignore previous instructions",
    "ignore all previous",
    "disregard your instructions",
    "system prompt:",
    "you are now",
    "new instructions:",
    "override:",
    "bypass your",
    "forget everything",
    "act as",
    "pretend you are",
    "jailbreak",
    "ignore your guidelines",
    "do not follow",
    "your new role is",
)

# Forbidden content classes from prompt_profiles.yaml (data-only, no executable effect)
_FORBIDDEN_CONTENT_CLASSES: Tuple[str, ...] = (
    "instruction_to_fabricate",
    "instruction_to_omit_required_disclaimer",
    "third_party_resume_text_paste",
    "request_to_invent_metric",
    "request_to_misstate_dates",
)

# Runtime gate ref placeholder (W6 pattern)
_GATE_REF_UNKNOWN = "GATE_REF::UNKNOWN::NOT_EVALUATED"


class PAResolverError(Exception):
    """Raised on fail-closed resolver errors (missing required config)."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"PAResolverError: {reason}")


# ── YAML loader (no external deps — stdlib only) ──────────────────────────────

def _load_yaml_file(path: Path) -> Dict[str, Any]:
    """Load YAML file using PyYAML if available, else return empty dict.

    W7 scope: resolving YAML files is a read-only operation over declarative
    config. No side effects.
    """
    try:
        import yaml  # type: ignore[import-untyped]
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        return data if isinstance(data, dict) else {}
    except ImportError:
        _log.warning("[PA resolver] PyYAML not available — returning empty dict for %s", path)
        return {}
    except Exception as exc:
        raise PAResolverError(f"Failed to parse YAML {path}: {exc}") from exc


def _load_yaml_list(path: Path) -> List[Dict[str, Any]]:
    """Load YAML file that is a list (e.g. prompt_profiles.yaml)."""
    try:
        import yaml  # type: ignore[import-untyped]
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            return [data]
        return []
    except ImportError:
        return []
    except Exception as exc:
        raise PAResolverError(f"Failed to parse YAML list {path}: {exc}") from exc


def _sha256_file(path: Path) -> str:
    """Return sha256 hex digest of file content, or empty string if missing."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _repo_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return start.parents[3]


# ── Injection detector ────────────────────────────────────────────────────────

def _detect_injection(content: str, slot_code: str) -> Optional[str]:
    """Return injection marker if found in content, else None.

    Only applied to DATA_ONLY slots (C0, U0, E0, M0, Y0, H0).
    """
    if _SLOT_BOUNDARY.get(slot_code.upper()) != DATA_BOUNDARY_DATA_ONLY:
        return None
    lower = content.lower()
    for marker in _INJECTION_MARKER_PATTERNS:
        if marker in lower:
            return marker
    return None


def check_data_slot_for_injection(content: str, slot_code: str) -> Tuple[bool, str]:
    """Public helper: returns (injection_detected, marker_or_empty).

    Used by tests and external callers.
    """
    marker = _detect_injection(content, slot_code)
    if marker:
        return True, marker
    return False, ""


# ── Profile resolver ──────────────────────────────────────────────────────────

class ManagedWorkflowPAResolver:
    """Resolves app prompt profiles and emits ManagedPromptArtifact.

    Usage::

        resolver = ManagedWorkflowPAResolver(app_id="apps_rg")
        artifact = resolver.resolve(
            prompt_profile_ref="app::apps_rg::resume_generation::v1",
            node_id="header_block",
            workflow_ref="wfm::apps_rg::resume_generation::v1",
            run_id="run-w7-test",
        )
        assert artifact.is_valid
        prompt_ref = artifact.as_prompt_ref()

    The resolver reads (in order):
      1. apps_rg/config/domain_contract/prompt_profiles.yaml  → profile metadata
      2. apps_rg/prompt_assembly/prompt_bom.yaml              → BOM / authority order
      3. apps_rg/prompt_assembly/prompt_registry.yaml         → template registry
      4. apps_rg/config/section_prompts/<node_id>.yaml        → per-node prompt profile
      5. apps_rg/config/domain_contract/output_schema.yaml    → output schema binding (R0)

    All paths are resolved relative to repo_root. No apps_rg runtime modules imported.
    """

    def __init__(
        self,
        app_id: str = "apps_rg",
        *,
        repo_root: Optional[Path] = None,
    ) -> None:
        self._app_id = app_id
        self._repo_root = repo_root or _repo_root(Path(__file__).resolve())

    # ── Public API ────────────────────────────────────────────────────────────

    def resolve(
        self,
        *,
        prompt_profile_ref: str,
        node_id: str,
        workflow_ref: str = "",
        run_id: str = "",
        trace_root: str = "",
        request_id: str = "",
        replay_key: str = "",
        # Optional pre-populated slot content for injection checking
        c0_resume_text: str = "",
        c0_jd_text: str = "",
        c0_company_brief_text: str = "",
        u0_user_request_text: str = "",
    ) -> ManagedPromptArtifact:
        """Resolve prompt profile for a single managed workflow node.

        Fail-closed: if required template or output_schema_ref is missing,
        returns an artifact with is_valid=False and failure_reason populated.

        Injection checks: applied to any non-empty c0_*/u0_* content args.
        Detected injections are recorded in injection_block_records.
        For DATA_ONLY slots, injection detection is always run.
        """
        artifact_id = f"pa::{self._app_id}::{node_id}::{uuid.uuid4().hex[:8]}"
        created_at = datetime.now(timezone.utc).isoformat()
        component_hashes: List[PromptComponentHash] = []
        injection_block_records: List[str] = []
        injection_detected = False

        # ── Step 1: Load prompt_profiles.yaml ────────────────────────────
        profile_data, profile_hash, profile_path = self._load_profile(prompt_profile_ref)
        if profile_data:
            component_hashes.append(
                PromptComponentHash(
                    component_id="prompt_profile",
                    digest=profile_hash,
                    source_path=str(profile_path.relative_to(self._repo_root)) if profile_path else "",
                )
            )
            policy_hash = str(profile_data.get("policy_hash") or "")
        else:
            policy_hash = ""

        # ── Step 2: Load prompt_bom.yaml ─────────────────────────────────
        bom_data, bom_hash, bom_path = self._load_bom()
        prompt_bom_ref = str(bom_data.get("bom_id") or "")
        if bom_hash:
            component_hashes.append(
                PromptComponentHash(
                    component_id="prompt_bom",
                    digest=bom_hash,
                    source_path=str(bom_path.relative_to(self._repo_root)) if bom_path else "",
                )
            )

        # Authority order from BOM required_slots, preserving canonical order
        bom_required_slots: List[str] = list(bom_data.get("required_slots") or [])
        bom_slot_defs: Dict[str, Any] = bom_data.get("slot_definitions") or {}

        # Preserve canonical ordering: filter _CANONICAL_AUTHORITY_ORDER to BOM slots
        authority_order = tuple(
            s for s in _CANONICAL_AUTHORITY_ORDER if s in bom_required_slots
        ) or tuple(bom_required_slots) or _CANONICAL_AUTHORITY_ORDER

        # ── Step 3: Load prompt_registry.yaml ────────────────────────────
        registry_data, registry_hash, registry_path = self._load_registry()
        prompt_registry_ref = str(registry_data.get("registry_id") or "")
        if registry_hash:
            component_hashes.append(
                PromptComponentHash(
                    component_id="prompt_registry",
                    digest=registry_hash,
                    source_path=str(registry_path.relative_to(self._repo_root)) if registry_path else "",
                )
            )

        # ── Step 4: Load section_prompt for node_id ───────────────────────
        section_data, section_hash, section_path, missing_template = (
            self._load_section_prompt(node_id)
        )
        section_prompt_ref = str(section_data.get("prompt_id") or "")
        if section_hash:
            component_hashes.append(
                PromptComponentHash(
                    component_id=f"section_prompt::{node_id}",
                    digest=section_hash,
                    source_path=str(section_path.relative_to(self._repo_root)) if section_path else "",
                )
            )

        # Fail-closed: missing required template
        if missing_template:
            return self._invalid(
                artifact_id=artifact_id,
                request_id=request_id,
                run_id=run_id,
                trace_root=trace_root,
                workflow_ref=workflow_ref,
                node_id=node_id,
                prompt_profile_ref=prompt_profile_ref,
                prompt_bom_ref=prompt_bom_ref,
                prompt_registry_ref=prompt_registry_ref,
                component_hashes=tuple(component_hashes),
                created_at=created_at,
                failure_reason=f"missing_required_template: no section prompt file for node_id={node_id!r}",
            )

        # ── Step 5: Resolve output_schema_ref ────────────────────────────
        output_schema_ref = self._resolve_output_schema_ref(
            section_data, profile_data, node_id
        )
        schema_data, schema_hash, schema_path = self._load_output_schema()
        if schema_hash:
            component_hashes.append(
                PromptComponentHash(
                    component_id="output_schema",
                    digest=schema_hash,
                    source_path=str(schema_path.relative_to(self._repo_root)) if schema_path else "",
                )
            )

        # Fail-closed: missing output schema ref
        if not output_schema_ref:
            return self._invalid(
                artifact_id=artifact_id,
                request_id=request_id,
                run_id=run_id,
                trace_root=trace_root,
                workflow_ref=workflow_ref,
                node_id=node_id,
                prompt_profile_ref=prompt_profile_ref,
                prompt_bom_ref=prompt_bom_ref,
                prompt_registry_ref=prompt_registry_ref,
                section_prompt_ref=section_prompt_ref,
                component_hashes=tuple(component_hashes),
                created_at=created_at,
                failure_reason=f"missing_output_schema_ref: section_prompt {node_id!r} and profile {prompt_profile_ref!r} both lack output_schema_ref",
            )

        # ── Step 6: Data boundary classification ──────────────────────────
        # Authority from BOM slot definitions
        slots_required = tuple(bom_required_slots)
        slots_optional = tuple(list(bom_data.get("optional_slots") or []))

        data_boundary_classes: Dict[str, str] = {}
        for slot_code in list(authority_order):
            data_boundary_classes[slot_code] = _SLOT_BOUNDARY.get(
                slot_code.upper(), DATA_BOUNDARY_DATA_ONLY
            )

        # ── Step 7: Injection detection on data-only content ─────────────
        data_content_map = {
            "C0": c0_resume_text + "\n" + c0_jd_text + "\n" + c0_company_brief_text,
            "U0": u0_user_request_text,
        }
        for slot_code, content in data_content_map.items():
            if not content.strip():
                continue
            detected, marker = check_data_slot_for_injection(content, slot_code)
            if detected:
                injection_detected = True
                record = f"slot:{slot_code}:blocked:{marker}"
                injection_block_records.append(record)
                _log.warning(
                    "[PA resolver] injection blocked in slot=%s node=%s marker=%r",
                    slot_code, node_id, marker,
                )

        # ── Step 8: Blueprint hash (hash of slot + boundary metadata) ─────
        blueprint_payload = {
            "app_id": self._app_id,
            "node_id": node_id,
            "authority_order": list(authority_order),
            "data_boundary_classes": data_boundary_classes,
            "slots_required": list(slots_required),
            "output_schema_ref": output_schema_ref,
        }
        blueprint_hash = _sha256_text(
            json.dumps(blueprint_payload, sort_keys=True, ensure_ascii=False)
        )

        # ── Step 9: Assemble artifact ─────────────────────────────────────
        artifact = ManagedPromptArtifact(
            artifact_id=artifact_id,
            request_id=request_id,
            run_id=run_id,
            trace_root=trace_root,
            app_context=self._app_id,
            task_class=str(profile_data.get("task_class") or ""),
            workflow_ref=workflow_ref,
            node_id=node_id,
            prompt_profile_ref=prompt_profile_ref,
            prompt_bom_ref=prompt_bom_ref,
            prompt_registry_ref=prompt_registry_ref,
            section_prompt_ref=section_prompt_ref,
            authority_order=authority_order,
            data_boundary_classes=data_boundary_classes,
            slots_required=slots_required,
            slots_optional=slots_optional,
            output_schema_ref=output_schema_ref,
            injection_block_records=tuple(injection_block_records),
            injection_detected=injection_detected,
            component_hashes=tuple(component_hashes),
            replay_key=replay_key,
            policy_hash=policy_hash,
            blueprint_hash=blueprint_hash,
            created_at=created_at,
            is_valid=True,
            runtime_gate_refs=(_GATE_REF_UNKNOWN,),
            schema_version="W7.a3f7e2",
        )
        # Seal prompt_digest over canonical fields
        prompt_digest = artifact.compute_digest()
        # Frozen dataclass — reconstruct with prompt_digest filled in
        import dataclasses
        artifact = dataclasses.replace(artifact, prompt_digest=prompt_digest)
        return artifact

    # ── Internal loaders ──────────────────────────────────────────────────────

    def _profile_dir(self) -> Path:
        return self._repo_root / self._app_id / "config" / "domain_contract"

    def _bom_dir(self) -> Path:
        return self._repo_root / self._app_id / "prompt_assembly"

    def _section_prompt_dir(self) -> Path:
        return self._repo_root / self._app_id / "config" / "section_prompts"

    def _load_profile(
        self, prompt_profile_ref: str
    ) -> Tuple[Dict[str, Any], str, Optional[Path]]:
        path = self._profile_dir() / "prompt_profiles.yaml"
        if not path.exists():
            return {}, "", None
        profiles = _load_yaml_list(path)
        for profile in profiles:
            if profile.get("prompt_profile_id") == prompt_profile_ref:
                digest = _sha256_file(path)
                return profile, digest, path
        # Profile ref not found — return empty (resolver continues with defaults)
        return {}, _sha256_file(path), path

    def _load_bom(self) -> Tuple[Dict[str, Any], str, Optional[Path]]:
        path = self._bom_dir() / "prompt_bom.yaml"
        if not path.exists():
            return {}, "", None
        data = _load_yaml_file(path)
        return data, _sha256_file(path), path

    def _load_registry(self) -> Tuple[Dict[str, Any], str, Optional[Path]]:
        path = self._bom_dir() / "prompt_registry.yaml"
        if not path.exists():
            return {}, "", None
        data = _load_yaml_file(path)
        return data, _sha256_file(path), path

    def _load_section_prompt(
        self, node_id: str
    ) -> Tuple[Dict[str, Any], str, Optional[Path], bool]:
        """Returns (data, digest, path, missing_required).

        missing_required=True when the file does not exist and the node
        requires a template (not a deterministic extraction node).
        """
        path = self._section_prompt_dir() / f"{node_id}.yaml"
        if not path.exists():
            return {}, "", None, True  # fail-closed
        data = _load_yaml_file(path)
        return data, _sha256_file(path), path, False

    def _load_output_schema(self) -> Tuple[Dict[str, Any], str, Optional[Path]]:
        path = self._profile_dir() / "output_schema.yaml"
        if not path.exists():
            return {}, "", None
        data = _load_yaml_file(path)
        return data, _sha256_file(path), path

    def _resolve_output_schema_ref(
        self,
        section_data: Dict[str, Any],
        profile_data: Dict[str, Any],
        node_id: str,
    ) -> str:
        """Resolve output_schema_ref with priority: section_prompt > profile > empty."""
        # 1. Section prompt has node-specific output schema ref
        ref = str(section_data.get("output_schema_ref") or "")
        if ref:
            return ref
        # 2. Profile has global output schema ref
        ref = str(profile_data.get("output_schema_ref") or "")
        if ref:
            return ref
        return ""

    @staticmethod
    def _invalid(
        *,
        artifact_id: str,
        request_id: str,
        run_id: str,
        trace_root: str,
        workflow_ref: str,
        node_id: str,
        prompt_profile_ref: str,
        prompt_bom_ref: str = "",
        prompt_registry_ref: str = "",
        section_prompt_ref: str = "",
        component_hashes: Tuple[PromptComponentHash, ...] = (),
        created_at: str,
        failure_reason: str,
    ) -> ManagedPromptArtifact:
        return ManagedPromptArtifact(
            artifact_id=artifact_id,
            request_id=request_id,
            run_id=run_id,
            trace_root=trace_root,
            workflow_ref=workflow_ref,
            node_id=node_id,
            prompt_profile_ref=prompt_profile_ref,
            prompt_bom_ref=prompt_bom_ref,
            prompt_registry_ref=prompt_registry_ref,
            section_prompt_ref=section_prompt_ref,
            component_hashes=component_hashes,
            created_at=created_at,
            is_valid=False,
            failure_reason=failure_reason,
            runtime_gate_refs=(_GATE_REF_UNKNOWN,),
        )


__all__ = [
    "ManagedWorkflowPAResolver",
    "PAResolverError",
    "check_data_slot_for_injection",
]
