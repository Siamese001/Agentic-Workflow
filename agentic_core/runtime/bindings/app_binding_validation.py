"""Fail-closed validation for generic AppBindingPackage instances."""

from __future__ import annotations

import importlib.util
import json
import re

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from agentic_core.runtime.bindings.app_binding_package import AppBindingPackage
from agentic_core.runtime.bindings.binding_validation_types import SectionValidationDetail

StatusLiteral = Literal["PASS", "FAIL"]

# Generic section identifiers — no domain lane vocabulary.
REQUIRED_BINDING_SECTIONS: tuple[str, ...] = (
    "runtime_customization_package",
    "l1_static_plan_profile",
    "l0_managed_route_profile",
    "evidence_discipline",
    "pa_lane_refs",
)

BINDING_REPO_REL_PATH_FULLMATCH = re.compile(
    r"^(?:apps_[a-z0-9_]+|agentic_core)/(?:[A-Za-z0-9_.\-]+/)*[A-Za-z0-9_.\-]+\.(?:yaml|yml|json|py)$"
)

_FORBIDDEN_APPS_IMPORT = re.compile(
    r"(?:^\s*from\s+(apps_[a-zA-Z0-9_]+)\s+import\b|^\s*import\s+(apps_[a-zA-Z0-9_]+)\b)",
    re.MULTILINE,
)


@dataclass
class AppBindingValidationResult:
    """Structured outcome for binding validation."""

    status: StatusLiteral
    app_id: str
    package_root: Path
    required_sections_present: list[str] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)
    resolved_refs: list[str] = field(default_factory=list)
    missing_refs: list[str] = field(default_factory=list)
    forbidden_core_imports: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    section_results: list[SectionValidationDetail] = field(default_factory=list)


def _agentic_core_root() -> Path:
    spec = importlib.util.find_spec("agentic_core")
    if spec is None or not spec.origin:
        raise RuntimeError("cannot locate agentic_core package")
    return Path(spec.origin).resolve().parent


def scan_generic_bindings_tree_for_apps_imports() -> list[str]:
    """Scan **only** ``agentic_core/runtime/bindings`` for apps_* imports.

    Legacy adapters elsewhere under agentic_core may still import apps_*;
    W1 requires the new generic receptor subtree remain free of app imports.
    """
    bindings_root = _agentic_core_root() / "runtime" / "bindings"
    if not bindings_root.is_dir():
        return []

    violations: list[str] = []
    for path in sorted(bindings_root.rglob("*.py")):
        if path.name == "__pycache__":
            continue
        text = path.read_text(encoding="utf-8")
        for match in _FORBIDDEN_APPS_IMPORT.finditer(text):
            line_no = text[: match.start()].count("\n") + 1
            violations.append(f"{path.relative_to(bindings_root)}:{line_no}:{match.group(0).strip()}")
    return violations


def _has_apps_antigen_dir(root: Path) -> bool:
    """True when ``root`` contains at least one ``apps_*`` package directory."""
    try:
        for child in root.iterdir():
            if child.is_dir() and child.name.startswith("apps_"):
                return True
    except OSError:
        return False
    return False


def infer_repo_root(package_root: Path) -> Path | None:
    """Walk parents to find checkout root.

    ``tests/`` may contain nested ``tests/apps_*`` trees used by the suite — those
    MUST NOT be mistaken for the repository root. Require a sibling marker file
    (``pyproject.toml`` or ``pytest.ini``) alongside the primary ``agentic_core``
    package and at least one ``apps_*`` antigen directory.

    When ``package_root`` lives outside the checkout (common for pytest ``tmp_path``
    directories under the OS temp folder), fall back to the mono-repo layout:
    ``<repo>/agentic_core/__init__.py`` implies repo root is ``agentic_core``'s parent.
    """
    cur = package_root.resolve()
    for _ in range(16):
        core_pkg = cur / "agentic_core"
        marker = (cur / "pyproject.toml").is_file() or (cur / "pytest.ini").is_file()
        if core_pkg.is_dir() and marker and _has_apps_antigen_dir(cur):
            return cur
        parent = cur.parent
        if parent == cur:
            break
        cur = parent

    try:
        core_pkg_root = _agentic_core_root()
        candidate = core_pkg_root.parent
        marker = (candidate / "pyproject.toml").is_file() or (candidate / "pytest.ini").is_file()
        if _has_apps_antigen_dir(candidate) and marker:
            return candidate.resolve()
    except RuntimeError:  # guardian: allow-return-none-swallow -- P1 ADG burndown
        return None
    return None


