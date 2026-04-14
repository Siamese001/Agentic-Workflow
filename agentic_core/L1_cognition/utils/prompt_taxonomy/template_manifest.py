"""
Template Manifest and Registry

TemplateManifest captures template metadata including version and required variables.
Registry maintains loaded templates with validation.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.L2_execution.reasoning import TemplateManifest as BaseTemplateManifest
from tqdm import tqdm


@dataclass
class ExtendedTemplateManifest:
    """
        Extended template manifest with taxonomy-specific fields.

        Inherits core fields from base TemplateManifest and adds
    category-specific metadata.
    """

    template_id: str
    version: str
    git_commit_hash: str
    required_variables: list[str]
    schema_version: str = "1.0"
    category: str = ""
    authority_slot: str = ""  # S0|I0|D0|C0|U0

    # Extended fields
    description: str = ""
    author: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    optional_variables: list[str] = field(default_factory=list)
    default_values: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def validate(self, provided_vars: dict[str, Any]) -> list[str]:
        """Validate that all required variables are provided."""
        missing = []
        for var in self.required_variables:
            if var not in provided_vars:
                missing.append(var)
        return missing

    def to_base(self) -> BaseTemplateManifest:
        """Convert to base TemplateManifest for runtime use."""
        return BaseTemplateManifest(
            template_id=self.template_id,
            version=self.version,
            git_commit_hash=self.git_commit_hash,
            required_variables=self.required_variables,
            schema_version=self.schema_version,
            category=self.category,
            authority_slot=self.authority_slot,
        )

    def compute_digest(self) -> str:
        """Compute content digest for integrity verification."""
        content = f"{self.template_id}:{self.version}:{self.git_commit_hash}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "template_id": self.template_id,
            "version": self.version,
            "git_commit_hash": self.git_commit_hash,
            "required_variables": self.required_variables,
            "schema_version": self.schema_version,
            "category": self.category,
            "authority_slot": self.authority_slot,
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "optional_variables": self.optional_variables,
            "default_values": self.default_values,
            "tags": self.tags,
            "digest": self.compute_digest(),
        }


class TemplateManifestRegistry:
    """
    Registry for template manifests.

    Provides lookup by template_id, category, or authority slot.
    """

    def __init__(self) -> None:
        self._manifests: dict[str, ExtendedTemplateManifest] = {}
        self._by_category: dict[str, list[str]] = {}
        self._by_slot: dict[str, list[str]] = {}

    def register(self, manifest: ExtendedTemplateManifest) -> None:
        """Register a template manifest."""
        self._manifests[manifest.template_id] = manifest

        # Index by category
        if manifest.category:
            if manifest.category not in self._by_category:
                self._by_category[manifest.category] = []
            if manifest.template_id not in self._by_category[manifest.category]:
                self._by_category[manifest.category].append(manifest.template_id)

        # Index by slot
        if manifest.authority_slot:
            slot = manifest.authority_slot.upper()
            if slot not in self._by_slot:
                self._by_slot[slot] = []
            if manifest.template_id not in self._by_slot[slot]:
                self._by_slot[slot].append(manifest.template_id)

    def get(self, template_id: str) -> ExtendedTemplateManifest | None:
        """Get manifest by template_id."""
        return self._manifests.get(template_id)

    def get_by_category(self, category: str) -> list[ExtendedTemplateManifest]:
        """Get all manifests for a category."""
        ids = self._by_category.get(category, [])
        return [self._manifests[i] for i in ids if i in self._manifests]

    def get_by_slot(self, slot_code: str) -> list[ExtendedTemplateManifest]:
        """Get all manifests for an authority slot."""
        slot_code = slot_code.upper()
        ids = self._by_slot.get(slot_code, [])
        return [self._manifests[i] for i in ids if i in self._manifests]

    def list_all(self) -> list[str]:
        """List all registered template IDs."""
        return list(self._manifests.keys())

    def is_registered(self, template_id: str) -> bool:
        """Check if template is registered."""
        return template_id in self._manifests

    def validate_all(self) -> dict[str, list[str]]:
        """Validate all registered manifests."""
        errors = {}
        for tid, manifest in tqdm(self._manifests.items(), desc="Processing", unit="item"):
            manifest_errors = []

            if not manifest.template_id:
                manifest_errors.append("Missing template_id")
            if not manifest.version:
                manifest_errors.append("Missing version")
            if not manifest.category and not manifest.authority_slot:
                manifest_errors.append("Missing both category and authority_slot")

            # Check for duplicate variable names
            dupes = set(manifest.required_variables) & set(manifest.optional_variables)
            if dupes:
                manifest_errors.append(f"Variables in both required and optional: {dupes}")

            if manifest_errors:
                errors[tid] = manifest_errors

        return errors
