"""Nested reference closure validators — generic string-path scans."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping

import yaml

from agentic_core.runtime.bindings.binding_validation_types import SectionValidationDetail

_REPO_PATHLIKE = re.compile(
    r"^(?:apps_[a-z0-9_]+|agentic_core|tests|artifacts)/[^\s]+\.(?:yaml|yml|json|py)$",
)


def _walk_collect_repo_strings(obj: Any, acc: set[str]) -> None:
    if isinstance(obj, dict):
        for v in obj.values():
            _walk_collect_repo_strings(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _walk_collect_repo_strings(v, acc)
    elif isinstance(obj, str):
        s = obj.strip()
        if "<" in s or ">" in s:
            return
        if _REPO_PATHLIKE.fullmatch(s):
            acc.add(s)


def validate_optional_manifest_declarations(_manifest: Mapping[str, Any]) -> list[str]:
    """Optional manifest keys beyond core sections — stub PASS."""
    return []


def validate_extended_nested_refs(
    *,
    section_paths: Mapping[str, Path],
    repo_root: Path,
    required_sections: tuple[str, ...],
) -> SectionValidationDetail:
    """Ensure YAML closure of repo-relative paths declared under required sections."""
    errs: list[str] = []
    resolved: set[str] = set()
    missing: set[str] = set()

    for key in required_sections:
        path = section_paths.get(key)
        if path is None or not path.is_file():
            errs.append(f"missing section file for extended ref scan: {key}")
            continue
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
            errs.append(f"cannot parse YAML for {key}: {exc}")
            continue
        acc: set[str] = set()
        _walk_collect_repo_strings(doc, acc)
        for rel in sorted(acc):
            tgt = (repo_root / rel).resolve()
            if tgt.is_file():
                resolved.add(rel)
            else:
                missing.add(rel)

    if missing:
        errs.append("missing nested refs: " + ",".join(sorted(missing)[:24]))

    status = "FAIL" if errs else "PASS"
    return SectionValidationDetail(
        section_name="extended_nested_refs",
        status=status,
        errors=errs,
        resolved_refs=sorted(resolved),
        missing_refs=sorted(missing),
    )


__all__ = ["validate_extended_nested_refs", "validate_optional_manifest_declarations"]
