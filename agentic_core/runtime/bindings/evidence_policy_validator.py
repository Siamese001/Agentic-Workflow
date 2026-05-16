"""Generic evidence discipline policy checks (W2)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from agentic_core.runtime.bindings.binding_validation_types import SectionValidationDetail


def validate_evidence_discipline_document(
    doc: Mapping[str, Any],
    *,
    repo_root: Path,
    policy_doc: Mapping[str, Any],
) -> SectionValidationDetail:
    """Validate canonical vs targeting-only posture without domain literals."""
    name = "evidence_discipline"
    errs: list[str] = []
    warns: list[str] = []
    resolved: list[str] = []
    missing: list[str] = []
    malformed: list[str] = []
    policy_lines: list[str] = []

    allow_roles = policy_doc.get("canonical_proof_roles_allowlist") or []
    if not isinstance(allow_roles, list) or not allow_roles:
        errs.append("policy missing canonical_proof_roles_allowlist")
        allow_set: set[str] = set()
    else:
        allow_set = {str(x) for x in allow_roles}

    tgt_policies = policy_doc.get("targeting_only_policy_values_allowlist") or []
    tgt_allow = {str(x) for x in tgt_policies} if isinstance(tgt_policies, list) else set()

    canon = doc.get("canonical_proof_evidence")
    prim_paths: list[str] = []
    if not isinstance(canon, Mapping):
        errs.append("canonical_proof_evidence mapping required")
    else:
        role = canon.get("role")
        if not isinstance(role, str) or not role.strip():
            errs.append("canonical_proof_evidence.role required")
        elif role.strip() not in allow_set:
            errs.append("canonical_proof_evidence.role not in allowlist (unsupported proof-source role)")
        policy_lines.append(f"canonical_role_ok={role in allow_set}")

        pp = canon.get("primary_paths")
        if isinstance(pp, list):
            prim_paths = [str(p).strip() for p in pp if isinstance(p, str) and p.strip()]
            for p in prim_paths:
                tgt = (repo_root / p).resolve()
                if tgt.is_file():
                    resolved.append(p)
                else:
                    missing.append(p)

        ptr = canon.get("active_pointer_ref")
        if isinstance(ptr, Mapping):
            pv = ptr.get("path")
            if isinstance(pv, str) and pv.strip():
                p = pv.strip()
                tgt = (repo_root / p).resolve()
                if tgt.is_file():
                    resolved.append(p)
                else:
                    missing.append(p)

    tgt_only = doc.get("targeting_context_only")
    if not isinstance(tgt_only, Mapping):
        errs.append("targeting_context_only mapping required")
    else:
        pol = tgt_only.get("policy")
        if not isinstance(pol, str) or not pol.strip():
            errs.append("targeting_context_only.policy required string")
        elif tgt_allow and pol.strip() not in tgt_allow:
            errs.append("targeting_context_only.policy not in allowlist")

        examples = tgt_only.get("examples_non_proof_paths")
        ex_paths: list[str] = []
        if isinstance(examples, list):
            ex_paths = [str(p).strip() for p in examples if isinstance(p, str) and p.strip()]
            for p in ex_paths:
                tgt = (repo_root / p).resolve()
                if tgt.is_file():
                    resolved.append(p)
                else:
                    missing.append(p)

        # Fail-closed: targeting-only paths cannot also be listed as canonical primary paths.
        overlap = set(prim_paths) & set(ex_paths)
        if overlap:
            errs.append(
                "targeting_only_paths_overlap_canonical_primary_paths:"
                + ",".join(sorted(overlap)[:12])
            )

    status = "FAIL" if errs or missing or malformed else "PASS"
    return SectionValidationDetail(
        section_name=name,
        status=status,
        errors=errs,
        warnings=warns,
        resolved_refs=sorted(set(resolved)),
        missing_refs=sorted(set(missing)),
        malformed_refs=malformed,
        hash_validation_results=[],
        policy_validation_results=policy_lines,
    )
