"""Gate profile resolver — loads app gate profiles from declarative JSON/YAML.

W8 plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2

Generic core — no app-specific logic hardcoded here.
App profiles are injected via repo_root + profile_path.
Fails closed on missing or malformed profiles.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class GateProfileError(Exception):
    """Raised when a required gate profile is missing or malformed."""


@dataclass(frozen=False)
class GateProfile:
    """Resolved gate profile for one app + task_class."""

    profile_id: str = ""
    app_id: str = ""
    task_class: str = ""
    version: str = ""

    required_exit_gates: tuple[str, ...] = field(default_factory=tuple)
    conditional_exit_gates: tuple[str, ...] = field(default_factory=tuple)

    gate_definitions: dict[str, dict[str, Any]] = field(default_factory=dict)
    conditional_gate_triggers: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Runtime gate profile (G21-G28 details)
    runtime_gate_profile: dict[str, Any] = field(default_factory=dict)

    raw_exit_profile: dict[str, Any] = field(default_factory=dict)
    raw_runtime_profile: dict[str, Any] = field(default_factory=dict)


class GateProfileResolver:
    """Load and merge app gate profiles from disk.

    Profile paths are relative to repo_root.
    Fails closed (GateProfileError) on missing or malformed files.
    """

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    def resolve(
        self,
        exit_profile_path: str,
        runtime_gate_profile_path: str | None = None,
    ) -> GateProfile:
        """Load and merge profiles.

        Args:
            exit_profile_path: repo-relative path to exit_profile JSON.
            runtime_gate_profile_path: optional repo-relative path to
                runtime_gate_profile JSON (supplemental gate rules).

        Returns:
            Merged GateProfile with all gate definitions populated.

        Raises:
            GateProfileError: if any required file is missing or JSON-invalid.
        """
        exit_data = self._load_json(exit_profile_path)
        rt_data = self._load_json(runtime_gate_profile_path) if runtime_gate_profile_path else {}

        # Validate minimum required fields
        for key in ("required_exit_gates", "gate_definitions"):
            if key not in exit_data:
                raise GateProfileError(
                    f"Exit profile {exit_profile_path!r} missing required key {key!r}"
                )

        gate_defs: dict[str, dict[str, Any]] = dict(exit_data.get("gate_definitions", {}))

        # Merge supplemental runtime gate definitions
        for gid, gdef in rt_data.get("gate_rules", {}).items():
            if gid not in gate_defs:
                gate_defs[gid] = gdef
            else:
                # Runtime profile can add fields but exit profile wins on conflicts
                merged = {**gdef, **gate_defs[gid]}
                gate_defs[gid] = merged

        return GateProfile(
            profile_id=exit_data.get("exit_profile_id", ""),
            app_id=exit_data.get("app_id", ""),
            task_class=exit_data.get("task_class", ""),
            version=exit_data.get("version", ""),
            required_exit_gates=tuple(exit_data.get("required_exit_gates", [])),
            conditional_exit_gates=tuple(exit_data.get("conditional_exit_gates", [])),
            gate_definitions=gate_defs,
            conditional_gate_triggers=exit_data.get("conditional_gate_triggers", {}),
            runtime_gate_profile=rt_data,
            raw_exit_profile=exit_data,
            raw_runtime_profile=rt_data,
        )

    def _load_json(self, rel_path: str) -> dict[str, Any]:
        full = self._repo_root / rel_path
        if not full.exists():
            raise GateProfileError(
                f"Gate profile not found: {full} (relative: {rel_path!r})"
            )
        try:
            return json.loads(full.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise GateProfileError(
                f"Gate profile malformed JSON at {full}: {exc}"
            ) from exc
