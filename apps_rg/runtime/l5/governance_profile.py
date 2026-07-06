"""apps_rg L5 governance profile loading and deterministic digesting."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml

REQUIRED_PROFILE_SECTIONS: tuple[str, ...] = (
    "safety_enforcement",
    "authority_context",
    "origin_trust",
    "hitl_posture",
    "provider_egress",
    "replay_audit",
    "static_governance",
    "runtime_certification",
)

DEFAULT_PROFILE_REL_PATH = "apps_rg/profiles/rg_l5_governance_profile.yaml"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode(
        "utf-8"
    )


def profile_digest_from_mapping(data: Mapping[str, Any]) -> str:
    """Return a deterministic sha256 digest over parsed canonical YAML content."""

    return hashlib.sha256(_canonical_json_bytes(dict(data))).hexdigest()


@dataclass(frozen=True, slots=True)
class AppsRgL5GovernanceProfile:
    """Loaded apps_rg L5 governance profile with section validation evidence."""

    path: Path
    data: Mapping[str, Any]
    profile_digest: str
    missing_sections: tuple[str, ...] = field(default_factory=tuple)

    @property
    def profile_ref(self) -> str:
        try:
            return self.path.relative_to(_repo_root()).as_posix()
        except ValueError:
            return self.path.as_posix()

    def section(self, name: str) -> Mapping[str, Any]:
        value = self.data.get(name)
        return value if isinstance(value, Mapping) else {}


def load_l5_governance_profile(
    path: str | Path | None = None,
    *,
    strict: bool = True,
) -> AppsRgL5GovernanceProfile:
    """Load and validate the apps_rg L5 governance profile.

    ``strict=False`` is used by packet construction to produce an explicit
    L5_NOT_CERTIFIED packet for incomplete profile evidence instead of raising
    before the packet can be materialized.
    """

    profile_path = Path(path) if path is not None else _repo_root() / DEFAULT_PROFILE_REL_PATH
    if not profile_path.is_absolute():
        profile_path = _repo_root() / profile_path
    raw = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, Mapping):
        raise ValueError(f"apps_rg L5 profile must parse to a mapping: {profile_path}")

    missing = tuple(section for section in REQUIRED_PROFILE_SECTIONS if section not in raw)
    if strict and missing:
        raise ValueError(
            "apps_rg L5 profile missing required section(s): "
            + ", ".join(missing)
        )

    return AppsRgL5GovernanceProfile(
        path=profile_path,
        data=dict(raw),
        profile_digest=profile_digest_from_mapping(raw),
        missing_sections=missing,
    )
