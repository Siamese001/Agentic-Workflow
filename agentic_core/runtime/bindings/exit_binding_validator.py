"""Exit compatibility hooks for binding manifests (generic)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml

from agentic_core.runtime.bindings.binding_validation_types import ExitCompatValidationResult


def validate_manifest_exit_compatibility_policy(
    manifest: Mapping[str, Any],
    section_paths: Mapping[str, Any],
) -> list[str]:
    """Require absence reason when no Exit-shaped bundle section is supplied."""
    errs: list[str] = []
    bundle_path = section_paths.get("exit_compatibility_bundle")
    has_bundle = bundle_path is not None and getattr(bundle_path, "is_file", lambda: False)()
    if has_bundle:
        return errs
    reason = manifest.get("exit_compatibility_absence_reason")
    if not isinstance(reason, str) or not reason.strip():
        errs.append(
            "binding manifest requires exit_compatibility_absence_reason when exit_compatibility_bundle is absent",
        )
    return errs


def validate_exit_compat_bundle_generic(
    bundle_raw: Mapping[str, Any],
    *,
    repo_root: Path,
    contract_yaml_path: Path,
    policy_yaml_path: Path,
) -> ExitCompatValidationResult:
    """Structural smoke against generic exit-compat contract YAML."""
    _ = repo_root
    errs: list[str] = []
    if not contract_yaml_path.is_file():
        return ExitCompatValidationResult(status="FAIL", errors=["contract_yaml missing"])
    if not policy_yaml_path.is_file():
        return ExitCompatValidationResult(status="FAIL", errors=["policy_yaml missing"])
    try:
        contract = yaml.safe_load(contract_yaml_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return ExitCompatValidationResult(status="FAIL", errors=[f"contract parse error: {exc}"])

    required_keys: list[str] = []
    if isinstance(contract, dict):
        rk = contract.get("required_bundle_keys") or contract.get("required_root_keys")
        if isinstance(rk, list):
            required_keys = [str(x) for x in rk if str(x).strip()]

    if required_keys:
        for k in required_keys:
            if k not in bundle_raw:
                errs.append(f"exit compatibility bundle missing required key {k!r}")
    else:
        # Minimal generic posture: non-empty mapping.
        if not bundle_raw:
            errs.append("exit compatibility bundle empty")

    status = "FAIL" if errs else "PASS"
    return ExitCompatValidationResult(status=status, errors=errs, contract_path=contract_yaml_path)


__all__ = ["validate_exit_compat_bundle_generic", "validate_manifest_exit_compatibility_policy"]