def validate_app_binding_package(package: AppBindingPackage) -> AppBindingValidationResult:
    """Fail-closed validation for required sections, refs, profile shapes, and import hygiene."""
    errors: list[str] = []
    warnings: list[str] = []
    section_results: list[SectionValidationDetail] = []

    forbidden = scan_generic_bindings_tree_for_apps_imports()
    if forbidden:
        errors.append(
            "forbidden apps_* import(s) under agentic_core/runtime/bindings: "
            + "; ".join(forbidden)
        )

    present: list[str] = []
    missing_sections: list[str] = []
    section_paths = dict(package.section_paths)

    for key in REQUIRED_BINDING_SECTIONS:
        path = section_paths.get(key)
        if path is None:
            missing_sections.append(key)
            continue
        if path.is_file():
            present.append(key)
        else:
            missing_sections.append(key)
            errors.append(f"missing section file for {key!r}: {path}")

    resolved_refs_set: set[str] = set()
    missing_refs: list[str] = []

    repo_root = infer_repo_root(package.package_root)
    if repo_root is None:
        errors.append(
            "cannot infer repository root (need ancestor with agentic_core/, at least one apps_*/ "
            "package dir, and pytest.ini or pyproject.toml) "
            f"starting from {package.package_root}"
        )
    else:
        # Manifest-declared section paths are themselves refs for auditability.
        for key in REQUIRED_BINDING_SECTIONS:
            path = section_paths.get(key)
            if path is not None and path.is_file():
                try:
                    rel = path.resolve().relative_to(repo_root.resolve())
                    resolved_refs_set.add(rel.as_posix())
                except ValueError:
                    resolved_refs_set.add(path.resolve().as_posix())

    # W2/W3 manifest discipline + profile validators (requires repo root).
    if repo_root is not None:
        from agentic_core.runtime.bindings.exit_binding_validator import (
            validate_exit_compat_bundle_generic,
            validate_manifest_exit_compatibility_policy,
        )
        from agentic_core.runtime.bindings.profile_validators import run_profile_validators
        from agentic_core.runtime.bindings.ref_validators import (
            validate_extended_nested_refs,
            validate_optional_manifest_declarations,
        )

        errors.extend(validate_optional_manifest_declarations(package.manifest_document))
        errors.extend(validate_manifest_exit_compatibility_policy(package.manifest_document, section_paths))

        profile_sections = {k: section_paths[k] for k in REQUIRED_BINDING_SECTIONS if k in section_paths}
        section_results.extend(run_profile_validators(profile_sections, repo_root))

        ext = validate_extended_nested_refs(
            section_paths=section_paths,
            repo_root=repo_root,
            required_sections=REQUIRED_BINDING_SECTIONS,
        )
        section_results.append(ext)

        bundle_key = "exit_compatibility_bundle"
        if bundle_key in section_paths:
            bp = section_paths[bundle_key]
            if bp.is_file():
                bundle_raw: dict[str, Any] | None = None
                try:
                    raw_yaml = yaml.safe_load(bp.read_text(encoding="utf-8"))
                    bundle_raw = raw_yaml if isinstance(raw_yaml, dict) else None
                except (OSError, UnicodeDecodeError, yaml.YAMLError):
                    bundle_raw = None
                if bundle_raw is None:
                    try:
                        raw_json = json.loads(bp.read_text(encoding="utf-8"))
                        bundle_raw = raw_json if isinstance(raw_json, dict) else None
                    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
                        errors.append(f"cannot parse exit compatibility bundle {bp}: {exc}")
                if isinstance(bundle_raw, dict):
                    contracts = sorted(repo_root.glob("apps_*/runtime/binding/exit_compat_contract.binding_v1.yaml"))
                    contract_path = contracts[0] if contracts else None
                    policy_path = (
                        Path(__file__).resolve().parent / "generic_binding_validation_policy.binding_v1.yaml"
                    )
                    if contract_path is None or not contract_path.is_file():
                        errors.append(
                            "exit compatibility bundle present but exit_compat_contract.binding_v1.yaml "
                            "not found under apps_*/runtime/binding/"
                        )
                    else:
                        exit_res = validate_exit_compat_bundle_generic(
                            bundle_raw,
                            repo_root=repo_root,
                            contract_yaml_path=contract_path,
                            policy_yaml_path=policy_path,
                        )
                        if exit_res.status != "PASS":
                            errors.extend(exit_res.errors)

        for detail in section_results:
            if detail.missing_refs:
                missing_refs.extend(detail.missing_refs)
            resolved_refs_set.update(detail.resolved_refs)
            if detail.status != "PASS":
                errors.extend([f"{detail.section_name}: {e}" for e in detail.errors])

    status: StatusLiteral = "PASS"
    if errors or missing_sections or missing_refs or forbidden:
        status = "FAIL"

    return AppBindingValidationResult(
        status=status,
        app_id=package.app_id,
        package_root=package.package_root,
        required_sections_present=sorted(present),
        missing_sections=sorted(missing_sections),
        resolved_refs=sorted(resolved_refs_set),
        missing_refs=sorted(set(missing_refs)),
        forbidden_core_imports=list(forbidden),
        errors=errors,
        warnings=warnings,
        section_results=section_results,
    )
