"""Structural validators for generic binding YAML sections (W2)."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Mapping

import yaml

from agentic_core.runtime.bindings.binding_validation_types import SectionValidationDetail
from agentic_core.runtime.bindings.evidence_policy_validator import validate_evidence_discipline_document

_POLICY_YAML = Path(__file__).resolve().parent / "generic_binding_validation_policy.binding_v1.yaml"

_REPO_PATHLIKE = re.compile(
    r"^(?:apps_[a-z0-9_]+|agentic_core|tests|artifacts)/[^\s]+\.(?:yaml|yml|json|py)$",
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _collect_repo_rel_paths(obj: Any, acc: set[str]) -> None:
    if isinstance(obj, dict):
        for v in obj.values():
            _collect_repo_rel_paths(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _collect_repo_rel_paths(v, acc)
    elif isinstance(obj, str):
        s = obj.strip()
        if _REPO_PATHLIKE.fullmatch(s):
            acc.add(s)


def _paths_exist(repo_root: Path, paths: Iterable[str], *, ctx: str) -> tuple[list[str], list[str]]:
    resolved: list[str] = []
    missing: list[str] = []
    for p in paths:
        tgt = (repo_root / p).resolve()
        if tgt.is_file():
            resolved.append(p)
        else:
            missing.append(f"{ctx}:{p}")
    return resolved, missing


def run_profile_validators(
    section_paths: Mapping[str, Path],
    repo_root: Path,
) -> list[SectionValidationDetail]:
    """Return per-section validation rows for the generic binding consumer."""
    policy_doc = yaml.safe_load(_POLICY_YAML.read_text(encoding="utf-8"))
    details: list[SectionValidationDetail] = []

    # --- runtime_customization_package ---
    rc_path = section_paths.get("runtime_customization_package")
    if rc_path is not None and rc_path.is_file():
        errs: list[str] = []
        doc = yaml.safe_load(rc_path.read_text(encoding="utf-8"))
        collected: set[str] = set()
        if isinstance(doc, dict):
            _collect_repo_rel_paths(doc.get("refs"), collected)
            _collect_repo_rel_paths(doc.get("profile_manifest"), collected)
        else:
            errs.append("runtime_customization_package must be a mapping")
        resolved, missing = _paths_exist(repo_root, sorted(collected), ctx="runtime_customization_package")
        details.append(
            SectionValidationDetail(
                section_name="runtime_customization_package",
                status="FAIL" if errs or missing else "PASS",
                errors=errs,
                resolved_refs=sorted(set(resolved)),
                missing_refs=sorted(set(missing)),
            ),
        )

    # --- l1_static_plan_profile ---
    l1_path = section_paths.get("l1_static_plan_profile")
    if l1_path is not None and l1_path.is_file():
        errs = []
        doc = yaml.safe_load(l1_path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            errs.append("l1_static_plan_profile must be a mapping")
        else:
            posture = doc.get("planning_posture")
            if not isinstance(posture, dict) or not str(posture.get("mode") or "").strip():
                errs.append("l1_static_plan_profile: planning_posture.mode required")
            hops = doc.get("plan_hops")
            if not isinstance(hops, list) or not hops:
                errs.append("l1_static_plan_profile: plan_hops required non-empty list")
            stable = doc.get("digest_stable_refs") or {}
            paths: list[str] = []
            if isinstance(stable, dict):
                v = stable.get("rg_planning_profile_ssot")
                if isinstance(v, str) and v.strip():
                    paths.append(v.strip())
            r, m = _paths_exist(repo_root, paths, ctx="l1_static_plan_profile.digest")
            errs.extend([f"missing digest ref {x}" for x in m])
            details.append(
                SectionValidationDetail(
                    section_name="l1_static_plan_profile",
                    status="FAIL" if errs else "PASS",
                    errors=errs,
                    resolved_refs=sorted(set(r)),
                    missing_refs=[],
                ),
            )

    # --- l0_managed_route_profile ---
    l0_path = section_paths.get("l0_managed_route_profile")
    if l0_path is not None and l0_path.is_file():
        errs = []
        doc = yaml.safe_load(l0_path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            errs.append("l0_managed_route_profile must be a mapping")
        else:
            auth = str(doc.get("route_profiles_authority_path") or "").strip()
            if not auth:
                errs.append("l0_managed_route_profile: route_profiles_authority_path required")
            else:
                if not (repo_root / auth).is_file():
                    errs.append(f"l0_managed_route_profile: authority file missing {auth}")
        details.append(
            SectionValidationDetail(
                section_name="l0_managed_route_profile",
                status="FAIL" if errs else "PASS",
                errors=errs,
                resolved_refs=[],
                missing_refs=[],
            ),
        )

    # --- evidence_discipline ---
    ev_path = section_paths.get("evidence_discipline")
    if ev_path is not None and ev_path.is_file():
        doc = yaml.safe_load(ev_path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            detail = SectionValidationDetail(
                section_name="evidence_discipline",
                status="FAIL",
                errors=["evidence_discipline must be a mapping"],
            )
        else:
            detail = validate_evidence_discipline_document(doc, repo_root=repo_root, policy_doc=policy_doc)
        details.append(detail)

    # --- pa_lane_refs (hash closure only; lane metadata is app-owned data) ---
    pa_path = section_paths.get("pa_lane_refs")
    if pa_path is not None and pa_path.is_file():
        errs = []
        warns: list[str] = []
        resolved: list[str] = []
        missing: list[str] = []
        doc = yaml.safe_load(pa_path.read_text(encoding="utf-8"))
        fh = doc.get("file_hashes") if isinstance(doc, dict) else None
        if isinstance(fh, dict):
            for rel, expected in fh.items():
                r = str(rel).strip()
                if not r:
                    continue
                exp = str(expected).strip().lower()
                tgt = (repo_root / r).resolve()
                if not tgt.is_file():
                    missing.append(r)
                    continue
                resolved.append(r)
                got = _sha256_file(tgt)
                if got != exp:
                    errs.append(f"hash mismatch for {r}: expected {exp} got {got}")
        else:
            errs.append("pa_lane_refs: file_hashes mapping required")
        details.append(
            SectionValidationDetail(
                section_name="pa_lane_refs",
                status="FAIL" if errs or missing else "PASS",
                errors=errs,
                warnings=warns,
                resolved_refs=sorted(set(resolved)),
                missing_refs=sorted(set(missing)),
            ),
        )

    return details


__all__ = ["run_profile_validators"]
