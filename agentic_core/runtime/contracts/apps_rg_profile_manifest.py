"""AppsRgProfileManifest — digest-bound manifest of declarative apps_rg profiles.

Path: agentic_core/runtime/contracts/apps_rg_profile_manifest.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass(frozen=True, slots=True)
class ProfileEntry:
    """Single profile entry within the manifest.

    Fields:
        profile_id: Canonical identifier for this profile (e.g., "standard_resume").
        source_path: Relative path under apps_rg/profiles/.
        content_digest: sha256 of the profile content for integrity verification.
    """
    profile_id: str
    source_path: str
    content_digest: str

    def __post_init__(self) -> None:
        if not self.profile_id or not isinstance(self.profile_id, str):
            raise ValueError("ProfileEntry.profile_id must be a non-empty string")
        if not self.source_path or not isinstance(self.source_path, str):
            raise ValueError("ProfileEntry.source_path must be a non-empty string")
        if self.source_path.startswith("/") or ".." in self.source_path:
            raise ValueError("ProfileEntry.source_path must be a relative path under profiles/")


@dataclass(frozen=True, slots=True)
class AppsRgProfileManifest:
    """Declarative profile manifest supplied by apps_rg.

    All fields are refs to declarative files (YAML/JSON) under apps_rg/profiles/.
    No runtime logic is embedded here. The manifest is digest-bound to prevent
    tampering between ingress and core consumption.
    """

    # Digest-bound integrity
    manifest_digest: str  # sha256 over canonical JSON of all profile contents

    # Core profile registry (profile_id -> ProfileEntry)
    profiles: Dict[str, ProfileEntry] = field(default_factory=dict)

    # Legacy explicit refs (for backwards compatibility during migration)
    planning_profile_ref: str = "rg_planning_profile.yaml"
    evidence_profile_ref: str = "rg_evidence_profile.yaml"
    prompt_profile_ref: str = "rg_prompt_profile.yaml"
    output_schema_ref: str = "rg_output_schema.json"
    style_profile_ref: str = "rg_style_profile.yaml"
    capability_profile_ref: str = "rg_capability_profile.yaml"

    # Binding provenance
    registry_binding_ref: str = "apps_rg"  # cert route registry entry
    policy_hash: str = ""  # hash of the authority policy version used
    blueprint_hash: str = ""  # hash of the task blueprint (e.g., resume_generation v2.1)

    def __post_init__(self) -> None:
        # All refs must be relative and under profiles/
        for attr in ("planning_profile_ref", "evidence_profile_ref", "prompt_profile_ref",
                     "output_schema_ref", "style_profile_ref", "capability_profile_ref"):
            val = getattr(self, attr)
            if not val or not isinstance(val, str):
                raise ValueError(f"AppsRgProfileManifest.{attr} must be a non-empty string")
            if val.startswith("/") or ".." in val:
                raise ValueError(f"AppsRgProfileManifest.{attr} must be a relative path under profiles/")

    def validate_all_present(self, required_ids: list[str]) -> bool:
        """Return True if all required profile_ids are present in the manifest."""
        return all(pid in self.profiles for pid in required_ids)
